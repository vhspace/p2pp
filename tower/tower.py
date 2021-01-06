__author__ = 'Tom Van den Eede'
__copyright__ = 'Copyright 2018-2021, Palette2 Splicer Post Processing Project'
__credits__ = ['Tom Van den Eede']
__license__ = 'GPLv3'
__maintainer__ = 'Tom Van den Eede'
__email__ = 'P2PP@pandora.be'


from random import random
from copy import deepcopy
from math import pi, sqrt

class Tower(object):


    def __init__(self, purge_per_layer_array, first_layerheight, layerheight, extrusionwidth, wipespeed, filamentdiameter = 1.75):

        self.purge_per_layer = deepcopy(purge_per_layer_array)
        self._base_x = None
        self._base_y = None
        self._size_x = None
        self._size_y = None
        self.wipespeed = wipespeed
        self.filament_diameter = filamentdiameter
        self.extrusionwidth = extrusionwidth
        self.firstlayerheight = first_layerheight
        self.layerheigth = layerheight
        self._zigurat = None
        self.layer = 0
        max2come = 0
        for idx in range(len(purge_per_layer_array)-1,-1,-1):
            max2come = max(max2come, purge_per_layer_array[idx])
            self._zigurat.insert(0, max2come)

        self._optimized_zigurat = deepcopy(self._zigurat)


    def _extrusion(self,l):
        if self.layer == 0:
            lh = self.firstlayerheight
        else:
            lh = self.layerheigth
        vol = lh * self.extrusionwidth * l

        return vol / self.filament_diameter / self.filament_diameter / pi


    def _rectangle(self, offset):
        lx = self.size_x - 2 * offset * self.extrusionwidth
        ly = self.size_y - 2 * offset * self.extrusionwidth

        speed = 1200 if self.layer==0 else self.wipespeed

        return [
            "G1 X{} Y{} F{}".format(self._base_x + offset * self.extrusionwidth, self._base_y + offset * self.extrusionwidth, speed),
            "G1 X{} E{}".format(self._base_x + lx, self._extrusion(lx)),
            "G1 Y{} E{}".format(self._base_y + ly, self._extrusion(ly)),
            "G1 X{} E{}".format(self._base_x + offset * self.extrusionwidth, self._extrusion(lx)),
            "G1 Y{} E{}".format(self._base_y + offset * self.extrusionwidth, self._extrusion(ly)),
        ]

    def _brim(self):
        gcode = []
        for i in range(5):
            gcode.append(self._rectangle(-5+i))
        return gcode

    def _perimeter(self):
        return self.rectangle(0).append(self.rectangle(1))


    def _intersect(self,x, y, direction,left):
        # calculate intersection points between the rectangle and the line through x,y
        points = []
        liy = y - left * direction * self.size_x/2
        lix = x - left * direction * self.size_y/2
        if  self._base_y <= liy <= self._base_y + self._size_y :
            points.append((self._base_x + (self._size_x if left==-1) , liy))
        else:
            points.append(lix ,self._base_x + (self._size_y if left == -1) )
        return points


    def _diagonal(self, direction, dist):
        gcode = []
        crosspoints = []
        startx = self._base_x + self._size_x/2
        starty = self._base_y + self._size_y/2

        dx = dist * sqrt(2)

        half_range = int((self._size_x + self._size_y)/(2*dx))

        for idx in range(-half_range, half_range + 1 , 1):
            _ip = self._intersect(startx + idx*dx, starty, direction)
        return gcode

    def _diagonal_right(self, dist):
        gcode = []
        return gcode

    def generate_layer(self, layernum):
        gcode = []
        gcode.append(self.perimeter())
        if layernum % 2:
            gcode.append(self._diagonal_left())
        else:
            gcode.append(self._diagonal_right())
        return gcode

