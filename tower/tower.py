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



def _zigurat_model(purgereq):
    ret = [ ]
    max_to_come = 0
    for idx in range(len(purgereq)-1, -1, -1):
        max_to_come = max(max_to_come, purgereq[idx])
        ret.insert(0, max_to_come)
    return ret

def optimize_zigurat():
    pass

if __name__ == "__main__":
    stop = 50 + random()*50
    for i in range(100):
        if (i>stop):
            layerpurge.append(0)
        else:
            layerpurge.append((int(random() * 4) + 1) * (100 + 20 * random()))

    print (sum(layerpurge), layerpurge)
    zigurat = _zigurat_model(layerpurge)
    print(sum(zigurat), zigurat)










