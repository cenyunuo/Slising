from concorde.tsp import TSPSolver
from concorde.tests.data_utils import get_dataset_path
from matplotlib import pyplot as plt
from matplotlib.patches import Rectangle
import os
import math

def vis_tour(solver, tour):
    for i in range(len(tour)-1):
        j = tour[i]
        k = tour[(i+1)%len(tour)]
        plt.plot(solver.data_x[[j,k]], solver.data_y[[j,k]], color='green', linewidth=5)

def vis_windows(solver, tour, loss):
    points = solver.selecting()
    for i in range(len(tour)):
        j = tour[i]
        k = tour[(i+1)%len(tour)]
        plt.scatter(solver.data_x[j], solver.data_y[j], color='red',s=32)
        plt.plot(solver.data_x[[j,k]], solver.data_y[[j,k]], color='blue')
    for k in range(len(points)):
        i = points[k]
        j = i[0]
        plt.scatter(solver.data_x[j], solver.data_y[j], color='orange', s=32)
        plt.annotate(i[1], xy = (solver.data_x[j], solver.data_y[j]),
                    xytext = (solver.data_x[j], solver.data_y[j]))
    ax = plt.gca()
    rect = Rectangle((solver.box_x, solver.box_y),
                      solver.box_length, solver.box_length, linewidth=2, edgecolor='orange', facecolor='none')
    ax.add_patch(rect)
    plt.title(loss/eva_tour(solver, solver.part_sol))

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
    fname = get_dataset_path("rd100")
    solver = TSPSolver.from_tspfile(fname)
    sol_init = solver.neighbour()
    loss = eva_tour(solver, sol_init)
    points = solver.selecting()
    Flag = True
    while Flag:
        if len(solver.longest_lines())>1:
            new_tour = solver.ins_2()
            vis_tour(solver, new_tour[0])
            vis_tour(solver, new_tour[1])
        elif len(solver.longest_lines()[-1])>1:
            new_tour = solver.ins_1()
            vis_tour(solver, new_tour)
        vis_windows(solver, sol_init, loss)
        Flag = solver.sliding()
        print(new_tour)
        plt.show()
    #sol_bk = solver.concorde().tour
    os.system('rm -rf *.res')
    os.system('rm -rf *.sol')
