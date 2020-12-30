__author__ = 'Tom Van den Eede'
__copyright__ = 'Copyright 2018-2021, Palette2 Splicer Post Processing Project'
__credits__ = ['Tom Van den Eede']
__license__ = 'GPLv3'
__maintainer__ = 'Tom Van den Eede'
__email__ = 'P2PP@pandora.be'


from random import random

# Amount of purge in each of the layers
layerpurge = []

# derived data
_required = []


# calculate the required number of purge length per layer
def calculate_required(base):
    maxup = 0

    tmp = []

    for layer in range(len(base)-1, -1, -1):
        maxup = max(maxup, base[layer])
        tmp.append(maxup)

    return tmp


def optimize_tower(maxdeltalayers) :

    optimized = []


    def avg_purge(layer_, maxdiff):
        sum = 0
        count = 0
        for l in range(max(0, layer_ - maxdiff), layer_+1):
            sum += layerpurge[l]
            count += 1
        return sum/count

    for layer in range(len(layerpurge)):
        optimized.append(avg_purge(layer,maxdeltalayers))

    return calculate_required(optimized)


if __name__ == "__main__":
    stop = 50 + random()*50
    for i in range(100):
        if (i>stop):
            layerpurge.append(0)
        else:
            layerpurge.append((int(random() * 4) + 1) * (100 + 20 * random()))

    print (sum(layerpurge), layerpurge)
    _required = calculate_required(layerpurge)
    _required.reverse()
    print(sum(_required), _required)
    _required = optimize_tower(20)
    _required.reverse()
    print(sum(_required), _required)
    _required = optimize_tower(50)
    _required.reverse()
    print(sum(_required), _required)
    _required = optimize_tower(100)
    _required.reverse()
    print(sum(_required), _required)










