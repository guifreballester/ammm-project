# imports
import math
import matplotlib.pyplot as plt

import BRKGA as brkga  # BRKGA framework (problem independent)
import DECODER_DUMMY as decoder  # Dgcoder algorithm (problem-dependent)
# Input data (problem-dependent and instance-dependent)
from data import data
# Configuration parameters (problem-dependent and execution-dependent)
from CONFIGURATION import config
import time
import numpy as np
import pprint

PLOTS_ENABLED = True

# initializations
numIndividuals = int(config['numIndividuals'])
chrLength = int(config['chromosomeLength'])
numElite = int(math.ceil(numIndividuals * config['eliteProp']))
numMutants = int(math.ceil(numIndividuals * config['mutantProp']))
numCrossover = max(numIndividuals - numElite - numMutants, 0)
maxNumGen = int(config['maxNumGen'])
ro = float(config['inheritanceProb'])
evol = []


def main():
    # Main body
    print "Using data: ", pprint.pprint(data)
    start = time.time()
    population = brkga.initializePopulation(numIndividuals, chrLength)

    i = 0
    while (i < maxNumGen):
        print "Iteration :", i
        population = decoder.decode(population, data)
        evol.append(brkga.getBestFitness(population)['fitness'])
        if numElite > 0:
            elite, nonelite = brkga.classifyIndividuals(population, numElite)
        else:
            elite = []
            nonelite = population
        if numMutants > 0:
            mutants = brkga.generateMutantIndividuals(numMutants, chrLength)
        else:
            mutants = []
        if numCrossover > 0:
            crossover = brkga.doCrossover(elite, nonelite, ro, numCrossover)
        else:
            crossover = []
        population = elite + crossover + mutants
        i += 1

    population = decoder.decode(population, data)
    bestIndividual = brkga.getBestFitness(population)
    print "Total execution time: ", time.time() - start
    print "Number of nurses working: ", bestIndividual['fitness']
    print "Solution", bestIndividual['solution']
    np.savetxt('results.out', bestIndividual['solution'], fmt='%d')
    if PLOTS_ENABLED:
        plt.plot(evol)
        plt.xlabel('number of generations')
        plt.ylabel('Fitness of best individual')
        #plt.axis([0, len(evol), 0, (2000 + 1) * 2000 / 2])
        plt.show()

# print bestIndividual


if __name__ == '__main__':
    main()
