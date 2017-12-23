import numpy as np
import random
import matplotlib.pyplot as plt
import time

from data import data_2 as data

# Setting to True will enable the debugger
DEBUG = False

ALFA = 0.8
MAX_TR = 10
INFEASIBLE = 5000
NO_HOUR = INFEASIBLE

NURSES = data.get('numNurses')
HOURS = data.get('hours')
MAX_PRESENCE = data.get('maxPresence')
MAX_CONSEC = data.get('maxConsec')

if DEBUG:
    import pdb


def grasp():
    """
    GRASP method call, it calculates the hours in which a given number
    of nurses has to work in order to minimize the nurses working
    """
    x = np.ones((NURSES, HOURS), dtype=np.int)
    total_solutions = []
    plot_values = []
    best_iter = 0
    start = time.time()
    for i in xrange(MAX_TR):
        solution = construct(ALFA)
        if solution is None:
            continue
        sol = local(solution)
        total_solutions.append(i)
        total_nurses = NURSES - sum([any(element) for element in x])
        plot_values.append((total_nurses, time.time() - start))
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
    print plot_values
    plt.plot([t[1] for t in plot_values], [y[0] for y in plot_values])
    plt.xlabel("Time")
    plt.ylabel("Empty nurses")
    plt.show()


def is_solution_better(previous, new):
    """ Checks if the new solution is better than the previous """
    total_previous = sum([any(element) for element in previous])
    total_new = sum([any(element) for element in new])
    return total_new < total_previous


def construct(ALFA):
    """ Construct method for the GRASP """
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
            print "Updated nurse %s, hour %s, cost %s" % (
                selected_nurse, selected_hour, cost)
            print sol
            pdb.set_trace()

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
    """ Checks if the demands have been fulfilled """
    is_fulfilled = calculate_demand(solution)
    for n in xrange(NURSES):
        total_h = sum([solution[n][h] for h in xrange(HOURS)])
        is_fulfilled.append(total_h >= data.get('minHours') or total_h == 0)
        break_demand = demand_break(solution[n])
        is_fulfilled.append(break_demand)
    return all(is_fulfilled)


def calculate_demand(solution):
    """ Calculates the total demand of a given solution """
    demand_fulfilled = []
    for h in xrange(HOURS):
        demand = sum([solution[n][h] for n in xrange(NURSES)])
        demand_fulfilled.append(demand >= data.get('demand')[h])
    return demand_fulfilled


def demand_break(nurse):
    """ Checks if the break demand has been fulfilled """
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
    """ Iterates a given solution to try and find a better solution """
    tmp_sol = solution
    for n in xrange(NURSES):
        if not any(solution[n]):
            continue
        tmp_sol = create_new_solution(solution, n)
        tmp = tmp_sol
        demand = calculate_demand(tmp_sol)
        if all(demand):
            solution = tmp_sol
            continue
        aviable_rows = [nu for nu in xrange(NURSES) if any(tmp_sol[nu])]
        random.shuffle(aviable_rows)

        for row in aviable_rows:
            for h in xrange(HOURS):
                if demand[h] or tmp_sol[row][h]:
                    continue
                hours_working = sum([h for h in tmp_sol[row]])
                # Check maxHours
                if hours_working == data.get('maxHours'):
                    continue
                # Check maxPresence (300 or 0 means hour is aviable)
                if calculate_pres_cost(tmp_sol[row], h) not in (300, 0):
                    continue
                # Check consec (-200 means hour is aviable)
                if calculate_consec_cost(tmp_sol[row], h) != -200:
                    continue
                tmp_sol[row][h] = 1
            if all(calculate_demand(tmp_sol)):
                solution = tmp_sol
                break
            else:
                tmp_sol = tmp
        else:
            continue
    return solution


def create_new_solution(sol, n):
    """ Creates a new solution with the nurse n not working any hour """
    tmp = sol.copy()
    new_hours = [0 for i in xrange(len(sol[n]))]
    tmp[n] = new_hours
    return tmp


def calculate_cost(sol, c):
    """ Calculates the total cost for a given hour and a nurse """
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
            print "Total cost", total_cost
            print cost_hours, cost_consec, cost_presence, cost_break, cost_demand
            print element
            print ' '

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

    return NO_HOUR


def calculate_consec_cost(nurse, hour):
    """
    Gives the cost for given hour depending on the previous
    and after hours
    """
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
            return NO_HOUR
        checking_hour += 1
    return -20


# TODO: Really need to clean this method up
def calculate_pres_cost(nurse, hour):
    """ Gives the cost for a given hour depending on the MAX_PRESENCE value """
    ones_index = np.where(nurse == 1)
    if ones_index[0].size == 0:
        return 1000
    first_element = ones_index[0][0]
    last_element = ones_index[0][-1]
    if first_element < hour < last_element:
        return -200
    elif last_element - first_element == MAX_PRESENCE:
        return NO_HOUR
    elif first_element + (MAX_PRESENCE / 2) >= hour and hour > last_element:
        return -100
    elif last_element - (MAX_PRESENCE / 2) <= hour and hour < first_element:
        return -100
    elif first_element + MAX_PRESENCE >= hour and hour > last_element:
        if nurse[hour - 2]:
            return 0
        return 300
    elif last_element - MAX_PRESENCE <= hour and hour < first_element:
        if nurse[hour + 2]:
            return 0
        return 300

    return NO_HOUR


# TODO: Probably should check costs
def calculate_break_cost(nurse, hour):
    """
    Gives the cost for a given hour so the breaks are only
    of 1 hour
    """
    ones_index = np.where(nurse == 1)
    if ones_index[0].size == 0:
        return 1000

    first_element = ones_index[0][0]
    last_element = ones_index[0][-1]

    previous_hour = 1
    next_hour = 1
    next_next_hour = 0
    previous_previous_hour = 0

    if hour > 0:
        previous_hour = nurse[hour - 1]
    elif hour < HOURS - 1:
        next_hour = nurse[hour + 1]

    if hour < HOURS - 2:
        next_next_hour = nurse[hour + 2]
    elif hour > 1:
        previous_previous_hour = nurse[hour - 2]

    if first_element < hour < last_element:
        if previous_hour == 0 and next_hour == 0:
            return -1000
        return 0
    elif previous_hour == 1 or next_hour == 1:
        return 100

    if next_next_hour or previous_previous_hour:
        return 100

    return 1000


def calculate_demand_cost(sol, hour):
    """ Gives the cost for an specific hour so the demand is fulfilled """
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
