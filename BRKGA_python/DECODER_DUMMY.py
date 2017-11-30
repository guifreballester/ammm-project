import numpy as np

def decode(population, data):
    for ind in population:
        ind['solution']=ind['chr']
        res=np.multiply(ind['chr'],range(len(ind['chr'])))
        ind['fitness']=sum(res)
    return(population)
    

