from __future__ import division, print_function
from collections import namedtuple
from concorde._concorde import _CCutil_gettsplib, _CCtsp_solve_dat
from concorde.util import write_tsp_file, EDGE_WEIGHT_TYPES
import numpy as np
import uuid

ComputedTour = namedtuple('ComputedTour', ['tour', 'optimal_value', 'success', 'found_tour', 'hit_timebound'])

class TSPSolver(object):

    def __init__(self):
        self._data = None
        self._ncount = -1
        self.part_sol = [0]

    @classmethod
    def from_tspfile(cls, fname):
        ncount, data = _CCutil_gettsplib(fname)
        if data is None:
            raise RuntimeError("Error in loading {}".format(fname))
        self = cls()
        self._ncount = ncount
        self._data = data
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

    def neighbour(self):
        while len(self.part_sol) < len(self._data.x):
            self.nearest()
        return self.part_sol

    def CalD(self, cities):
        x = self._data.x[cities].reshape(len(cities), 1)
        y = self._data.y[cities].reshape(len(cities), 1)
        d = np.sqrt((x - x.T)**2 + (y - y.T)**2)
        return d/d.max()

    def CalJ(self, cities, d):
        J = np.zeros((len(cities)**2, len(cities)**2))
        for i in range(len(cities)):
            for j in range(len(cities)):
                I = i*len(cities) + j
                for ip in range(len(cities)):
                    for jp in range(len(cities)):
                        Ip = ip*len(cities)+jp
                        J[I, Ip] = (i==ip) + (j==jp)
                        if (jp==j-1) or (jp==j+1):
                            J[I, Ip] = J[I,Ip] + 0.5*d[i, ip]/4
        return J

    def arr2seq(self, arr):
        return np.argmax(arr, axis=1)

    def CalEne(self, cities, spin, d):
        S = spin.reshape(len(cities), len(cities))
        Ha_0 = (S.sum(axis=0) + len(cities) - 2)**2
        Ha_1 = (S.sum(axis=1) + len(cities) - 2)**2
        HA = Ha_0.sum() + Ha_1.sum()
        HB = 0
        for j in range(len(cities)-1):
            for i in range(len(cities)):
                for ip in range(len(cities)):
                    HB += d[i,ip]*(S[i, j]+1)*(S[ip, j+1]+1)
        return HA, HB

    def anneal(self, cities):
        n_step = 10001
        spins = np.zeros((len(cities)**2, n_step))
        spins[:,0] = 2*np.eye(len(cities)).reshape((len(cities)**2, 1))-1
        d = self.CalD(cities)
        J = self.CalJ(cities, d) - 5*np.eye(len(cities)**2)


    def sliding(self, pos, size_w):
        cities = self.part_sol[pos: pos+size_w+1]
        self.part_sol[pos: pos+size_w+1] = self.anneal(cities)


    def concorde(self, time_bound=-1, verbose=False, random_seed=0):
        name = str(uuid.uuid4().hex)[0:9]
        res = _CCtsp_solve_dat(self._ncount, self._data, name, time_bound, verbose, random_seed)
        return ComputedTour(*res)
