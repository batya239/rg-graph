#!/usr/bin/python
# -*- coding: utf8
import re
import os
import t_3_groups
import uncertainties

__author__ = 'dima'


DEPOT = None


def init_if_need():
    global DEPOT
    if DEPOT is None:
        DEPOT = dict()
        logs = filter(lambda s: "log3l" in s, os.listdir("./"))
        for g in t_3_groups.graphs:
            for f in logs:
                with open("./" + f) as ff:
                    ff1 = [x for x in ff]
                    for l in ff1:
                        if l[:-1] == str(g):
                            line = ff1[ff1.index(l) + 2]
                            parsed_value = re.sub("(-[\d]+:)", "\\1(", line.replace(",", "),").replace("}", ")}").replace("+/-", ","))
                            result_dict = eval(parsed_value)
                            result_dict = dict(map(lambda (k, v): (k, uncertainties.ufloat(*((v, 0.0) if isinstance(v, float) or len(v) == 1 else v))), result_dict.iteritems()))
                            DEPOT[g] = result_dict
                            break


def get(g):
    init_if_need()
    return DEPOT[g]