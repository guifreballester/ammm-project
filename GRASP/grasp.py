import numpy as np
import random
import matplotlib.pyplot as plt
import time
from data import data_2 as data
import pprint
import cProfile


#np.set_printoptions(threshold=np.inf)

# Setting to True will enable the debugger
DEBUG = False

ALFA = 0.5
MAX_TR = 10
INFEASIBLE = 5000
NO_HOUR = INFEASIBLE
COST_ZERO = 0
OPTIONAL = 500

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
    print "Using data: ", pprint.pprint(data)
    start = time.time()
    x = np.ones((NURSES, HOURS), dtype=np.int)
    total_solutions = []
    plot_values = []
    best_iter = 0
    start = time.time()
    iter_break = MAX_TR
    for i in xrange(MAX_TR):
        print "Iteration: ", i
        if i == iter_break:
            break

        solution = construct(ALFA)
        if solution is None:
            continue
        #sol = solution
        sol = local(solution)

        total_solutions.append(i)
        total_nurses = NURSES - sum([any(element) for element in x])
        plot_values.append((total_nurses, time.time() - start))

        if is_solution_better(x, sol):
            best_iter = i
            iter_break = (MAX_TR - i) / 2
            print "Found a better solution"
            print sol
            np.savetxt('results.out', sol, fmt='%d')
            x = sol
        else:
            print "Solution found is not better"

    print "Final Solution"
    print x
    print '\nTotal amount of solutions: ', len(total_solutions)
    print '*' * 30
    print "Best solution in iteration: ", best_iter
    total_empty = NURSES - sum([any(element) for element in x])
    print "Total nurses empty: ", total_empty
    print '*' * 30
    end = time.time() - start
    print "Total time", end
    #plt.plot([t[1] for t in plot_values], [y[0] for y in plot_values])
    #plt.xlabel("Time")
    #plt.ylabel("Empty nurses")
    #plt.show()
    return end, NURSES - total_empty


def is_solution_better(previous, new):
    """ Checks if the new solution is better than the previous """
    total_previous = np.sum(previous, axis=0)
    total_new = np.sum(new, axis=0)
    return all(np.less(total_new, total_previous))


def construct(ALFA):
    """ Construct method for the GRASP """
    sol = np.zeros((NURSES, HOURS), dtype=np.int)
    c = initialize_c()
    selected_nurse = None
    selected_hour = None
    while not demand_fulfilled(sol):
        try:
            if selected_nurse is None:
                raise TypeError

            d = filter(lambda x: (x['nurse'] == selected_nurse or
                                  x['hour'] == selected_hour), c)
            costs = calculate_cost(sol, d)
            res = list(filter(lambda x: x['nurse'] != selected_nurse or
                              x['hour'] != selected_hour, c))
            res += costs
        except TypeError:
            res = calculate_cost(sol, c)

        total_costs = [element['cost'] for element in res]
        s_min = min(total_costs)
        s_max = max(total_costs)

        if s_min >= INFEASIBLE:
            print "Value became infeasible"
            return

        s = s_min + ALFA * (s_max - s_min)

        rcl = []
        for element in res:
            if DEBUG:
                print element
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
            #pdb.set_trace()

        candidate_index = np.where(c == selected_candidate)
        c = np.delete(c, candidate_index)
        if (np.sum(sol[selected_nurse]) == data.get('maxHours') and
                not demand_break(sol[selected_nurse])):
            print "Constrain not fulfilled"
            return

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


def demand_fulfilled(solution, flag=False):
    """ Checks if the demands have been fulfilled """
    is_fulfilled = calculate_demand(solution)
    total_h = np.sum(solution, axis=1)
    for n in xrange(NURSES):
        is_fulfilled.append(
            total_h[n] >= data.get('minHours') or total_h[n] == 0)
        break_demand = demand_break(solution[n])
        is_fulfilled.append(break_demand)
    return all(is_fulfilled)


def calculate_demand(solution):
    """ Calculates the total demand of a given solution """
    demand = np.sum(solution, axis=0)
    return [demand[h] >= data.get('demand')[h] for h in xrange(HOURS)]


def demand_break(nurse, first_element=None, last_element=None):
    """ Checks if the break demand has been fulfilled """
    if first_element is None:
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
        demand = calculate_demand(tmp_sol)
        if all(demand):
            solution = tmp_sol
        # aviable_rows = [nu for nu in xrange(NURSES) if any(tmp_sol[nu])]
        # random.shuffle(aviable_rows)
        # total_working = np.sum(solution[n])

        # for row in aviable_rows:
        #     possible_hours = []
        #     for h in xrange(HOURS):
        #         if tmp_sol[row][h]:
        #             continue
        #         hours_working = sum([hs for hs in tmp_sol[row]])
        #         # Check maxHours
        #         if hours_working == data.get('maxHours'):
        #             continue
        #         # Check maxPresence (300 or 0 means hour is aviable)
        #         if (calculate_pres_cost(tmp_sol[row], h, hours_working)
        #                 not in (COST_ZERO, OPTIONAL)):
        #             continue
        #         # Check consec (-200 means hour is aviable)
        #         if calculate_consec_cost(tmp_sol[row], h) != COST_ZERO:
        #             continue
        #         if calculate_break_cost(tmp_sol[row], h) == INFEASIBLE:
        #             continue
        #         if not calculate_demand(tmp_sol)[h]:
        #             tmp_sol[row][h] = 1
        #             total_working -= 1
        #         else:
        #             possible_hours.append(h)
        #     if all(calculate_demand(tmp_sol)):
        #         if len(possible_hours):
        #             for element in possible_hours:
        #                 if sum(tmp_sol[row]) == data.get('maxHours'):
        #                     break
        #                 tmp_sol[row][element] = 1
        #         solution = tmp_sol
        #         break
        #     else:
        #         tmp_sol = tmp
        # else:
        #     continue
    return solution


def create_new_solution(sol, n):
    """ Creates a new solution with the nurse n not working any hour """
    tmp = sol.copy()
    new_hours = [0 for i in xrange(HOURS)]
    tmp[n] = new_hours
    return tmp


def calculate_cost(sol, c):
    demands = [None] * HOURS
    """ Calculates the total cost for a given hour and a nurse """
    for element in c:
        nurse = element['nurse']
        hour = element['hour']
        sol_nurse = sol[nurse]
        hours_working = np.sum(sol_nurse)

        cost_hours = calculate_hours_cost(hours_working)
        cost_consec = calculate_consec_cost(sol_nurse, hour)
        cost_presence = calculate_pres_cost(sol_nurse, hour, hours_working)
        if demands[hour] is None:
            demands[hour] = calculate_demand_cost(sol, hour)
        cost_demand = demands[hour]
        cost_break = calculate_break_cost(sol_nurse, hour)
        if INFEASIBLE in (cost_consec, cost_demand, cost_hours, cost_presence):
            total_cost = INFEASIBLE
        else:
            total_cost = min((cost_hours + cost_consec + cost_presence +
                              cost_break + cost_demand), INFEASIBLE)
        element['cost'] = total_cost

    return c  # cost per la hora h


def calculate_hours_cost(hours_working):
    """ Assigns a cost for each nurse depending of working HOURS """
    if hours_working == 0:
        return 1000
    elif hours_working < data.get('minHours'):
        return 0
    elif hours_working < data.get('maxHours'):
        return OPTIONAL

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
    return COST_ZERO


# TODO: Really need to clean this method up
def calculate_pres_cost(nurse, hour, hours_working):
    """ Gives the cost for a given hour depending on the MAX_PRESENCE value """
    ones_index = np.where(nurse == 1)

    if ones_index[0].size == 0:
        return 1000

    first_element = ones_index[0][0]
    last_element = ones_index[0][-1]
    if first_element < hour < last_element:
        return -OPTIONAL
    elif last_element - first_element == MAX_PRESENCE:
        return INFEASIBLE
    if not demand_break(nurse, first_element, last_element):
        return INFEASIBLE
    remaning_hours_presence = ((data.get('maxHours') - hours_working) * 2) - 2

    if ((remaning_hours_presence + last_element) >= hour and
            hour > last_element and first_element + MAX_PRESENCE > hour):
        return COST_ZERO
    elif ((-remaning_hours_presence + first_element) <= hour and
            hour < first_element and last_element - MAX_PRESENCE < hour):
        return COST_ZERO
    return INFEASIBLE


# TODO: Probably should check costs
def calculate_break_cost(nurse, hour):
    """
    Gives the cost for a given hour so the breaks are only
    of 1 hour
    """
    previous_hour = 0
    next_hour = 0

    previous_previous = 0
    next_next = 0

    ones_index = nurse.nonzero()
    if len(ones_index[0]) == 0:
        return 1000
    first_element = ones_index[0][0]
    last_element = ones_index[0][-1]

    if hour > 0:
        previous_hour = nurse[hour - 1]
    if hour < HOURS - 1:
        next_hour = nurse[hour + 1]

    if hour > 1:
        previous_previous = nurse[hour - 2]
    if hour < HOURS - 2:
        next_next = nurse[hour + 2]

    if first_element < hour < last_element:
        if ((previous_previous and not previous_hour) or
                (next_next and not next_hour)):
            return -OPTIONAL * 2
        if previous_hour == 0 and next_hour == 0:
            return -OPTIONAL * 3

        if ((previous_hour == 0 and next_hour) or
                (previous_hour and next_hour == 0)):
            return COST_ZERO

        if previous_hour and next_hour:
            return OPTIONAL * 4

    elif ((previous_previous and not previous_hour) or
            (next_next and not next_hour)):
        return OPTIONAL
    elif ((previous_hour == 0 and next_hour) or
            (previous_hour and next_hour == 0)):
        return OPTIONAL * 4
    return INFEASIBLE


def calculate_demand_cost(sol, hour):
    """ Gives the cost for an specific hour so the demand is fulfilled """
    hour_demand = np.sum(sol, axis=0)[hour]

    if hour_demand < data.get('demand')[hour]:
        return -OPTIONAL * 6
    return OPTIONAL * 6


if __name__ == '__main__':
    print "Starting"
    cProfile.run('grasp()')
    #grasp()
    print "End"
