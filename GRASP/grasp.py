import numpy as np
from data import data


alfa = 0.5
max_tr = 1000


def grasp():
    x = np.ones((data.get('numNurses'),), dtype=np.int)

    for i in xrange(max_tr):
        y = construct(alfa)

        sol = local(y)

        if np.sum(sol) < np.sum(x):
            x = sol


def construct(alfa):
    sol = np.zeros((data.get('numNurses'), data.get('hours')), dtype=np.int)
    c = np.ones((data.get('numNurses'), data.get('hours')), dtype=np.int)
    while c != 0:
        res = cost(c)
        s_min = res.min # min
        s_max = res.max # max
        s = s_min + alfa * (s_max - s_min)
        rcl = []
        for element in res:
            if element < s:
                rcl.append(1)
            else:
                rcl.append(0)


def local(y):
    pass


def cost(c, h):
    return []  # cost per la hora h