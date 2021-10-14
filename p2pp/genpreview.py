#
# import matplotlib.pyplot as plt
# from mpl_toolkits import mplot3d
# import p2pp.variables as v
# from cycler import cycler

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
    # fig = plt.figure(figsize=(16, 16))
    # ax = fig.add_subplot(111, projection='3d')
    # ax.set_xlim(v.bed_origin_x, v.bed_max_x)
    # ax.set_ylim(v.bed_origin_y, v.bed_max_y)
    # ax.set_zlim(0, 300)
    # prevcol = -9
    #
    # colors = []
    # for i in range(v.colors):
    #     colors.append("#{}00".format(v.filament_color_code[i]))
    #
    # print(colors)
    # print_cycler = cycler(color=colors)
    # ax.set_prop_cycle(print_cycler)
    #
    #
    # for z in sorted(extrusions.keys()):
    #
    #     for tupple in extrusions[z]:
    #         x0 = tupple[0]
    #         y0 = tupple[1]
    #         x1 = tupple[2]
    #         y1 = tupple[3]
    #
    #         if prevcol != tupple[4]:
    #             prevcol = tupple[4]
    #             color = "C{}".format(prevcol)
    #
    #         ax.plot([x0, x1], [y0, y1], [z, z], color=color, linewidth=0.2, markersize=0)
    #
    # fig.savefig(fname="preview.png")
    pass
