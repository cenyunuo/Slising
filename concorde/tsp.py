from __future__ import division, print_function
from collections import namedtuple
from concorde._concorde import _CCutil_gettsplib, _CCtsp_solve_dat
from copy import deepcopy
from scipy.special import expit
import numpy as np
import uuid
import math

ComputedTour = namedtuple('ComputedTour', ['tour', 'optimal_value', 'success', 'found_tour', 'hit_timebound'])

class TSPSolver(object):

    def __init__(self):
        self._data = None
        self._ncount = -1
        self.part_sol = [0]
        self.box_length = 0.4
        self.box_step = 0.1
        self.box_x = 0.0
        self.box_y = 0
        self.limit = 1

    @classmethod
    def from_tspfile(cls, fname):
        ncount, data = _CCutil_gettsplib(fname)
        if data is None:
            raise RuntimeError("Error in loading {}".format(fname))
        self = cls()
        self._ncount = ncount
        self._data = data
        tmp = np.array([data.x,data.y])
        self.data_x = (data.x-tmp.min()) / (tmp.max()-tmp.min())
        self.data_y = (data.y-tmp.min()) / (tmp.max()-tmp.min())
        return self

    def nearest(self):
        current = self.part_sol[-1]
        x = self._data.x[current]
        y = self._data.y[current]
        tbd = list(set(range(len(self._data.x))) - set(self.part_sol))
        next = tbd[0]
        x_ = self._data.x[next]
        y_ = self._data.y[next]
        d = (x-x_)**2 + (y-y_)**2
        for i in tbd:
            x_ = self._data.x[i]
            y_ = self._data.y[i]
            d_ = (x-x_)**2 + (y-y_)**2
            if d_ <= d:
                d = d_
                next = i
        self.part_sol.append(next)

    def eva_tour(self, tour):
        d = 0
        for i in range(len(tour)):
            j = tour[i]
            k = tour[(i+1)%len(tour)]
            d += math.sqrt((self.data_x[j] - 
                            self.data_x[k])**2 + 
                        (self.data_y[j] - 
                            self.data_y[k])**2)
        return d

    def neighbour(self):
        while len(self.part_sol) < len(self._data.x):
            self.nearest()
        return self.part_sol

    def CalD(self, cities):
        x = self._data.x[cities].reshape(len(cities), 1)
        y = self._data.y[cities].reshape(len(cities), 1)
        d = np.sqrt((x - x.T)**2 + (y - y.T)**2)
        return d/d.max()

    def sliding(self):
        Flag = True
        self.box_x += self.box_step
        if (self.box_x + self.box_length > self.limit):
            self.box_x = 0
            self.box_y += self.box_step
        if (self.box_y + self.box_length > self.limit):
            Flag = False
            self.box_x = 0
            self.box_y = 0
        return Flag

    def selecting(self):
        tmp = []
        for i in range(len(self.part_sol)):
            j = self.part_sol[i]
            if (self.box_x <= self.data_x[j] <= self.box_x+self.box_length) and (self.box_y <= self.data_y[j] <= self.box_y+self.box_length):
                tmp.append([j, i, self.data_x[j], self.data_y[j]])
        return tmp

    def recognize_lines(self):
        points = self.selecting()
        try:
            tmp_1 = [points[0][1]]
        except:
            tmp_1 = []
        tmp_2 = []
        for i in range(len(points)-1):
            if points[i][1]+1 == points[i+1][1]:
                tmp_1.append(points[i+1][1])
            else:
                tmp_2.append(tmp_1)
                tmp_1 = [points[i+1][1]]
        tmp_2.append(tmp_1)
        return tmp_2 # indexs of the selected points

    def longest_lines(self):
        lines = self.recognize_lines()
        lines.sort(key = len)
        return lines

    def cost_ins(self, d, prev, next, ins):
        return d[prev, ins] + d[ins, next] - d[prev, next]

    def ins_1(self):
        line = self.longest_lines()[-1]
        init = self.part_sol[line[0] - 1]
        end = self.part_sol[(line[-1] + 1) % len(self.part_sol)]
        tbd = self.part_sol[line[0] : line[-1] + 1]
        d = self.CalD([init] + tbd + [end])
        d[0, -1] = -100
        d[-1, 0] = -100
        mask = np.zeros(len(line)+2)
        tour = [0, len(line) + 1]
        mask[tour] = True
        for i in range(len(line)):
            feas = (mask==0)
            feas_ind = np.flatnonzero(mask == 0)
            a = feas_ind[d[np.ix_(feas, ~feas)].min(1).argmax()]
            mask[a] = True
            ins_ind = np.argmin(self.cost_ins(d,tour,np.roll(tour, -1), a))
            tour.insert(ins_ind + 1, a)
        new_tour = np.array(tbd)[np.array(tour[1:-1])-1].tolist()
        tmp = deepcopy(self.part_sol)
        tmp[line[0] : line[-1] + 1] = new_tour
        if self.eva_tour(tmp) < self.eva_tour(self.part_sol):
            self.part_sol = tmp
        return [init] + new_tour + [end]

    def ins_2(self):
        longest_line = self.longest_lines()[-1]
        second_longest_line = self.longest_lines()[-2]
        if longest_line[0] > second_longest_line[0]:
            line_1 = second_longest_line
            line_2 = longest_line
        else:
            line_1 = longest_line
            line_2 = second_longest_line
        prev_1 = self.part_sol[line_1[0] - 1]
        prev_2 = self.part_sol[line_1[0] - 1]
        next_1 = self.part_sol[(line_1[-1] + 1)]
        next_2 = self.part_sol[(line_2[-1] + 1) % len(self.part_sol)]
        if line_1[0]-1 == -1:
            fixed_1 = []
        else:
            fixed_1 = self.part_sol[:line_1[0]]
        tbd_1 = self.part_sol[line_1[0] : line_1[-1] + 1]
        fixed_2 = self.part_sol[line_1[-1] + 1: line_2[0]]
        tbd_2 = self.part_sol[line_2[0] : line_2[-1] + 1]
        fixed_3 = self.part_sol[line_2[-1] + 1 :]

        d = self.CalD([prev_1] + tbd_1 + [next_1] + [prev_2] + tbd_2 + [next_2])
        d[0, -1] = -100
        d[-1, 0] = -100
        d[len(tbd_1)+1, len(tbd_1)+2] = -100
        d[len(tbd_1)+1, len(tbd_1)+2] = -100
        mask = np.zeros(len(line_1)+len(line_2)+4)
        tour = [0, len(line_1)+1, len(line_1)+2, len(line_1)+len(line_2)+3]
        mask[tour] = True
        for i in range(len(line_1)+len(line_2)):
            feas = (mask==0)
            feas_ind = np.flatnonzero(mask == 0)
            a = feas_ind[d[np.ix_(feas, ~feas)].min(1).argmin()]
            mask[a] = True
            ins_ind = np.argmin(self.cost_ins(d,tour,np.roll(tour, -1), a))
            tour.insert(ins_ind + 1, a)
        new_tour = np.array([prev_1] + tbd_1 + [next_1] + [prev_2] + tbd_2 + [next_2])[np.array(tour)].tolist()
        cut = new_tour.index(next_1)
        tour_1 = new_tour[1 : cut]
        tour_2 = new_tour[cut+2 : -1]
        if self.eva_tour(fixed_1 + tour_1 + fixed_2 + tour_2 + fixed_3) < self.eva_tour(self.part_sol):
            self.part_sol = fixed_1 + tour_1 + fixed_2 + tour_2 + fixed_3
        return [prev_1] + tour_1 + [next_1], [prev_2] + tour_2 + [next_2]
        #return fixed_1 + tour_1 + fixed_2 + tour_2 + fixed_3

    def concorde(self, time_bound=-1, verbose=False, random_seed=0):
        name = str(uuid.uuid4().hex)[0:9]
        res = _CCtsp_solve_dat(self._ncount, self._data, name, time_bound, verbose, random_seed)
        return ComputedTour(*res)
