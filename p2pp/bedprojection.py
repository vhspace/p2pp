__author__ = 'Tom Van den Eede'
__copyright__ = 'Copyright 2018-2022, Palette2 Splicer Post Processing Project'
__credits__ = ['Tom Van den Eede']
__license__ = 'GPLv3'
__maintainer__ = 'Tom Van den Eede'
__email__ = 'P2PP@pandora.be'


import p2pp.variables as v


# SECTION BedProjection


class BedProjection(object):

    def __init__(self, width, height):
        self.data = Image.new('1', (width, height), 0)
        self.draw = ImageDraw.Draw(self.data)
        self._posx = 0.0
        self._posy = 0.0

    def position(self, x, y):
        if x is not None:
            self._posx = x
        if y is not None:
            self._posy = y

    def line(self, x, y):
        if x is None:
            x = self._posx
        if y is None:
            y = self._posy
        self.draw.line(((self._posx + v.bed_origin_x, self._posy + v.bed_origin_y),
                        (x + v.bed_origin_x, y + v.bed_origin_y)), 1, 1, None)
        self._posx = x
        self._posy = y

    def save_image(self):
        self.data.save('/Users/tomvandeneede/Desktop/print.png', "PNG")
