__author__ = 'Tom Van den Eede'
__copyright__ = 'Copyright 2018-2021, Palette2 Splicer Post Processing Project'
__credits__ = ['Tom Van den Eede',
               'Tim Brookman'
               ]
__license__ = 'GPLv3'
__maintainer__ = 'Tom Van den Eede'
__email__ = 'P2PP@pandora.be'

import os
import time
import sys

import p2pp.gcode as gcode
import p2pp.gui as gui
import p2pp.pings as pings
import p2pp.purgetower as purgetower
import p2pp.variables as v
from p2pp.psconfig import parse_prusaslicer_config
from p2pp.omega import header_generate_omega, header_generate_omega_palette3
from p2pp.sidewipe import create_side_wipe
import p2pp.manualswap as swap
import p2pp.bedprojection as bp
import base64
import version
import zipfile

# GCODE BLOCK CLASSES
CLS_UNDEFINED = 0
CLS_NORMAL = 1
CLS_TOOL_START = 2
CLS_TOOL_UNLOAD = 4
CLS_TOOL_PURGE = 8
CLS_EMPTY = 16
CLS_BRIM = 32
CLS_BRIM_END = 64
CLS_ENDGRID = 128
CLS_COMMENT = 256
CLS_ENDPURGE = 512
CLS_TOOLCOMMAND = 1024

# HASH CODES FOR KEY COMMENTS
hash_FIRST_LAYER_BRIM_START = hash("WIPE TOWER FIRST LAYER BRIM START")
hash_FIRST_LAYER_BRIM_END = hash("WIPE TOWER FIRST LAYER BRIM END")
hash_EMPTY_GRID_START = hash("EMPTY GRID START")
hash_EMPTY_GRID_END = hash("EMPTY GRID END")
hash_TOOLCHANGE_START = hash("TOOLCHANGE START")
hash_TOOLCHANGE_UNLOAD = hash("TOOLCHANGE UNLOAD")
hash_TOOLCHANGE_LOAD = hash("TOOLCHANGE LOAD")
hash_TOOLCHANGE_WIPE = hash("TOOLCHANGE WIPE")
hash_TOOLCHANGE_END = hash("TOOLCHANGE END")


#  delta tower strategy: try to delay the delta as long as possible to minimize the extra print time


def optimize_tower_skip(max_layers):
    skippable = v.skippable_layer.count(True)

    idx = 0
    while skippable > max_layers:
        if v.skippable_layer[idx]:
            v.skippable_layer[idx] = False

            skippable -= 1
        idx += 1

    return skippable



def gcode_process_toolchange(new_tool):
    if new_tool == v.current_tool:
        return

    location = v.total_material_extruded + v.splice_offset

    if new_tool == -1:      # LAST SLICE PROCESSING
        location += v.extra_runout_filament
        v.material_extruded_per_color[v.current_tool] += v.extra_runout_filament
        v.total_material_extruded += v.extra_runout_filament
    else:
        v.palette_inputs_used[new_tool] = True

    length = location - v.previous_toolchange_location

    if v.current_tool != -1:  # FIRST SLICE PROCESSING

        v.splice_extruder_position.append(location)
        v.splice_length.append(length)
        v.splice_used_tool.append(v.current_tool)

        if len(v.splice_extruder_position) == 1:
            min_length = v.min_start_splice_length
            gui_format = "SHORT FIRST SPLICE (min {}mm) Length:{:-3.2f} Input {}"
        else:
            min_length = v.min_splice_length
            gui_format = "SHORT SPLICE (min {}mm) Length:{:-3.2f} Layer:{} Input:{}"

        if v.splice_length[-1] < min_length:
            if v.autoaddsplice and (v.full_purge_reduction or v.side_wipe):
                v.autoadded_purge = v.min_start_splice_length - length
                v.side_wipe_length += v.autoadded_purge
                v.splice_extruder_position[-1] += v.autoadded_purge * v.extrusion_multiplier
                v.splice_length[-1] += v.autoadded_purge
            else:
                gui.log_warning(gui_format.format(min_length, length, v.last_parsed_layer, v.current_tool + 1))
                v.filament_short[new_tool] = max(v.filament_short[new_tool],
                                                 v.min_start_splice_length - v.splice_length[-1])

        v.previous_toolchange_location = v.splice_extruder_position[-1]

    v.previous_tool = v.current_tool
    v.current_tool = new_tool


def calculate_temp_wait_position():

    pos_x = v.wipe_tower_info_minx + v.tx_offset * 1 if abs(v.wipe_tower_info_minx - v.purge_keep_x) < abs(v.wipe_tower_info_maxx - v.purge_keep_x) else -1
    pos_y = v.wipe_tower_info_miny + v.ty_offset * 1 if abs(v.wipe_tower_info_miny - v.purge_keep_y) < abs(v.wipe_tower_info_maxy - v.purge_keep_y) else -1
    return [pos_x, pos_y]


def entertower(layer_hght):

    purgeheight = layer_hght - v.cur_tower_z_delta

    if v.current_position_z != purgeheight:
        v.max_tower_delta = max(v.cur_tower_z_delta, v.max_tower_delta)
        gcode.issue_code(";------------------------------", True)
        gcode.issue_code(";  P2PP DELTA ENTER", True)
        gcode.issue_code(";  Current printing Z = {:.2f}".format(v.current_position_z), True)
        gcode.issue_code(";  Tower Z = {:.2f}".format(purgeheight), True)
        gcode.issue_code(";  Delta = {:.2f} ".format(v.current_position_z - purgeheight), True)
        gcode.issue_code(";------------------------------", True)

        if v.retraction >= 0:
            purgetower.retract(v.current_tool)

        if v.manual_filament_swap:
            swap.swap_pause("M25")
            # unpause z-move is not required

        gcode.issue_code("G1 X{} Y{} F8640".format(v.current_position_x, v.current_position_y))
        gcode.issue_code("G1 Z{:.2f} F10810".format(purgeheight))

        if purgeheight <= (v.first_layer_height+0.02):  # FIRST LAYER PURGES SLOWER
            gcode.issue_code("G1 F{}".format(min(1200, v.wipe_feedrate)))
        else:
            gcode.issue_code("G1 F{}".format(v.wipe_feedrate))

        v.disable_z = True


def update_class(line_hash):

    if line_hash == hash_EMPTY_GRID_START:
        v.block_classification = CLS_EMPTY
        v.layer_emptygrid_counter += 1

    elif line_hash == hash_EMPTY_GRID_END:
        v.block_classification = CLS_ENDGRID

    elif line_hash == hash_TOOLCHANGE_START:
        v.block_classification = CLS_TOOL_START
        v.layer_toolchange_counter += 1

    elif line_hash == hash_TOOLCHANGE_UNLOAD:
        v.block_classification = CLS_TOOL_UNLOAD

    elif line_hash == hash_TOOLCHANGE_LOAD:
        v.block_classification = CLS_TOOL_UNLOAD

    elif line_hash == hash_TOOLCHANGE_WIPE:
        v.block_classification = CLS_TOOL_PURGE

    elif line_hash == hash_TOOLCHANGE_END:
        v.block_classification = CLS_ENDPURGE

    elif line_hash == hash_FIRST_LAYER_BRIM_START:
        v.block_classification = CLS_BRIM
        v.tower_measure = True

    elif line_hash == hash_FIRST_LAYER_BRIM_END:
        v.block_classification = CLS_BRIM_END
        v.tower_measure = False
        v.wipe_tower_xsize = v.wipe_tower_info_maxx - v.wipe_tower_info_minx
        v.wipe_tower_ysize = v.wipe_tower_info_maxy - v.wipe_tower_info_miny


def process_layer(layer, index):
    if layer == v.last_parsed_layer:
        return
    v.last_parsed_layer = layer
    v.layer_end.append(index)
    if layer >= 0:
        v.skippable_layer.append((v.layer_emptygrid_counter > 0) and (v.layer_toolchange_counter == 0))

    v.layer_toolchange_counter = 0
    v.layer_emptygrid_counter = 0


def speed_limiter ( g_code ):
    if g_code[gcode.F] is not None and g_code[gcode.EXTRUDE] and g_code[gcode.F] > v.wipe_feedrate:
        g_code[gcode.COMMENT] = ";-- SLOW DOWN {} --> {}--;".format(g_code[gcode.F], v.wipe_feedrate)
        g_code[gcode.F] = v.wipe_feedrate


def parse_gcode():

    v.layer_toolchange_counter = 0
    v.layer_emptygrid_counter = 0

    v.block_classification = CLS_NORMAL
    v.previous_block_classification = CLS_NORMAL
    total_line_count = len(v.input_gcode)

    flh = int(v.first_layer_height * 100)
    olh = int(v.layer_height * 100)

    backpass_line = -1
    jndex = 0
    side_wipe_towerdefined = False

    for index in range(total_line_count):

        v.previous_block_classification = v.block_classification

        # memory management, reduce size of data structures when data is processed
        line = v.input_gcode[jndex]
        jndex += 1

        if jndex == 100000:
            gui.progress_string(4 + 46 * index // total_line_count)
            v.input_gcode = v.input_gcode[jndex:]
            jndex = 0

        # actual line processing
        if line.startswith(';'):

            is_comment = True

            # following lines should only be tested at the beginning og the file before the first layer is executed
            if not v.thumbnail_end:

                if line.startswith("; thumbnail end"):
                    v.thumbnail = False
                    v.thumbnail_end = True
                    v.thumbnail_data = v.thumbnail_data.replace("; ","")

                if v.thumbnail:
                    v.thumbnail_data += line


                if line.startswith("; thumbnail begin"):
                    v.thumbnail = True


            if line.startswith('; CP'):  # code block assignment
                update_class(hash(line[5:]))

            elif line.startswith(';LAYERHEIGHT'):  # Layer instructions
                fields = line.split(' ')
                try:
                    lv = float(fields[1])
                    lv = int((lv + 0.001) * 100) - flh
                    if lv % olh == 0:
                        process_layer(int(lv / olh), index)
                except (ValueError, IndexError):
                    pass

        else:
            is_comment = False
            try:
                if line[0] == 'T':
                    if v.set_tool == -1:
                        v.block_classification = CLS_NORMAL
                    else:
                        v.block_classification = CLS_TOOL_PURGE
                    cur_tool = int(line[1])
                    v.set_tool = cur_tool
            except (TypeError, IndexError, ValueError):
                pass

        code = gcode.create_command(line, is_comment, v.block_classification)
        v.parsed_gcode.append(code)

        if v.block_classification != v.previous_block_classification:

            if v.block_classification in [CLS_TOOL_START, CLS_TOOL_UNLOAD, CLS_EMPTY, CLS_BRIM]:
                for idx in range(backpass_line, len(v.parsed_gcode)):
                    v.parsed_gcode[idx][gcode.CLASS] = v.block_classification

        # determine tower size
        if v.tower_measure:
            if code[gcode.X]:
                v.wipe_tower_info_minx = min(v.wipe_tower_info_minx, code[gcode.X] - 2 * v.extrusion_width)
                v.wipe_tower_info_maxx = max(v.wipe_tower_info_maxx, code[gcode.X] + 2 * v.extrusion_width)
            if code[gcode.Y]:
                v.wipe_tower_info_miny = min(v.wipe_tower_info_miny, code[gcode.Y] - 4 * 2 * v.extrusion_width)
                v.wipe_tower_info_maxy = max(v.wipe_tower_info_maxy, code[gcode.Y] + 4 * 2 * v.extrusion_width)

        if v.bedtrace:
            if (code[gcode.MOVEMENT] & (gcode.X + gcode.Y)) and v.bed is not None:
                if code[gcode.EXTRUDE]:
                    v.bed.line(code[gcode.X], code[gcode.Y])
                else:
                    v.bed.position(code[gcode.X], code[gcode.Y])

        # determine block separators by looking at the last full XY positioning move
        if (code[gcode.MOVEMENT] & 3) == 3:
            if (code[gcode.MOVEMENT] & 12) == 0:
                backpass_line = len(v.parsed_gcode) - 1

            # add
            if side_wipe_towerdefined:
                if ((v.wipe_tower_info_minx <= code[gcode.X] <= v.wipe_tower_info_maxx) and
                   (v.wipe_tower_info_miny <= code[gcode.Y] <= v.wipe_tower_info_maxy)):
                    code[gcode.MOVEMENT] += gcode.INTOWER

            if v.block_classification in [CLS_ENDGRID, CLS_ENDPURGE]:
                if not (code[gcode.MOVEMENT] & gcode.INTOWER):
                    v.parsed_gcode[-1][gcode.CLASS] = CLS_NORMAL
                    v.block_classification = CLS_NORMAL

        if v.block_classification == CLS_BRIM_END:
            v.block_classification = CLS_NORMAL
            side_wipe_towerdefined = True

    v.input_gcode = []


def gcode_parselines():

    idx = 0
    purge = False
    total_line_count = len(v.parsed_gcode)
    v.retraction = 0
    v.last_parsed_layer = 0
    v.previous_block_classification = v.parsed_gcode[0][gcode.CLASS]

    for process_line_count in range(total_line_count):

        try:
            if process_line_count >= v.layer_end[0]:
                v.last_parsed_layer += 1
                v.layer_end.pop(0)
                v.current_layer_is_skippable = v.skippable_layer[v.last_parsed_layer]
                if v.current_layer_is_skippable:
                    if v.last_parsed_layer == 0:
                        v.cur_tower_z_delta += v.first_layer_height
                    else:
                        v.cur_tower_z_delta += v.layer_height
        except IndexError:
            pass

        g = v.parsed_gcode[idx]

        idx = idx + 1

        # ----- MEMORY MANAGEMENT - when 10K lines are processed, remove the top of the list

        if idx > 100000:
            v.parsed_gcode = v.parsed_gcode[idx:]
            idx = 0

        if process_line_count % 10000 == 0:
            gui.progress_string(50 + 50 * process_line_count // total_line_count)

        current_block_class = g[gcode.CLASS]

        # ---- FIRST SECTION HANDLES DELAYED TEMPERATURE COMMANDS ----

        if current_block_class not in [CLS_TOOL_PURGE, CLS_TOOL_START, CLS_TOOL_UNLOAD] and v.current_temp != v.new_temp:
            gcode.issue_code(v.temp1_stored_command)
            v.temp1_stored_command = ""

        # ---- SECOND SECTION HANDLES COMMENTS AND NONE-MOVEMENT COMMANDS ----

        if g[gcode.COMMAND] is None:
            if v.disable_z and g[gcode.COMMENT].endswith("END"):
                v.disable_z = False

            if v.needpurgetower and g[gcode.COMMENT].endswith("BRIM END"):
                v.needpurgetower = False
                purgetower.purge_create_layers(v.wipe_tower_info_minx, v.wipe_tower_info_miny, v.wipe_tower_xsize,
                                               v.wipe_tower_ysize)
                purgetower.purge_generate_brim()
                v.toolchange_processed = False
            gcode.issue_command(g)
            continue

        elif g[gcode.MOVEMENT] == 0:

            if g[gcode.COMMAND].startswith('T'):

                if v.manual_filament_swap and not (v.side_wipe or v.full_purge_reduction or v.tower_delta) and (v.current_tool != -1):
                    swap.swap_pause("M25")
                    swap.swap_unpause()

                gcode_process_toolchange(int(g[gcode.COMMAND][1:]))
                if not v.debug_leaveToolCommands:
                    gcode.move_to_comment(g, "--P2PP-- Color Change")
                    v.toolchange_processed = (current_block_class != CLS_NORMAL)

            elif v.klipper and g[gcode.COMMAND] == "ACTIVATE_EXTRUDER":
                extruder = g[gcode.OTHER]

                if extruder.startswith(" EXTRUDER=extruder"):

                    try:
                        extruder_num = int(extruder[18])
                    except ValueError:
                        extruder_num = None
                    except IndexError:
                        extruder_num = 0

                    if extruder_num is not None:
                        gcode_process_toolchange(extruder_num)

                    if not v.debug_leaveToolCommands:
                        gcode.move_to_comment(g, "--P2PP-- Color Change")
                        v.toolchange_processed = True
            else:
                if current_block_class == CLS_TOOL_UNLOAD:
                    if g[gcode.COMMAND] in ["G4", "M900"]:
                        gcode.move_to_comment(g, "--P2PP-- tool unload")

                if g[gcode.COMMAND] is not None and g[gcode.COMMAND].startswith('M'):
                    try:
                        commandNum = int(g[gcode.COMMAND][1:])
                    except (ValueError, KeyError):
                        commandNum = 0
                        pass

                    if commandNum in [104, 109]:
                        if v.process_temp:
                            if current_block_class not in [CLS_TOOL_PURGE, CLS_TOOL_START,
                                                           CLS_TOOL_UNLOAD]:
                                g[gcode.COMMENT] += " Unprocessed temp "
                                v.new_temp = gcode.get_parameter(g, gcode.S, v.current_temp)
                                v.current_temp = v.new_temp
                            else:
                                v.new_temp = gcode.get_parameter(g, gcode.S, v.current_temp)
                                if v.new_temp >= v.current_temp:
                                    g[gcode.COMMAND] = "M109"
                                    v.temp2_stored_command = gcode.create_commandstring(g)
                                    gcode.move_to_comment(g,
                                                          "--P2PP-- delayed temp rise until after purge {}-->{}".format(v.current_temp,
                                                                                                                        v.new_temp))
                                    v.current_temp = v.new_temp

                                else:
                                    v.temp1_stored_command = gcode.create_commandstring(g)
                                    gcode.move_to_comment(g,
                                                          "--P2PP-- delayed temp drop until after purge {}-->{}".format(v.current_temp,
                                                                                                                        v.new_temp))
                    elif commandNum == 107:
                        v.saved_fanspeed = 0

                    elif commandNum == 106:
                        v.saved_fanspeed = gcode.get_parameter(g, gcode.S, v.saved_fanspeed)

                    elif commandNum == 221:
                        v.extrusion_multiplier = float(gcode.get_parameter(g, gcode.S, v.extrusion_multiplier * 100.0)) / 100.0

                    elif commandNum == 220:
                        gcode.move_to_comment(g, "--P2PP-- Feed Rate Adjustments are removed")

                    elif commandNum == 572:
                        for i in range(1, v.filament_count):
                            g[gcode.OTHER] = g[gcode.OTHER].replace("D{}".format(i), "D0")

                    elif not v.generate_M0 and g[gcode.COMMAND] == "M0":
                        gcode.move_to_comment(g, "--P2PP-- remove M0 command")

            gcode.issue_command(g)
            continue

        # ---- AS OF HERE ONLY MOVEMENT COMMANDS ----

        classupdate = current_block_class != v.previous_block_classification
        v.previous_block_classification = current_block_class

        if g[gcode.MOVEMENT] & 1:
            v.previous_purge_keep_x = v.purge_keep_x
            v.purge_keep_x = g[gcode.X]
            v.current_position_x = g[gcode.X]

        if g[gcode.MOVEMENT] & 2:
            v.previous_purge_keep_y = v.purge_keep_y
            v.purge_keep_y = g[gcode.Y]
            v.current_position_y = g[gcode.Y]

        if g[gcode.MOVEMENT] & 4:
            if v.disable_z:
                gcode.move_to_comment(g, "-- P2PP - invalid move in delta tower")
                gcode.issue_command(g)
                continue
            else:
                v.current_position_z = g[gcode.Z]

        if g[gcode.MOVEMENT] & 16:
            v.keep_speed = g[gcode.F]

        # this goes for all situations: START and UNLOAD are not needed
        if current_block_class in [CLS_TOOL_START, CLS_TOOL_UNLOAD]:
            gcode.move_to_comment(g, "--P2PP-- tool unload")
            gcode.issue_command(g)
            continue

        # --------------------- TOWER DELTA PROCESSING
        if v.tower_delta:

            if classupdate:

                if current_block_class == CLS_TOOL_PURGE:
                    gcode.issue_command(g)
                    entertower(v.last_parsed_layer * v.layer_height + v.first_layer_height)
                    continue

                if current_block_class == CLS_EMPTY and not v.towerskipped:
                    v.towerskipped = (g[gcode.MOVEMENT] & gcode.INTOWER) == gcode.INTOWER and v.current_layer_is_skippable

                    if not v.towerskipped:
                        gcode.issue_command(g)
                        entertower(v.last_parsed_layer * v.layer_height + v.first_layer_height)
                        continue

                if current_block_class == CLS_NORMAL:
                    if v.towerskipped:
                        gcode.issue_code("G1 Z{:.2f} F10810".format(v.current_position_z))
                        v.towerskipped = False

            if current_block_class == CLS_TOOL_PURGE:
                speed_limiter(g)

            if current_block_class == CLS_TOOL_PURGE:
                if g[gcode.F] is not None and g[gcode.F] > v.purgetopspeed and g[gcode.E]:
                    g[gcode.F] = v.purgetopspeed
                    g[gcode.COMMENT] += " prugespeed topped"

            if v.towerskipped:
                gcode.move_to_comment(g, "--P2PP-- tower skipped")
                gcode.issue_command(g)
                continue
        # --------------------- SIDE WIPE PROCESSING
        elif v.side_wipe:

            if classupdate:

                if current_block_class == CLS_BRIM:
                    if v.bigbrain3d_purge_enabled:
                        create_side_wipe(v.bigbrain3d_prime * v.bigbrain3d_blob_size)
                    v.towerskipped = True
                    v.side_wipe_state = 0

            if not v.towerskipped and (g[gcode.MOVEMENT] & 3) == 3:
                if (g[gcode.MOVEMENT] & gcode.INTOWER) == gcode.INTOWER:
                    v.towerskipped = True
                    v.side_wipe_state = 1 if (current_block_class == CLS_TOOL_PURGE) else 0

            if v.towerskipped and current_block_class == CLS_NORMAL and (g[gcode.MOVEMENT] & 3) == 3:
                if (v.bed_origin_x <= g[gcode.X] <= v.bed_max_x) and (v.bed_origin_y <= g[gcode.Y] <= v.bed_max_y):
                    v.towerskipped = False
                    v.side_wipe_state = 0
                    if v.toolchange_processed and v.side_wipe_length:
                        create_side_wipe()
                        v.toolchange_processed = False

            if v.towerskipped:
                inc = "NO_E"
                if current_block_class in [CLS_TOOL_PURGE, CLS_ENDPURGE] or (current_block_class == CLS_EMPTY and v.side_wipe_state == 1):
                    if g[gcode.EXTRUDE]:
                        v.side_wipe_length += g[gcode.E]
                        inc = "INC_E"

                gcode.move_to_comment(g, "--P2PP-- side wipe skipped ({})".format(inc))
                gcode.issue_command(g)
                continue

        # --------------------- FULL PURGE PROCESSING
        elif v.full_purge_reduction:

            if classupdate:

                if current_block_class == CLS_NORMAL:
                    v.towerskipped = False
                    purge = False

                if current_block_class == CLS_TOOL_PURGE:
                    purge = True

            if not v.towerskipped and current_block_class == CLS_EMPTY and v.current_layer_is_skippable:
                v.towerskipped = (g[gcode.MOVEMENT] & gcode.INTOWER) == gcode.INTOWER

            if v.towerskipped or current_block_class in [CLS_BRIM, CLS_ENDGRID, CLS_EMPTY]:
                gcode.move_to_comment(g, "--P2PP-- full purge skipped")
                gcode.issue_command(g)
                continue

            if current_block_class in [CLS_TOOL_PURGE, CLS_ENDPURGE, CLS_EMPTY]:
                if purge:
                    if g[gcode.EXTRUDE]:
                        v.side_wipe_length += g[gcode.E]
                    gcode.move_to_comment(g, "--P2PP-- full purge skipped ")
                gcode.issue_command(g)
                continue

            if v.toolchange_processed and current_block_class == CLS_NORMAL:
                if v.side_wipe_length and (g[gcode.MOVEMENT] & 3) == 3 and not (g[gcode.MOVEMENT] & gcode.INTOWER) == gcode.INTOWER:
                    purgetower.purge_generate_sequence()
                    v.toolchange_processed = False
                    # do not issue code here as the next code might require further processing such as retractioncorrection
                else:
                    gcode.move_to_comment(g, "--P2PP-- full purge skipped")
                    gcode.issue_command(g)
                    continue

            if v.expect_retract and (g[gcode.MOVEMENT] & 3):
                v.expect_retract = False
                if v.retraction >= 0 and g[gcode.RETRACT]:
                    purgetower.retract(v.current_tool)

            if v.retract_move and g[gcode.RETRACT]:
                g[gcode.X] = v.retract_x
                g[gcode.Y] = v.retract_y
                g[gcode.MOVEMENT] |= 3
                v.retract_move = False

                if v.retraction <= - v.retract_length[v.current_tool]:
                    gcode.move_to_comment(g, "--P2PP-- Double Retract")
                else:
                    v.retraction += g[gcode.E]

        # --------------------- NO TOWER PROCESSING
        else:

            if classupdate:

                if current_block_class in [CLS_TOOL_PURGE, CLS_EMPTY]:
                    if v.acc_ping_left <= 0:
                        pings.check_accessorymode_first()
                    v.enterpurge = True

            # TOEE - Added to limit the speed of the extrusions during purge to defined WIPEFEEDRATE
            if current_block_class == CLS_TOOL_PURGE:
                speed_limiter(g)

            if v.toolchange_processed:

                if v.temp2_stored_command != "":
                    wait_location = calculate_temp_wait_position()
                    gcode.issue_code(
                        "G1 X{:.3f} Y{:.3f} F8640; temp wait position\n".format(wait_location[0], wait_location[0]))
                    gcode.issue_code(v.temp2_stored_command)
                    v.temp2_stored_command = ""

                gcode.issue_code("G1 F8640 ; correct speed")
                gcode.issue_command(g)
                gcode.issue_code("G1 Z{} F10800 ;P2PP correct z-moves".format(v.current_position_z))

                v.toolchange_processed = False
                continue

            if current_block_class == CLS_TOOL_PURGE:
                if g[gcode.F] is not None and g[gcode.F] > v.purgetopspeed and g[gcode.E]:
                    g[gcode.F] = v.purgetopspeed
                    g[gcode.COMMENT] += " prugespeed topped"

        # --------------------- GLOBAL PROCEDDING

        if g[gcode.UNRETRACT]:
            g[gcode.E] = min(-v.retraction, g[gcode.E])
            v.retraction += g[gcode.E]
        elif g[gcode.RETRACT]:
            v.retraction += g[gcode.E]
        elif (g[gcode.MOVEMENT] & 3) and g[gcode.EXTRUDE] and v.retraction < -0.01:
            purgetower.unretract(v.current_tool, -1, ";--- P2PP --- fixup retracts")





        # --------------------- PING PROCESSING

        if v.accessory_mode and g[gcode.EXTRUDE]:
            if not pings.check_accessorymode_second(g[gcode.E]):
                gcode.issue_command(g)
        else:
            gcode.issue_command(g)
            if g[gcode.EXTRUDE] and v.side_wipe_length == 0:
                pings.check_connected_ping()

        v.previous_position_x = v.current_position_x
        v.previous_position_y = v.current_position_y

    # LAST STEP IS ADDING AN EXTRA TOOL UNLOAD TO DETERMINE THE LENGTH OF THE LAST SPLICE
    gcode_process_toolchange(-1)

# -- MAIN ROUTINE --- GLUES ALL THE PROCESSING ROUTINED
# -- FILE READING / FIRST PASS / SECOND PASS / FILE WRITING


def generate(input_file, output_file):

    starttime = time.time()
    basename = os.path.basename(input_file)
    _taskName = os.path.splitext(basename)[0].replace(" ", "_")
    _taskName = _taskName.replace(".mcf", "")
    gui.setfilename(input_file)
    gui.app.sync()
    try:
        # python 3.x
        # noinspection PyArgumentList
        opf = open(input_file, encoding='utf-8')
    except TypeError:
        try:
            # python 2.x
            opf = open(input_file)
        except IOError:
            gui.log_warning("Error Reading:'{}'".format(input_file))
            return
    except IOError:
        gui.log_warning("Error Reading: '{}'".format(input_file))
        return

    gui.create_logitem("Reading File " + input_file)
    gui.progress_string(1)
    v.input_gcode = opf.readlines()
    opf.close()

    v.input_gcode = [item.strip() for item in v.input_gcode]

    gui.create_logitem("Analyzing Prusa Slicer Configuration")
    gui.progress_string(2)
    parse_prusaslicer_config()

    if v.save_unprocessed:
        pre, ext = os.path.splitext(input_file)
        of = pre + "_unprocessed" + ext
        gui.create_logitem("Saving unpocessed code to: " + of)
        opf = open(of, "wb")
        for line in v.input_gcode:
            opf.write(line.encode('utf8'))
            opf.write("\n".encode('utf8'))
        opf.close()

    # added for issue Error: float division by zero (#87)
    if v.extrusion_width == 0:
        gui.create_logitem("Extrusionwidth set to 0, defaulted back to 0.45")
        v.extrusion_width = 0.45

    # v.bed = bp.BedProjection(int(v.bed_size_x), int(v.bed_size_y))
    gui.create_logitem("Analyzing Layers / Functional blocks")
    gui.progress_string(4)
    parse_gcode()
    # if v.bedtrace:
    #     v.bed.save_image()
    v.input_gcode = None

    if v.bed_size_x == -9999 or v.bed_size_y == -9999 or v.bed_origin_x == -9999 or v.bed_origin_y == -9999:
        gui.log_warning("Bedsize nor or incorrectly defined.")
    else:
        if v.bed_shape_rect and v.bed_shape_warning:
            gui.create_logitem("Manual bed size override, PrusaSlicer Bedshape configuration ignored.")
        gui.create_logitem("Bed origin ({:3.1f}mm, {:3.1f}mm)".format(v.bed_origin_x, v.bed_origin_y))
        gui.create_logitem("Bed size   ({:3.1f}mm, {:3.1f}mm)".format(v.bed_size_x, v.bed_size_y))

    v.bed_max_x = v.bed_origin_x + v.bed_size_x
    v.bed_max_y = v.bed_origin_y + v.bed_size_y

    if v.process_temp and v.side_wipe:
        gui.log_warning("TEMPERATURECONTROL and SIDEWIPE / BigBrain3D are incompatible")

    if v.palette_plus:
        if v.palette_plus_ppm == -9:
            gui.log_warning("P+ parameter P+PPM incorrectly set up in startup GCODE")
        if v.palette_plus_loading_offset == -9:
            gui.log_warning("P+ parameter P+LOADINGOFFSET incorrectly set up in startup GCODE")

    v.side_wipe = not ((v.bed_origin_x <= v.wipetower_posx <= v.bed_max_x) and (v.bed_origin_y <= v.wipetower_posy <= v.bed_max_y))
    v.tower_delta = v.max_tower_z_delta > 0

    if (v.tower_delta or v.full_purge_reduction) and v.variable_layer:
        gui.log_warning("Variable layers may cause issues with FULLPURGE / TOWER DELTA")
        gui.log_warning("This warning could be caused by support that will print on variable layer offsets")

    if v.side_wipe:

        if v.skirts:
            if v.ps_version >= "2.2":
                gui.log_warning("SIDEWIPE and SKIRTS are NOT compatible in PS2.2 or later")
            if v.full_purge_reduction:
                gui.log_warning("FULLPURGE and SKIRTS are NOT compatible.  Overlaps may occur")

        if v.wipe_remove_sparse_layers:
            gui.log_warning("SIDE WIPE mode not compatible with sparse wipe tower in PS")
            gui.log_warning("Use Tower Delta instead")

        gui.create_logitem("Side wipe activated", "blue")

        if v.full_purge_reduction:
            gui.log_warning("FULLURGEREDUCTION is incompatible with SIDEWIPE, parameter ignored")
            v.full_purge_reduction = False

    if v.full_purge_reduction:

        if v.tower_delta:
            gui.log_warning("FULLPURGEREDUCTION is incompatible with TOWERDELTA")
            v.tower_delta = False
        gui.create_logitem("FULLPURGEREDUCTION activated", "blue")

    if v.autoaddsplice and not v.full_purge_reduction and not v.side_wipe:
        gui.log_warning("AUTOADDPURGE only works with SIDEWIPE and FULLPURGEREDUCTION")

    if len(v.skippable_layer) == 0:
        gui.log_warning("LAYER configuration is missing.")
        gui.close_button_enable()
        sys.exit(-1)
    else:
        skippable = optimize_tower_skip(int(v.max_tower_z_delta / v.layer_height))
        if v.tower_delta:
            v.skippable_layer[0] = False
            if skippable > 0:
                gui.log_warning("TOWERDELTA in effect for {} Layers or {:.2f}mm".format(skippable, skippable * v.layer_height))
            else:
                gui.create_logitem("TOWERDELTA could not be applied to this print")

        gui.create_logitem("Generate processed GCode")
        gcode_parselines()
        v.processtime = time.time() - starttime
        omega_result = header_generate_omega(_taskName)
        header = omega_result['header'] + omega_result['summary'] + omega_result['warnings']

        # write the output file
        ######################

        if output_file is None:
            output_file = input_file

        path, _ = os.path.split(output_file)

        if v.palette3:
            output_file = os.path.join(path, "print.gcode")
            pre, ext = os.path.splitext(input_file)
            mcfx = pre + ".mcfx"

        gui.create_logitem("Generating GCODE file: " + output_file)
        opf = open(output_file, "wb")
        if not v.accessory_mode and not v.palette3:
            for line in header:
                opf.write(line.encode('utf8'))
            opf.write(("\n\n;--------- THIS CODE HAS BEEN PROCESSED BY P2PP v{} --- \n\n".format(version.Version)).encode('utf8'))
            if v.generate_M0:
                header.append("M0\n")
            opf.write("T0\n".encode('utf8'))
        else:
            opf.write(("\n\n;--------- THIS CODE HAS BEEN PROCESSED BY P2PP v{} --- \n\n".format(version.Version)).encode('utf8'))


        if v.splice_offset == 0:
            gui.log_warning("SPLICE_OFFSET not defined")
        for line in v.processed_gcode:
            try:
                opf.write(line.encode('utf8'))
            except IOError:
                gui.log_warning("Line : {} could not be written to output".format(line))
            opf.write("\n".encode('utf8'))
        opf.close()

        if v.palette3:

            # generate meta.json
            # generate palette.json
            # generate thumbnail
            # generate zip
            meta, palette = header_generate_omega_palette3(None)

            meta_file = os.path.join(path , "meta.json")
            palette_file = os.path.join(path , "palette.json")
            im_file = os.path.join(path, "thumbnail.png")

            gui.create_logitem("Generating Palette 3 output files")
            mf = open(meta_file, 'wb')
            mf.write(meta.__str__().encode('ascii'))
            mf.close()

            pa = open(palette_file, 'wb')
            pa.write(palette.__str__().encode('ascii'))
            pa.close()

            im = open(im_file, "wb")
            im.write(base64.b64decode(v.thumbnail_data))
            im.close()

            zipf = zipfile.ZipFile(mcfx, 'w', zipfile.ZIP_DEFLATED)
            zipf.write(meta_file , "meta.json")
            zipf.write(palette_file, "palette.json")
            zipf.write(output_file, "print.gcode")
            zipf.write(im_file, "thumbnail.png")

            os.remove(meta_file)
            os.remove(palette_file)
            os.remove(output_file)
            os.remove(im_file)
            zipf.close()



        if v.accessory_mode:

            pre, ext = os.path.splitext(output_file)
            if v.palette_plus:
                maffile = pre + ".msf"
            else:
                maffile = pre + ".maf"
            gui.create_logitem("Generating PALETTE MAF/MSF file: " + maffile)

            maf = open(maffile, 'wb')

            for h in header:
                h = str(h).strip("\r\n")
                maf.write(h.encode('ascii'))
                maf.write("\r\n".encode('ascii'))

            maf.close()

        gui.print_summary(omega_result['summary'])

    gui.progress_string(101)
    if (len(v.process_warnings) > 0 and not v.ignore_warnings) or v.consolewait:
        gui.close_button_enable()
