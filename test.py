from concorde.tsp import TSPSolver
from concorde.tests.data_utils import get_dataset_path
from matplotlib import pyplot as plt
import os
import math

def vis_tour(solver, tour):
    for i in range(len(tour)):
        j = tour[i]
        k = tour[(i+1)%len(tour)]
        plt.scatter(solver._data.x[j], solver._data.y[j], color='red',s=32)
        plt.plot(solver._data.x[[j,k]], solver._data.y[[j,k]], color='blue')
    plt.show()

def eva_tour(solver, tour):
    d = 0
    for i in range(len(tour)):
        j = tour[i]
        k = tour[(i+1)%len(tour)]
        d += math.sqrt((solver._data.x[j] - 
                        solver._data.x[k])**2 + 
                       (solver._data.y[j] - 
                        solver._data.y[k])**2)
    return d

if __name__ == "__main__":
    # for dataset in ["rd100", "lin318", "d657", "pr1002"]
    fname = get_dataset_path("lin318")
    solver = TSPSolver.from_tspfile(fname)
    sol_init = solver.neighbour()
    sol_bk = solver.concorde().tour
    print(eva_tour(solver, sol_init)/eva_tour(solver, sol_bk))
    os.system('rm -rf *.res')
    os.system('rm -rf *.sol')