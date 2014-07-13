#!/usr/bin/python
# -*- coding: utf8
__author__ = 'mkompan'

import numpy
import matplotlib.pyplot as plt


def xindex():
    i = 0
    while True:
        yield i
        i += 1


_INDEX = xindex()
_R_MIN = 10 ** -2
K = 0.01
K = 0.01
_RANDOM_AMPL = 0.00001
_RANDOM_AMPL = 0.2
VERTEX_SIZE = 70
LINE_SIZE = 20


class Vertex(object):
    def __init__(self, position, m=1, q=1, neighbours=None, fixed=False, **kwargs):
        self.pos = numpy.array(position, dtype=numpy.float)
        self.fixed = fixed
        self.new_pos = self.pos
        self.id = _INDEX.next()
        self.m, self.q = map(float, (m, q))
        self.options = kwargs
        self.neighbours = list() if neighbours is None else neighbours

    def __str__(self):
        return "(id=%s, %s, m=%s, q=%s, %s, %s)" % (
            self.id, self.pos, self.m, self.q, self.options, map(lambda x: x.id, self.neighbours))

    def __repr__(self):
        return str(self)

    def add_neighbour(self, vertex):
        self.neighbours.append(vertex)

    def shift(self, d_pos):
        self.pos = self.pos + d_pos

    def fix(self):
        self.fixed = True

    def f_repulsion_at_pos(self, pos):
        r = self._r(self.pos, pos)

        if r < _R_MIN:
            r = _R_MIN
        return self._r_vec(self.pos, pos) * self.q / r / r / r

    def f_attraction(self):
        f = numpy.zeros_like(self.pos)
        for n in self.neighbours:
            r_vec = self._r_vec(self.pos, n.pos)
            f += r_vec * (K)
        return f

    def get_property(self, property_name):
        if property_name in self.options:
            return self.options[property_name]
        else:
            return None

    def set_new_pos(self, f):
        self.new_pos = self.pos + f / self.m

    def apply_pos(self):
        if not self.fixed:
            self.pos = self.new_pos

    @staticmethod
    def link(vertex1, vertex2):
        vertex1.add_neighbour(vertex2)
        vertex2.add_neighbour(vertex1)

    @staticmethod
    def r(item1, item2):
        pos1 = item1.pos if isinstance(item1, Vertex) else item1
        pos2 = item2.pos if isinstance(item2, Vertex) else item2
        return Vertex._r(pos1, pos2)

    @staticmethod
    def _r_vec(pos1, pos2):
        return pos2 - pos1

    @staticmethod
    def _r(pos1, pos2):
        return ((pos1 - pos2) ** 2).sum() ** 0.5


def evaluate_vertices(v_list, n=100):
    for i in range(n):
        for v_ in v_list:
            f_repulsion = numpy.zeros_like(v_.pos)
            for v2_ in v_list:
                if v_ == v2_:
                    continue
                f_repulsion += v_.q * v2_.f_repulsion_at_pos(v_.pos)
            v_.set_new_pos(v_.f_attraction() + f_repulsion)
        for v_ in v_list:
            v_.apply_pos()


def create_edge(v1, v2, n=10, size=LINE_SIZE, **kwargs):
    r = Vertex._r_vec(v1.pos, v2.pos) / (n + 1)
    R = Vertex._r(v1.pos, v2.pos)
    q = 0.01 * R
    res = [v1, ]
    pos0 = v1.pos
    for i in range(1, n + 1):
        res.append(Vertex(pos0 + r * i, m=0.1, q=q, r=size, **kwargs))
        Vertex.link(res[-1], res[-2])
    Vertex.link(res[-1], v2)
    return res[1:]


def random_shift(v_list):
    for v in v_list:
        if not v.fixed:
            r = numpy.random.random(len(v.pos)) * _RANDOM_AMPL * 2 - _RANDOM_AMPL
            v.shift(r)
    return v_list


def constant_shift(v_list):
    v_ = v_list[0]
    r = numpy.random.random(len(v_.pos)) * _RANDOM_AMPL*5 * 2 - _RANDOM_AMPL*5
    for v in v_list:
        if not v.fixed:
            v.shift(r)
    return v_list

if __name__=="__main__":
    v1 = Vertex((0, 0), fixed=True, r=VERTEX_SIZE)
    v2 = Vertex((10, 0), fixed=True, r=VERTEX_SIZE)
    v3 = Vertex((5, 0), r=VERTEX_SIZE)
    v4 = Vertex((5, 0), r=VERTEX_SIZE)
    #v3 = Vertex((0, 1, 0))
    #Vertex.link(v1, v2)
    #Vertex.link(v1, v3)
    #Vertex.link(v2, v3)

    V = [v1, v2]
    V = [v1, v2, v3, v4]
    N = 5

    # V = V + create_edge(v1, v2, N) + create_edge(v1, v2, N)
    V = (V + create_edge(v1, v3, N)
         + create_edge(v1, v4, N)
         + create_edge(v1, v4, N)
         + create_edge(v2, v3, N)
         + create_edge(v2, v4, N)
         + create_edge(v3, v4, N)
         + create_edge(v3, v4, N))
    #V = V + create_edge(v1, v2) + create_edge(v1, v2)
    #V = V + create_edge(v1, v2)
    random_shift(V)

    evaluate_vertices(V, n=300)

    plt.figure(1)
    for v in V:
        plt.scatter(v.pos[0], v.pos[1], s=v.get_property('r'))

    evaluate_vertices(V, n=300)

    plt.figure(2)
    for v in V:
        plt.scatter(v.pos[0], v.pos[1], s=v.get_property('r'))
    plt.show()