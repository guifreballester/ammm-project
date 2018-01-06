from data import data

config = {'chromosomeLength': data.get('numNurses') + data.get('numNurses') * data.get('hours'),
          'numIndividuals': 50, 'maxNumGen': 50,
          'eliteProp': 0.1, 'mutantProp': 0.2, 'inheritanceProb': 0.7}
