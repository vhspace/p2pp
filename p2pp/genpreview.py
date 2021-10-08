import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D


extrusions = {}
z = 0
prevx = 0
prevy = 0


def add_extrusion(x, y, tool, extrusion):
    global prevx, prevy, extrusions
    if extrusion > 0:
        try:
            extrusions[z].append((x, y, prevx, prevy, tool))
        except KeyError:
            extrusions[z] = [(x, y, prevx, prevy, tool)]
    else:
        prevx = x
        prevy = y


def buildpreview():
    # for i in sorted(extrusions.keys()):
    #     print("Layer z={} has {} extrusions".format(i, len(extrusions[i])))
    #     fig = plt.figure(figsize=(16, 16))
    #     sp = fig.add_subplot(111, projection='3d')
    #     for tupple in extrusions[i]:
    #         x0 = tupple[0]
    #         y0 = tupple[1]
    #         x1 = tupple[2]
    #         y1 = tupple[3]
    #         sp.
    #         sp.plot([0.5 * (x0 + x1)], [0.5 * (y0 + y1)], tuple[4], markersize=2)
    #     fig.savefig(fname="layer_{}.png".format(i))
    pass
