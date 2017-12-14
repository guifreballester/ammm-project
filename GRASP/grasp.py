import numpy as np
import random
from data import data

DEBUG = False

ALFA = 0.4
MAX_TR = 10
INFEASIBLE = 10000

NURSES = data.get('numNurses')
HOURS = data.get('hours')
MAX_PRESENCE = data.get('maxPresence')
MAX_CONSEC = data.get('maxConsec')


def grasp():
    x = np.ones((NURSES, HOURS), dtype=np.int)

    for i in xrange(MAX_TR):
        solution = construct(ALFA)
        if solution is None:
            print "Solution became infeasible, skipping to next iteration"
            print "Current iteration %d" % i
            continue
        sol = local(solution)
        if is_solution_better(x, sol):
            print "Found a better solution"
            print sol
            x = sol
    print "Final Solution"
    print x


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
            print sol
            print data.get('demand')
            total_demand = []
            for h in xrange(HOURS):
                total_hours = 0
                for n in xrange(NURSES):
                    total_hours += sol[n][h]
                total_demand.append(total_hours)
            print "Current demand", "Demand"
            for c_demand, d in zip(total_demand, data.get('demand')):
                print c_demand, d
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
        is_fulfilled.append(sum([solution[n][h]
                            for n in xrange(NURSES)]) >= data.get('demand')[h])
    print is_fulfilled
    for n in xrange(NURSES):
        total_h = sum([solution[n][h] for h in xrange(HOURS)])
        is_fulfilled.append(total_h >= data.get('minHours') or total_h == 0)
        is_fulfilled.append(demand_break(solution[n]))
    print solution
    print is_fulfilled[HOURS:]

    return all(is_fulfilled)


def demand_break(nurse):

    ones_index = np.where(nurse == 1)

    if not ones_index[0].size:
        return True

    first_element = ones_index[0][0]
    last_element = ones_index[0][-1]

    for h in xrange(first_element, last_element):

        if nurse[h]:
            continue

        try:
            previous_hour = nurse[h - 1]
            next_hour = nurse[h + 1]
        except IndexError:
            continue
        if not (nurse[h] and (not nurse[previous_hour] or not nurse[next_hour])):
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
        cost_break = calculate_break_cost(sol[current_nurse], current_hour)

        if DEBUG:
            print "Costs hour %s, cost consec %s, cost presence %s, cost break %s" % (
                cost_hours, cost_consec, cost_presence, cost_break)

        total_cost = cost_hours + cost_consec + cost_presence + cost_break
        element['cost'] = total_cost

    if DEBUG:
        prev_nurse = 0
        for element in c:
            if element['nurse'] != prev_nurse:
                print '\n'
            print element

    return c  # cost per la hora h


def calculate_hours_cost(nurse):
    """ Assigns a cost for each nurse depending of working HOURS """
    hours_working = sum([h for h in nurse])
    if hours_working == 0:
        return 600
    elif hours_working < data.get('minHours'):
        return 0
    elif hours_working < data.get('maxHours'):
        return 300
    else:
        return INFEASIBLE


def calculate_consec_cost(nurse, hour):
    current_hour = nurse[hour]
    consec_hours = 0
    checking_hour = nurse[current_hour - MAX_CONSEC]
    while checking_hour != current_hour + MAX_CONSEC:
        if nurse[checking_hour] == 1 or nurse[checking_hour] == hour:
            consec_hours += 1
        elif nurse[checking_hour] == 0:
            consec_hours = 0
        if consec_hours > MAX_CONSEC:
            return INFEASIBLE
        checking_hour += 1
    return 100


def calculate_pres_cost(nurse, hour):
    current_hour = nurse[hour]
    ones_index = np.where(nurse == 1)
    if not ones_index[0].size:
        return 300
    first_element = ones_index[0][0]
    last_element = ones_index[0][-1]

    if first_element < current_hour < last_element:
        return 100
    elif ((hour + MAX_PRESENCE > last_element) or
            (hour - MAX_PRESENCE < first_element)):
        return 100
    return INFEASIBLE


def calculate_break_cost(nurse, hour):
    ones_index = np.where(nurse == 1)

    if not ones_index[0].size:
        return 300

    first_element = ones_index[0][0]
    last_element = ones_index[0][-1]

    try:
        previous_hour = nurse[hour - 1]
    except IndexError:
        previous_hour = nurse[hour]

    try:
        next_hour = nurse[hour + 1]
    except IndexError:
        next_hour = nurse[hour]

    if hour < first_element or hour > last_element:
        return 100

    elif previous_hour == 0 or next_hour == 0:
        return 0
    return 100


def calculate_demand_cost(sol, hour):
    hour_demand = 0
    for nurse in xrange(NURSES):
        hour_demand += nurse[hour]

    if hour_demand >= data.get('demand')[hour]:
        return 500
    return 0


if __name__ == '__main__':
    print "Starting"
    grasp()
    print "End"
