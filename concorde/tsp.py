# -*- coding: utf-8 -*-
from __future__ import division, print_function

from collections import namedtuple
import uuid

from concorde._concorde import _CCutil_gettsplib, _CCtsp_solve_dat
from concorde.util import write_tsp_file, EDGE_WEIGHT_TYPES

ComputedTour = namedtuple('ComputedTour', [
    'tour', 'optimal_value', 'success', 'found_tour', 'hit_timebound'
])


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

    def __str__(self):
        if self._data is None:
            return "Uninitialized TSPSolver"
        else:
            return "TSPSolver with {} nodes".format(self._ncount)

    def concorde(self, time_bound=-1, verbose=False, random_seed=0):
        name = str(uuid.uuid4().hex)[0:9]
        res = _CCtsp_solve_dat(
            self._ncount, self._data, name,
            time_bound, verbose, random_seed
        )
        return ComputedTour(*res)
