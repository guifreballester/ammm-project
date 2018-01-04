import numpy as np
from data import data as d

DEBUG = False

if DEBUG:
    import pdb


def decode(population, data):
    for ind in population:
        solution, fitness = decoder_order(data, ind['chr'])
        ind['solution'] = solution
        ind['fitness'] = fitness
    return(population)


def decoder_order(data, chromosomes):
    nurses = data.get('numNurses')
    hours = data.get('hours')

    sol = np.zeros((nurses, hours), dtype=np.int)
    h_demand = np.zeros(d.get('hours'))

    chr_nurses = chromosomes[0:nurses]
    chr_nurses_hours = chromosomes[nurses:]

    # Access order for nurses
    nurses_ordered = sorted(xrange(nurses), key=lambda k: chr_nurses[k])

    hours_ordered = []
    # Create ordered hours for each nurse
    iteration = 0
    for h in xrange(0, nurses * hours, hours):
        hours_ordered.append(
            sorted(xrange(0, hours),
                   key=lambda k: chr_nurses_hours[k + iteration]))
        iteration += hours

    for nurse in nurses_ordered:
        n = calculate_working(sol, nurse, hours_ordered[nurse], h_demand)
        if (sum(n) < d.get('minHours') and sum(n) > 0):
            n = calculate_working(sol, nurse, hours_ordered[nurse], h_demand,
                                  nurse=n)

        sol[nurse] = n

    fitness = sum([nurse.any() for nurse in sol])
    return sol, fitness


def calculate_working(sol, n, h, hours_demand, nurse=None):
    HOURS = d.get('hours')
    if nurse is None:
        nurse = np.zeros(HOURS)

    hours_working = 0

    for hour in h:
        if nurse[hour]:
            continue
        if hours_working == d.get('maxHours'):
            return nurse
        if not calculate_consec(nurse, hour):
            continue

        elements = (first_element, last_element) = _get_first_and_last(nurse)

        if not calculate_presence(nurse, hour, elements):
            continue

        rest = calculate_rest(nurse, hour, h, hours_working, elements)

        if not isinstance(rest, bool):
            nurse = rest
            continue
        elif not rest:
            continue
        if hours_working > 0 and hours_working < d.get('minHours'):
            nurse[hour] = 1
        elif calculate_demand(hour, hours_demand):
            nurse[hour] = 1

        if nurse[hour]:
            hours_working += 1
            hours_demand[hour] += 1

    return nurse


def calculate_consec(nurse, hour):
    """
    Gives the cost for given hour depending on the previous
    and after hours
    """
    MAX_CONSEC = d.get('maxConsec')
    HOURS = d.get('hours')

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
            return False
        checking_hour += 1
    return True


def calculate_demand(hour, hours_demand):
    """ Gives the cost for an specific hour so the demand is fulfilled """

    return hours_demand[hour] < d.get('demand')[hour]


def calculate_presence(nurse, hour, elements):

    first_element, last_element = elements

    if first_element is None or last_element is None:
        return True

    min_element = min(hour, first_element)
    max_element = max(hour, last_element)

    return not (max_element - min_element > d.get('maxPresence'))


def calculate_rest(nurse, h, hours, working_hours, elements):
    # Working hours is a memory reference to the variable in the main method

    first_element, last_element = elements
    previous_hour = 0
    next_hour = 0

    if first_element is None or last_element is None:
        return True

    if h > 0:
        previous_hour = nurse[h - 1]
    if h < d.get('hours') - 1:
        next_hour = nurse[h + 1]

    if (not (next_hour and previous_hour)) and (
            first_element < h < last_element):
        return True

    # Calculates the distance between hour H and the last or first 1
    remaning_hours = (d.get('maxHours') - working_hours) / 2.0

    distance = h - last_element
    if remaning_hours and h > last_element:

        if distance == 1:
            return True

        elif distance > 1:
            current_position = hours.index(h)
            remaning_elements = xrange(last_element + 1, h + 1, 2)
            are_in = [e in remaning_elements for e in hours[current_position:]]

            if sum(are_in) == len(remaning_elements):

                for p in remaning_elements:
                    nurse[p] = 1

                return nurse

    distance = first_element - h
    if remaning_hours and h < first_element:
        if distance == 1:
            return True
        elif distance > 1:
            current_position = hours.index(h)
            remaning_elements = xrange(h, first_element, 2)

            are_in = [e in remaning_elements for e in hours[current_position:]]

            if sum(are_in) == len(remaning_elements):
                for p in remaning_elements:
                    nurse[p] = 1
                return nurse

    return False


def _get_first_and_last(nurse):
    first_element = None
    last_element = None
    elements = nurse.nonzero()
    try:
        first_element = elements[0][0]
        last_element = elements[0][-1]
    except IndexError:
        pass

    return (first_element, last_element)
