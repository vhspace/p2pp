__author__ = 'Tom Van den Eede'
__copyright__ = 'Copyright 2018-2022, Palette2 Splicer Post Processing Project'
__credits__ = ['Tom Van den Eede']
__license__ = 'GPLv3'
__maintainer__ = 'Tom Van den Eede'
__email__ = 'P2PP@pandora.be'


from copy import deepcopy
from math import pi, sqrt
from PIL import Image, ImageDraw

totallength = 0


class Tower(object):

    def __init__(self, purge_per_layer_array, first_layerheight, layerheight, extrusionwidth, wipespeed, filamentdiameter=1.75):

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
        self._zigurat = []
        self.layer = 0
        max2come = 0
        for idx in range(len(purge_per_layer_array)-1, -1, -1):
            max2come = max(max2come, purge_per_layer_array[idx])
            self._zigurat.insert(0, max2come)

        self._optimized_zigurat = deepcopy(self._zigurat)

    @staticmethod
    def _dist(p1, p2):
        return sqrt((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2)

    @staticmethod
    def _move(p):
        return "G1 X{:0.3f} Y{:0.3f} F8640".format(p[0], p[1])

    def _extrude(self, p1, p2):
        global totallength
        if p1 == p2:
            return ""
        volume = self._dist(p1, p2) * self.extrusionwidth * self.layerheigth
        length = volume / ((self.filament_diameter * self.filament_diameter) / 4 * pi)
        totallength += length
        return "G1 X{:0.3f} Y{:0.3f} E{:0.5f} F{}".format(p2[0], p2[1], length, self.wipespeed)

    def _rectangle(self, offset):
        lx = self._size_x - 2 * offset * self.extrusionwidth
        ly = self._size_y - 2 * offset * self.extrusionwidth

        speed = 1200 if self.layer == 0 else self.wipespeed

        p1 = (self._base_x + offset * self.extrusionwidth, self._base_y + offset * self.extrusionwidth)
        p2 = (self._base_x + offset * self.extrusionwidth + lx, self._base_y + offset * self.extrusionwidth)
        p3 = (self._base_x + offset * self.extrusionwidth + lx, self._base_y + offset * self.extrusionwidth + ly)
        p4 = (self._base_x + offset * self.extrusionwidth, self._base_y + offset * self.extrusionwidth + ly)
        return [
            self._move(p1),
            self._extrude(p1, p2),
            self._extrude(p2, p3),
            self._extrude(p3, p4),
            self._extrude(p4, p1)
        ]

    def _perimeter(self, layernum):       # perimeter and brim on layer 1

        _gcode = self._rectangle(-0.7)
        count = 6 if layernum == 1 else 1
        for i in range(count):
            _gcode += self._rectangle(-1.7 - i)
        return _gcode

    def _intersect(self, x0, y0, direction):
        points = []

        def calcy(__x):
            return y0 + direction * (__x - x0)

        def calcx(__y):
            return x0 + direction * (__y - y0)

        # doorsnede met rechte x = _base_x
        y = calcy(self._base_x)
        if self._base_y <= y <= self._base_y + self._size_y:
            points.append((self._base_x, y))

        # doorsnede met rechte x = _base_x + _size_x
        y = calcy(self._base_x + self._size_x)
        if self._base_y <= y <= self._base_y + self._size_y:
            points.append((self._base_x + self._size_x, y))

        if len(points) == 2:
            return points

        # rechte
        # doorsnede met rechte y = _base_y
        x = calcx(self._base_y)
        if self._base_x <= x <= self._base_x + self._size_x:
            points.append((x, self._base_y))

        # doorsnede met rechte y = _base_y + _size_y
        x = calcx(self._base_y+self._size_y)
        if self._base_x <= x <= self._base_x + self._size_x:
            points.append((x, self._base_y + self._size_y))

        return points

    def _diagonal(self, direction, ppct):

        def _swap(last, _next):
            return self._dist(last, _next[0]) > self._dist(last, _next[1])

        dx = self.extrusionwidth * (100 / ppct * sqrt(2))

        _ip = []
        _gcode = []

        startx = self._base_x + self._size_x/2
        starty = self._base_y + self._size_y/2

        half_range = int((self._size_x + self._size_y)/(2*dx))

        self.data = Image.new('1', (1000, 1000), 0)
        self.draw = ImageDraw.Draw(self.data)

        for idx in range(-half_range, half_range + 1, 1):
            _ip.append(self._intersect(startx + idx*dx, starty, direction))

        if len(_ip) > 0:
            _gcode.append(self._move(_ip[0][0]))
            _gcode.append(self._extrude(_ip[0][0], _ip[0][1]))

            self.draw.line((_ip[0][0], _ip[0][1]), 1, 1, None)
            last_point = _ip[0][1]
            for i in range(len(_ip)):
                if _swap(last_point, _ip[i]):
                    p1 = _ip[i][1]
                    p2 = _ip[i][0]
                else:
                    p1 = _ip[i][0]
                    p2 = _ip[i][1]
                _gcode.append(self._extrude(last_point, p1))
                _gcode.append(self._extrude(p1, p2))

                self.draw.line((last_point, p1), 1, 1, None)
                self.draw.line((p1, p2), 1, 1, None)
                last_point = p2
        self.data.save('/Users/tomvandeneede/Desktop/tower.png', "PNG")
        return _gcode

    def generate_layer(self, layernum, ppct):
        __gcode = self._perimeter(layernum)
        if layernum % 2:
            __gcode += self._diagonal(-1, ppct)
        else:
            __gcode += self._diagonal(1, ppct)
        return __gcode


if __name__ == "__main__":

    t = Tower([], 0.2, 0.2, 0.45, 3000, 1.75)

    t._base_x = 100
    t._base_y = 100
    t._size_x = 100
    t._size_y = 200

    for pct in range(100):
        percent = pct + 1
        totallength = 0
        gcode = t.generate_layer(4, percent)
        expected = percent/100 * t._size_x * t._size_y * t.layerheigth / pi / 1.75 / 1.75 * 4
        print("PCS {:3} Extruded: {:6}  Needed: {:6} - difference {:6}".format(percent, int(totallength), int(expected), int(totallength-expected)))

    gcode = t.generate_layer(4, 10)
