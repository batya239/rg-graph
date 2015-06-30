#!/usr/bin/python
# -*- coding: utf8

__author__ = 'dima'

import swiginac
import hardcoded
from rggraphenv import symbolic_functions
from rggraphutil import zeroDict


class Entry(object):
    def __add__(self, other):
        if other is None:
            return self
        assert isinstance(other, (Entry, swiginac.numeric))
        if isinstance(other, swiginac.numeric):
            other = Number(other)
        self_c = self.entries if isinstance(self, Add) else (self, )
        other_c = other.entries if isinstance(other, Add) else (other, )
        return Add(self_c + other_c)

    __radd__ = __add__

    def __sub__(self, other):
        assert isinstance(other, (Entry, swiginac.numeric))
        if isinstance(other, swiginac.numeric):
            other = Number(other)
        other *= Number(swiginac.numeric(-1))
        self_c = self.entries if isinstance(self, Add) else (self, )
        other_c = other.entries if isinstance(other, Add) else (other, )
        return Add(self_c + other_c)

    def __neg__(self):
        return Neg(self)

    def __mul__(self, other):
        if other is None:
            return self
        assert isinstance(other, (Entry, swiginac.numeric, int)), type(other)
        if isinstance(other, swiginac.numeric):
            other = Number(other)
        if isinstance(other, int):
            other = Number(symbolic_functions.cln(other))
        if isinstance(other, Mul):
            return NotImplemented
        return Mul(self, other)

    def __div__(self, other):
        assert isinstance(other, int)
        return self * (symbolic_functions.CLN_ONE / symbolic_functions.cln(other))

    __rmul__ = __mul__

    def __eq__(self, other):
        return self.as_ginac().is_equal(other.as_ginac())

    def as_ginac(self):
        raise NotImplementedError()

    def __hash__(self):
        return 1

    def collect_kr1(self, collector):
        raise AssertionError()

    def collect_values(self, collector):
        raise AssertionError()

    def eval_with_tau(self):
        raise NotImplementedError()

    def eval_with_error(self):
        raise NotImplementedError()


class Neg(Entry):
    def __init__(self, a):
        self.a = a

    def __str__(self):
        return "-%s" % self.a

    __repr__ = __str__

    def as_ginac(self):
        return - self.a.as_ginac()

    def collect_kr1(self, collector):
        self.a.collect_kr1(collector)

    def collect_values(self, collector):
        self.a.collect_values(collector)

    def eval_with_tau(self):
        return - self.a.eval_with_tau()

    def eval_with_error(self):
        res = zeroDict()
        for k, v in self.a.eval_with_error().iteritems():
            res[k] = -v
        return res


class KR1(Entry):
    GINAC_IDX = -1
    GINAC_CACHE = dict()

    def __init__(self, graph, operation=None):
        self.graph = graph
        self.operation = "log" if operation is None else operation

    def __str__(self):
        return "KR1[\"%s\"][%s]" % (self.graph, self.operation)

    __repr__ = __str__

    def __hash__(self):
        return hash(self.as_ginac())

    def __eq__(self, other):
        return self.as_ginac() is other.as_ginac()

    def as_ginac(self):
        pair = (self.graph.to_graph_state(), self.operation)
        if pair in KR1.GINAC_CACHE:
            return KR1.GINAC_CACHE[pair]
        KR1.GINAC_IDX += 1
        var = symbolic_functions.var("kr1_%s" % KR1.GINAC_IDX)
        KR1.GINAC_CACHE[pair] = var
        return var

    def collect_kr1(self, collector):
        collector.add(self)

    def collect_values(self, collector):
        pass

    def eval_with_tau(self):
        r = hardcoded.kr1(self.graph, self.operation)
        result = symbolic_functions.CLN_ZERO
        for k, v in r.items():
            result += v * symbolic_functions.e ** k
        return result

    def eval_with_error(self):
        res = dict()
        for k, v in hardcoded.kr1(self.graph, self.operation).iteritems():
            res[k] = v.evalf().to_double()
        return res


class Number(Entry):
    def __init__(self, num):
        self.num = num

    def __str__(self):
        return str(self.num)

    __repr__ = __str__

    def as_ginac(self):
        return self.num

    def collect_kr1(self, collector):
        pass

    def collect_values(self, collector):
        pass

    def eval_with_tau(self):
        return self.num

    def eval_with_error(self):
        return {0: self.num.evalf().to_double()}


class Mul(Entry):
    def __init__(self, *entries):
        for e in entries:
            assert isinstance(e, Entry)
        self.entries = tuple(entries)

    def __mul__(self, other):
        if isinstance(other, int):
            other = Number(symbolic_functions.cln(other))
        elif isinstance(other, swiginac.numeric):
            other = Number(other)
        return Mul(*(self.entries + (other, )))

    __rmul__ = __mul__

    def __str__(self):
        return "*".join(map(lambda e: "(%s)" % e, self.entries))

    __repr__ = __str__

    def as_ginac(self):
        return reduce(lambda a, b: a * b.as_ginac(), self.entries, symbolic_functions.CLN_ONE)

    def collect_kr1(self, collector):
        for e in self.entries:
            e.collect_kr1(collector)

    def collect_values(self, collector):
        for e in self.entries:
            e.collect_values(collector)

    def eval_with_tau(self):
        return reduce(lambda a, b: a * b.eval_with_tau(), self.entries, symbolic_functions.CLN_ONE)

    def eval_with_error(self):
        res = None
        for e in self.entries:
            if res is None:
                res = e.eval_with_error()
            else:
                curr_res = zeroDict()
                for k, v in res.iteritems():
                    for k2, v2 in e.eval_with_error().iteritems():
                        curr_res[k + k2] += v * v2
                res = curr_res
        assert res is not None
        return res


class Add(Entry):
    def __init__(self, entries):
        self.entries = entries

    def __str__(self):
        return "+".join(map(lambda e: "(%s)" % e, self.entries))

    __repr__ = __str__

    def as_ginac(self):
        return reduce(lambda a, b: a + b.as_ginac(), self.entries, symbolic_functions.CLN_ZERO)

    def collect_kr1(self, collector):
        for e in self.entries:
            e.collect_kr1(collector)

    def collect_values(self, collector):
        for e in self.entries:
            e.collect_values(collector)

    def eval_with_tau(self):
        return reduce(lambda a, b: a + b.eval_with_tau(), self.entries, symbolic_functions.CLN_ZERO)

    def eval_with_error(self):
        res = zeroDict()
        for e in self.entries:
            for k, v in e.eval_with_error().items():
                res[k] += v
        return res


Unit = Number(symbolic_functions.CLN_ONE)