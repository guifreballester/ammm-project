import numpy as np
import random
from data import data

DEBUG = False

ALFA = 0.5
MAX_TR = 100
INFEASIBLE = 5000

NURSES = data.get('numNurses')
HOURS = data.get('hours')
MAX_PRESENCE = data.get('maxPresence')
MAX_CONSEC = data.get('maxConsec')


def grasp():
    x = np.ones((NURSES, HOURS), dtype=np.int)
    total_solutions = []
    best_iter = 0
    for i in xrange(MAX_TR):
        solution = construct(ALFA)
        if solution is None:
            continue
        sol = local(solution)
        total_solutions.append(i)
        if is_solution_better(x, sol):
            best_iter = i
            print "Found a better solution"
            print sol
            x = sol
    print "Final Solution"
    print x
    print '\nTotal amount of solutions: ', len(total_solutions)
    print '*' * 30
    print "Best solution: ", best_iter
    total_empty = NURSES - sum([any(element) for element in x])
    print "Total nurses empty: ", total_empty
    print '*' * 30


def is_solution_better(previous, new):
    """ Checks if the new solution is better than the previous """
    total_previous = sum([any(element) for element in previous])
    total_new = sum([any(element) for element in new])
    return total_new < total_previous


def construct(ALFA):
    sol = np.zeros((NURSES, HOURS), dtype=np.int)
    c = initialize_c()
    while not demand_fulfilled(sol):
        res = calculate_cost(sol, c)
        total_costs = [element['cost'] for element in res]
        s_min = min(total_costs)
        s_max = max(total_costs)
        if s_min >= INFEASIBLE:
            return
        s = s_min + ALFA * (s_max - s_min)
        rcl = []
        for element in res:
            if element['cost'] <= s:
                rcl.append(element)

        selected_candidate = random.choice(rcl)
        selected_nurse, cost, selected_hour = selected_candidate.values()
        # Update solution
        sol[selected_nurse][selected_hour] = 1
        if DEBUG:
            print "Updated nurse %s, hour %s, cost %s" % (selected_nurse, selected_hour, cost)
            print sol
        candidate_index = np.where(c == selected_candidate)
        c = np.delete(c, candidate_index)

    if DEBUG:
        print sol

    return sol


def initialize_c():
    c = []
    for nurse in xrange(NURSES):
        for hour in xrange(HOURS):
            c.append({'nurse': nurse,
                      'hour': hour,
                      'cost': 0})
    return np.array(c)


def demand_fulfilled(solution):
    is_fulfilled = []
    for h in xrange(HOURS):
        demand = sum([solution[n][h] for n in xrange(NURSES)])
        is_fulfilled.append(demand >= data.get('demand')[h])
    for n in xrange(NURSES):
        total_h = sum([solution[n][h] for h in xrange(HOURS)])
        is_fulfilled.append(total_h >= data.get('minHours') or total_h == 0)
        break_demand = demand_break(solution[n])
        is_fulfilled.append(break_demand)
    return all(is_fulfilled)


def demand_break(nurse):

    ones_index = np.where(nurse == 1)

    if not ones_index[0].size:
        return True

    first_element = ones_index[0][0]
    last_element = ones_index[0][-1]
    total_breaks = 0
    for h in xrange(first_element, last_element):
        if nurse[h]:
            total_breaks = 0
            continue
        total_breaks += 1
        if total_breaks > 1:
            return False
    return True


def local(solution):
    return solution


def calculate_cost(sol, c):
    for element in c:
        current_nurse = element['nurse']
        current_hour = element['hour']
        cost_hours = calculate_hours_cost(sol[current_nurse])
        cost_consec = calculate_consec_cost(sol[current_nurse], current_hour)
        cost_presence = calculate_pres_cost(sol[current_nurse], current_hour)
        cost_demand = calculate_demand_cost(sol, current_hour)
        cost_break = calculate_break_cost(sol[current_nurse], current_hour)
        total_cost = (cost_hours + cost_consec + cost_presence +
                  cost_break + cost_demand)
        element['cost'] = total_cost
        if DEBUG:
            print element
            print ' '

    if DEBUG:
        prev_nurse = 0
        for element in c:
            if element['nurse'] != prev_nurse:
                print '\n'
                prev_nurse = element['nurse']
            print element

    return c  # cost per la hora h


def calculate_hours_cost(nurse):
    """ Assigns a cost for each nurse depending of working HOURS """
    hours_working = sum([h for h in nurse])
    if hours_working == 0:
        return 1000
    elif hours_working < data.get('minHours'):
        return 0
    elif hours_working < data.get('maxHours'):
        return 100
    else:
        return INFEASIBLE


def calculate_consec_cost(nurse, hour):
    consec_hours = 0
    checking_hour = 0
    if hour - MAX_CONSEC >= 0:
        checking_hour = hour - MAX_CONSEC
    while checking_hour <= hour + MAX_CONSEC:
        if checking_hour == HOURS:
            break
        if nurse[checking_hour] == 1 or checking_hour == hour:
            consec_hours += 1
        elif nurse[checking_hour] == 0:
            consec_hours = 0
        if consec_hours > MAX_CONSEC:
            return INFEASIBLE
        checking_hour += 1
    return -200


def calculate_pres_cost(nurse, hour):
    ones_index = np.where(nurse == 1)
    if ones_index[0].size == 0:
        return 1000
    first_element = ones_index[0][0]
    last_element = ones_index[0][-1]
    if first_element < hour < last_element:
        return 0
    elif last_element - first_element == MAX_PRESENCE:
        return INFEASIBLE
    elif first_element + MAX_PRESENCE >= hour and hour > last_element:
        return 300
    elif last_element - MAX_PRESENCE <= hour and hour < first_element:
        return 300
    return INFEASIBLE


def calculate_break_cost(nurse, hour):
    ones_index = np.where(nurse == 1)
    if ones_index[0].size == 0:
        return 1000

    first_element = ones_index[0][0]
    last_element = ones_index[0][-1]

    previous_hour = 1
    next_hour = 1
    if hour > 0:
        previous_hour = nurse[hour - 1]
    if hour < HOURS - 1:
        next_hour = nurse[hour + 1]
    if first_element < hour < last_element:
        if previous_hour == 0 and next_hour == 0:
            return 0
    if previous_hour == 1 or next_hour == 1:
        return 50
    return 1000


def calculate_demand_cost(sol, hour):
    hour_demand = 0
    for nurse in xrange(NURSES):
        hour_demand += sol[nurse][hour]
    if hour_demand >= data.get('demand')[hour]:
        return 1000
    return 0


if __name__ == '__main__':
    print "Starting"
    grasp()
    print "End"
