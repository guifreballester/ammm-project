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

    chr_nurses = chromosomes[0:nurses]
    chr_nurses_hours = chromosomes

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
        n = calculate_working(sol, nurse, hours_ordered[nurse])
        if (sum(n) < d.get('minHours') and sum(n) > 0):
            n = calculate_working(sol, nurse, hours_ordered[nurse], nurse=n)
        sol[nurse] = n
    fitness = sum([nurse.any() for nurse in sol])
    return sol, fitness


def calculate_working(sol, n, h, nurse=None):

    if nurse is None:
        nurse = [0] * len(sol[n])
    #print h
    #print "Starting", h
    for hour in h:
        if nurse[hour]:
            continue
        hours_working = np.sum(nurse)
        if hours_working == d.get('maxHours'):
            return nurse
        if not calculate_consec(nurse, hour):
            continue
        if not calculate_presence(nurse, hour):
            continue
        rest = calculate_rest(nurse, hour, h)
        if type(rest) == list:
            nurse = rest
            continue
        elif not rest:
            continue
        if hours_working > 0 and hours_working < d.get('minHours'):
            nurse[hour] = 1
        elif calculate_demand(sol, hour):
            nurse[hour] = 1
        if DEBUG:
            print "Hour", hour
            print "Nurse", nurse
            pdb.set_trace()
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


def calculate_demand(sol, hour):
    """ Gives the cost for an specific hour so the demand is fulfilled """
    hour_demand = np.sum(sol, axis=0)[hour]

    return hour_demand < d.get('demand')[hour]


def calculate_presence(nurse, hour):
    first_element, last_element = _get_first_and_last(nurse)
    if first_element is None or last_element is None:
        return True

    m_element = min(hour, first_element)
    ma_element = max(hour, last_element)

    return not (ma_element - m_element > d.get('maxPresence'))


def calculate_rest(nurse, h, hours):
    first_element, last_element = _get_first_and_last(nurse)

    if first_element is None or last_element is None:
        return True

    previous_hour = 0
    next_hour = 0

    if h > 0:
        previous_hour = nurse[h - 1]
    if h < d.get('hours') - 1:
        next_hour = nurse[h + 1]

    if (not (next_hour and previous_hour)) and (
            first_element < h < last_element):
        return True

    working_hours = np.sum(nurse)
    # Calculates the distance between hour H and the last or first 1
    distance = h - last_element
    if d.get('maxHours') - working_hours >= distance / 2.0 and h > last_element:
        if distance == 1:
            return True
        elif distance > 1:
            current_position = hours.index(h)
            remaning_elements = range(last_element, h + 1, 2)[1:]
            are_in = [e in remaning_elements for e in hours[current_position:]]
            if sum(are_in) == len(remaning_elements):
                for p in remaning_elements:
                    nurse[p] = 1
                return nurse

    distance = first_element - h
    if d.get('maxHours') - working_hours >= distance / 2.0 and h < first_element:
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

    try:
        first_element = nurse.index(1)
        last_element = len(nurse) - 1 - nurse[::-1].index(1)
    except ValueError:
        pass
    return (first_element, last_element)
