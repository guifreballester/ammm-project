import numpy as np
import random
from data import data


alfa = 0.5
max_tr = 1000
nurses = data.get('numNurses')
hours = data.get('hours')


def grasp():
    x = np.ones((nurses, hours), dtype=np.int)

    for i in xrange(max_tr):
        solution = construct(alfa)
        sol = local(solution)

        if is_solution_better(x, sol):
            x = sol


def is_solution_better(previous, new):
    """ Checks if the new solution is better than the previous """
    total_previous = sum([any(element) for element in previous])
    total_new = sum([any(element) for element in new])

    return total_new > total_previous


def construct(alfa):
    sol = np.zeros((nurses, hours), dtype=np.int)
    while not demand_fulfilled(sol):
        res = cost(sol)
        s_min = res.min()
        s_max = res.max()
        s = s_min + alfa * (s_max - s_min)
        rcl = []
        for nurse in res:
            for hour in nurse:
                if hour <= s:
                    rcl.append((res.index(nurse), nurse.index(hour)))

        selected_nurse, selected_hour = random.choice(rcl)
        # Update solution
        sol[selected_nurse][selected_hour] = 1

    return sol


def demand_fulfilled(solution):
    is_fulfilled = []
    for h in xrange(hours):
        is_fulfilled.append(sum([solution[n][h]
                            for n in xrange(nurses)]) >= data.get('demand')[h])
    for n in xrange(nurses):
        total_h = sum([solution[n][h] for h in xrange(hours)])
        is_fulfilled.append(total_h >= data.get('minHours') or total_h == 0)
    return all(is_fulfilled)


def local(solution):
    return solution


def cost(sol):
    c = []
    for nurse in sol:
        cost_hours = calculate_hours_cost(nurse)
        for working in nurse:
            if working:
                continue
            cost_consec = cal

            total_cost = cost_hours
            c.append((nurse, hours, total_cost))
    return []  # cost per la hora h


def calculate_hours_cost(nurse):
    """ Assigns a cost for each nurse depending of working hours """
    hours_working = sum([h for h in nurse])
    if hours_working == 0:
        return 10
    elif hours_working < data.get('minHours'):
        return 0
    elif hours_working < data.get('maxHours'):
        return 5
    else:
        return 10000
