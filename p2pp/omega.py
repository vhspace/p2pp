__author__ = 'Tom Van den Eede'
__copyright__ = 'Copyright 2018-2021, Palette2 Splicer Post Processing Project'
__credits__ = ['Tom Van den Eede',
               'Tim Brookman'
               ]
__license__ = 'GPLv3'
__maintainer__ = 'Tom Van den Eede'
__email__ = 'P2PP@pandora.be'

import p2pp.gui as gui
import p2pp.variables as v
from p2pp.colornames import find_nearest_colour
from p2pp.formatnumbers import hexify_short, hexify_float, hexify_long, hexify_byte
import json
import p2pp.purgetower as purgetower


# ################################################################
# ######################### ALGORITHM PROCESSING ################
# ################################################################
def algorithm_create_process_string(heating, compression, cooling):
    if v.palette_plus:
        if int(cooling) != 0:  # cooling parameter functions as a forward/reverse
            cooling = 1
        return "{},{},{}".format(hexify_float(float(heating))[1:].zfill(8),
                                 hexify_float(float(compression))[1:].zfill(8),
                                 cooling
                                 )
    elif v.palette3:
        return int(heating), int(compression), int(cooling)

    else:
        return "{} {} {}".format(hexify_short(int(heating)),
                                 hexify_short(int(compression)),
                                 hexify_short(int(cooling))
                                 )


def algorithm_process_material_configuration(splice_info):
    fields = splice_info.split("_")
    if fields[0] == "DEFAULT" and len(fields) == 4:
        v.default_splice_algorithm = algorithm_create_process_string(fields[1],
                                                                     fields[2],
                                                                     fields[3])

    if len(fields) == 5:
        key = "{}{}".format(fields[0],
                            fields[1])
        v.splice_algorithm_dictionary[key] = algorithm_create_process_string(fields[2],
                                                                             fields[3],
                                                                             fields[4])


def algorithm_transition_used(from_input, to_input):
    if len(v.splice_used_tool) > 0:
        for idx in range(len(v.splice_used_tool) - 1):
            if v.splice_used_tool[idx] == from_input and v.splice_used_tool[idx + 1] == to_input:
                return True
    return False


def algorithm_create_table():
    splice_list = []
    for i in range(4):
        for j in range(4):

            if i == j:
                continue
            try:
                algo_key = "{}{}".format(v.used_filament_types.index(v.filament_type[i]) + 1,
                                         v.used_filament_types.index(v.filament_type[j]) + 1)
                if algo_key in splice_list:
                    continue
            except (IndexError, KeyError):
                continue

            if not algorithm_transition_used(i, j):
                continue

            splice_list.append(algo_key)

            try:
                algo = v.splice_algorithm_dictionary["{}{}".format(v.filament_type[i], v.filament_type[j])]
            except (IndexError, KeyError):
                gui.log_warning("WARNING: No Algorithm defined for transitioning" +
                                " {} to {}. Using Default".format(v.filament_type[i],
                                                                  v.filament_type[j]))
                if v.default_splice_algorithm is None:
                    if v.palette_plus:
                        algo = "0,0,0"
                    else:
                        algo = "D0000 D0000 D0000"
                else:
                    algo = v.default_splice_algorithm
            if v.palette_plus:
                v.splice_algorithm_table.append("({},{})".format(algo_key, algo).replace("-", ""))
            else:
                v.splice_algorithm_table.append("D{} {}".format(algo_key, algo))


def generatewarnings():
    warnings = ["\n",
                ";------------------------:\n",
                "; - Process Info/Warnings:\n",
                ";------------------------:\n",
                ";Generated with P2PP version {}\n".format(v.version),
                ";Processed file:. {}\n".format(v.filename),
                ";P2PP Processing time {:-5.2f}s\n".format(v.processtime)]
    gui.create_logitem(("Processing time {:-5.2f}s".format(v.processtime)))
    if len(v.process_warnings) == 0:
        warnings.append(";No warnings\n")
    else:
        for i in range(len(v.process_warnings)):
            warnings.append("{}\n".format(v.process_warnings[i]))

    return warnings


############################################################################
# Generate the Omega - Header that drives the Palette to p2pp_process_file filament
############################################################################
def header_generate_omega(job_name):
    if v.printer_profile_string == '':
        v.printer_profile_string = v.default_printerprofile
        if v.palette3:
            v.printer_profile_string = v.default_printerprofile + v.default_printerprofile
        else:
            v.printer_profile_string = v.default_printerprofile
        gui.log_warning("The PRINTERPROFILE identifier is missing, Default will be used {} \n".format(v.printer_profile_string))
        v.printer_profile_string = v.default_printerprofile

    if len(v.splice_extruder_position) == 0 and not v.palette3:
        gui.log_warning("This does not look like a multi-colour file.\n")

    if v.palette3:
        return {'header': [], 'summary': generatesummary(), 'warnings': generatewarnings()}

    algorithm_create_table()
    if not v.palette_plus:
        return header_generate_omega_palette2(job_name)
    else:
        return header_generate_omega_paletteplus()


def header_generate_omega_paletteplus():
    header = ["MSF1.4\n"]

    cu = "cu:"
    for i in range(4):
        if v.palette_inputs_used[i]:
            cu = cu + "{}{};".format(v.used_filament_types.index(v.filament_type[i]) + 1,
                                     find_nearest_colour(v.filament_color_code[i].strip("\n"))
                                     )
        else:
            cu = cu + "0;"

    header.append(cu + "\n")

    header.append("ppm:{}\n".format((hexify_float(v.palette_plus_ppm))[1:]))
    header.append("lo:{}\n".format((hexify_short(v.palette_plus_loading_offset))[1:]))
    header.append("ns:{}\n".format(hexify_short(len(v.splice_extruder_position))[1:]))
    header.append("np:{}\n".format(hexify_short(len(v.ping_extruder_position))[1:]))
    header.append("nh:0000\n")
    header.append("na:{}\n".format(hexify_short(len(v.splice_algorithm_table))[1:]))

    for i in range(len(v.splice_extruder_position)):
        header.append("({},{})\n".format(hexify_byte(v.splice_used_tool[i])[1:],
                                         (hexify_float(v.splice_extruder_position[i])[1:])))

    # make ping list

    for i in range(len(v.ping_extruder_position)):
        header.append("(64,{})\n".format((hexify_float(v.ping_extruder_position[i])[1:])))

    # insert algos

    for i in range(len(v.splice_algorithm_table)):
        header.append("{}\n"
                      .format(v.splice_algorithm_table[i]))

    summary = []
    warnings = []

    return {'header': header, 'summary': summary, 'warnings': warnings}


def header_generate_omega_palette2(job_name):
    header = []
    summary = []
    warnings = []

    header.append('O21 ' + hexify_short(20) + "\n")  # MSF2.0

    if v.printer_profile_string == '':
        if v.palette3:
            v.printer_profile_string = v.default_printerprofile + v.default_printerprofile
        else:
            v.printer_profile_string = v.default_printerprofile
        gui.log_warning("No or Invalid Printer profile ID specified\nusing default P2PP printer profile ID {}"
                        .format(v.default_printerprofile))

    header.append('O22 D' + v.printer_profile_string.strip("\n") + "\n")  # PRINTERPROFILE used in Palette2
    header.append('O23 D0001' + "\n")  # unused
    header.append('O24 D0000' + "\n")  # unused

    omega_str = "O25"

    initools = [0, 1, 2, 3]
    for i in range(4):
        if not v.palette_inputs_used[i]:
            initools[i] = -1

    for i in initools:
        if i != -1:

            omega_str += " D{}{}{}{}".format(v.used_filament_types.index(v.filament_type[i]) + 1,
                                             v.filament_color_code[i].strip("\n"),
                                             find_nearest_colour(v.filament_color_code[i].strip("\n")),
                                             v.filament_type[i].strip("\n")
                                             )
        else:
            omega_str += " D0"

    header.append(omega_str + "\n")

    header.append('O26 ' + hexify_short(len(v.splice_extruder_position)) + "\n")
    header.append('O27 ' + hexify_short(len(v.ping_extruder_position)) + "\n")
    if len(v.splice_algorithm_table) > 9:
        header.append("O28 D{:0>4d}\n".format(len(v.splice_algorithm_table)))
    else:
        header.append('O28 ' + hexify_short(len(v.splice_algorithm_table)) + "\n")
    header.append('O29 ' + hexify_short(v.hotswap_count) + "\n")

    for i in range(len(v.splice_extruder_position)):
        if v.accessory_mode:
            header.append("O30 D{:0>1d} {}\n".format(v.splice_used_tool[i],
                                                     hexify_float(v.splice_extruder_position[i])
                                                     )
                          )
        else:
            header.append("O30 D{:0>1d} {}\n".format(v.splice_used_tool[i],
                                                     hexify_float(v.splice_extruder_position[i] + v.autoloadingoffset)
                                                     )
                          )

    if v.accessory_mode:
        for i in range(len(v.ping_extruder_position)):
            header.append("O31 {} {}\n".format(hexify_float(v.ping_extruder_position[i]),
                                               hexify_float(v.ping_extrusion_between_pause[i])))

    for i in range(len(v.splice_algorithm_table)):
        header.append("O32 {}\n"
                      .format(v.splice_algorithm_table[i]))

    if v.autoloadingoffset > 0:
        header.append("O40 D{}".format(v.autoloadingoffset))
    else:
        v.autoloadingoffset = 0

    if not v.accessory_mode:
        if len(v.splice_extruder_position) > 0:
            header.append("O1 D{} {}\n"
                          .format(job_name,
                                  hexify_long(int(v.splice_extruder_position[-1] + 0.5 + v.autoloadingoffset))))
        else:
            header.append("O1 D{} {}\n"
                          .format(job_name, hexify_long(int(v.total_material_extruded + 0.5 + v.autoloadingoffset))))

        if v.generate_M0:
            header.append("M0\n")
        if not v.klipper:
            header.append("T0\n")

        summary = generatesummary()
        warnings = generatewarnings()

    return {'header': header, 'summary': summary, 'warnings': warnings}


def generatesummary():
    summary = [";Splice Information:\n", ";-------------------\n",
               ";       Splice Offset = {:-8.2f}mm\n".format(v.splice_offset),
               ";       Autoloading Offset = {:-8.2f}mm\n\n".format(v.autoloadingoffset)]

    for i in range(len(v.splice_extruder_position)):
        if i == 0:
            pos = 0
        else:
            pos = v.splice_extruder_position[i - 1]

        summary.append(";{:04}   Input: {}  Location: {:-8.2f}mm   length {:-8.2f}mm \n"
                       .format(i + 1,
                               v.splice_used_tool[i] + 1,
                               pos,
                               v.splice_length[i]
                               )
                       )

    summary.append("\n")
    summary.append(";Ping Information:\n")
    summary.append(";-----------------\n")

    for i in range(len(v.ping_extruder_position)):
        pingtext = ";Ping {:04} at {:-8.2f}mm\n".format(i + 1, v.ping_extruder_position[i])
        summary.append(pingtext)

    if v.side_wipe and v.side_wipe_loc == "" and not v.bigbrain3d_purge_enabled:
        gui.log_warning("Using sidewipe with undefined SIDEWIPELOC!!!")

    return summary


# PALETTE 3

def generate_meta():
    fila = []
    lena = {}
    vola = {}
    inputsused = 0


    if v.palette3 and len(v.splice_extruder_position) < 2:
        try:
            drive_used = v.splice_used_tool[0]+1
        except IndexError:
            drive_used = 1
        v.palette_inputs_used[drive_used-1] = True

    for i in range(v.colors):
        if v.palette_inputs_used[i]:
            inputsused += 1
            fila.append({"materialId": v.used_filament_types.index(v.filament_type[i]) + 1,
                         "filamentId": i + 1,
                         "type": v.filament_type[i],
                         "name": find_nearest_colour(v.filament_color_code[i]),
                         "color": "#" + v.filament_color_code[i].strip("\n")
                         })
            try:
                if i == v.splice_used_tool[0]:
                    add = v.splice_offset
                else:
                    add = 0
            except IndexError:
                add = 0

            if v.palette3 and len(v.splice_extruder_position) < 2:
                lena[str(i + 1)] = int(v.total_material_extruded + 0.5 + v.autoloadingoffset)
                vola[str(i + 1)] = int(purgetower.volfromlength(v.total_material_extruded + 0.5 + v.autoloadingoffset))
            else:
                lena[str(i + 1)] = int(v.material_extruded_per_color[i] + add)
                vola[str(i + 1)] = int(purgetower.volfromlength(v.material_extruded_per_color[i] + add))

    bounding_box = {"min": [v.bb_minx, v.bb_miny, v.bb_minz], "max": [v.bb_maxx, v.bb_maxy, v.bb_maxz]}


    splice_count = len(v.splice_extruder_position)

    if v.palette3 and splice_count == 0:
        splice_count = 1

    metafile = {"version": "3.2",
                "setupId": "null",
                "printerProfile": {
                    "id": v.printer_profile_string,
                    "name": v.p3_printername
                },
                "preheatTemperature": {
                    "nozzle": [0],
                    "bed": 0
                },
                "paletteNozzle": 0,
                "time": v.printing_time,
                "length": lena,
                "totalLength": int(v.total_material_extruded + 0.5 + v.autoloadingoffset),
                "volume": vola,
                "totalVolume": int(purgetower.volfromlength(v.total_material_extruded + 0.5 + v.autoloadingoffset)),
                "inputsUsed": inputsused,
                "splices": splice_count,
                "pings": len(v.ping_extruder_position),
                "boundingBox": bounding_box,
                "filaments": fila
                }

    if v.p3_process_preheat:
        try:
            if v.palette3 and len(v.splice_extruder_position) < 2:
                first_filament = drive_used-1
            else:
                first_filament = v.splice_used_tool[0]

            metafile["preheatTemperature"]["nozzle"] = [v.p3_printtemp[first_filament]]
            metafile["preheatTemperature"]["bed"] = v.p3_bedtemp[first_filament]
        except(IndexError, KeyError):
            pass

    return json.dumps(metafile, indent=2)


def generate_palette():
    palette = {"version": "3.0",
               "drives": [],
               "splices": [],
               "pingCount": len(v.ping_extruder_position),
               "algorithms": []
               }
    if len(v.splice_extruder_position) < 2:
        try:
            drive_used = v.splice_used_tool[0]+1
        except IndexError:
            drive_used = 1

        palette["splices"] = [{"id": drive_used, "length": round(v.total_material_extruded + v.autoloadingoffset, 4)}]
        if v.colors == 4:
            palette["drives"] = [0, 0, 0, 0]
        else:
            palette["drives"] = [0, 0, 0, 0, 0, 0, 0, 0]
        palette["drives"][drive_used-1] = drive_used
        palette["algorithms"].append({
            "ingoingId": drive_used,
            "outgoingId": drive_used,
            "heat": 0,
            "compression": 0,
            "cooling": 0
        })
    else:
        for i in range(len(v.splice_extruder_position)):
            palette["splices"].append(
                {"id": v.splice_used_tool[i] + 1, "length": round(v.splice_extruder_position[i] + v.autoloadingoffset, 4)})

        splice_list = []
        palette["drives"] = []

        for i in range(v.colors):

            fIdx = 0
            if v.palette_inputs_used[i]:
                fIdx = i + 1

            palette["drives"].append(fIdx)

            for j in range(v.colors):
                if i == j:
                    continue
                try:
                    algo_key = "{}{}".format(v.used_filament_types.index(v.filament_type[i]) + 1,
                                             v.used_filament_types.index(v.filament_type[j]) + 1)
                    if algo_key in splice_list:
                        continue
                except (IndexError, KeyError):
                    continue

                if not algorithm_transition_used(i, j):
                    continue

                splice_list.append(algo_key)
                try:
                    algo = v.splice_algorithm_dictionary["{}{}".format(v.filament_type[i], v.filament_type[j])]
                except (IndexError, KeyError):
                    algo = v.default_splice_algorithm
                    gui.log_warning("WARNING: No Algorithm defined for transitioning" +
                                    " {} to {}. Using Default Splice Algorithm".format(v.filament_type[i],
                                                                                       v.filament_type[j]))
                try:
                    algin = int(algo_key[0])
                except ValueError:
                    algin = 0

                try:
                    algout = int(algo_key[1])
                except ValueError:
                    algout = 0

                palette["algorithms"].append({
                    "ingoingId": algin,
                    "outgoingId": algout,
                    "heat": algo[0],
                    "compression": algo[1],
                    "cooling": algo[2]
                })

    return json.dumps(palette, indent=2)


def header_generate_omega_palette3(job_name):
    return generate_meta(), generate_palette()
