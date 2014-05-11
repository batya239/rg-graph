#!/usr/bin/python
# -*- coding: utf8
__author__ = 'kirienko'

import graphine
from graph_state_builder_static import gs_builder
import conserv

"""
Поиск диаграмм, имеющих одинаковое фейнмановское представление
"""

## Ipython parallel part -- for future

def xindex():
    index = 0
    while True:
        yield index
        index += 1

def set_to_list(s):
    t = map(set,s)
    return [x for x in map(list,t)]
def abc(s):
    """
    Flatten list of lists 's' and return its different elements
    """
    tmp = []
    for x in s:
        tmp += x
    return set(tmp)
def fp2(t):
    """
    Ищем сколько раз каждая конкретная линия входит в закон сохр. длиной L
    """
    t = set_to_list(t)
    return sorted([sorted([len(x) for x in t if x.count(c)>0 ]) for c in abc(t)])

## Берём все диаграммы
with open('../graphs/phi4/e4-6loop.txt') as f:
    diags = [d.split(' ')[0] for d in f.read().split('\n')[:-1] if d.split(' ')[-1] is not 'S']
## Отдаём в графин
diags = [graphine.Graph(gs_builder.graph_state_from_str(d.replace('-','|'))) for d in diags ]
print "Total number of diags:", len(diags)

conservations = []
for graph in diags:
    index = xindex()
    edges_map = dict([(index.next(), x) for x in graph.allEdges(nickel_ordering=True)])
    ## внутренние линии:
    internal_edges = dict(map(lambda x: (x[0], x[1].nodes), filter(lambda x: 1 if not x[1].is_external() else None, edges_map.items())))
    #print internal_edges
    conservations += [conserv.Conservations(internal_edges)]

## Количество законов сохранения разной длины:
fingerprints = [sorted(map(len,c)) for c in conservations]
#print "fingerprints:", fingerprints

## Ищем повторяющиеся отпечатки
duplicates = [(f,i,conservations[i]) for i,f in enumerate(fingerprints) if fingerprints.count(f) > 1]
#print "duplicates:",duplicates
dup_dict = {}
for d in duplicates:
    if str(d[0]) in dup_dict:
        dup_dict[str(d[0])] += [(fp2(d[2]), diags[d[1]])]
    else:
        dup_dict[str(d[0])]  = [(fp2(d[2]), diags[d[1]])]
#print len(dup_dict), dup_dict

def separate(old):
    """
    old --> new
    old = [[(1, 'a'), (1, 'b')], [(1, 'a'), (2, 'b')], [(2, 'c'), (2, 'd'), (3, 'e')], [(3, 'e'), (3, 'f'), (3, 'g'), (4, 'h'), (4, 'h')]]
    new = [['a', 'b'], ['c', 'd'], ['e', 'f', 'g'], ['h', 'h']]
    """
    new = []
    for l in old:
        while l:
            a = l.pop(0)
            if [x[0] for x in l].count(a[0])>0:
                new += [[a[1]]]
                for i in range([x[0] for x in l].count(a[0])):
                    idx = [x[0] for x in l].index(a[0])
                    new[-1] += [l[idx][1]]
                    l.pop([x[0] for x in l].index(a[0]))
    return new

## Второй этап сравнения:
#e1, e2 = duplicates[0][2], duplicates[1][2]
#print "fingerprints2(t1):", fp2(e1)
#print "fingerprints2(t2):", fp2(e2)
#print fp2(e1) == fp2(e2)
## ----------------------

## Сравниваем с известными численными ответами
with open('../dvfu_cluster/res_best_6loops.txt') as res:
    results = eval(res.read())

final = separate(dup_dict.values())
## Вывод ответа
ring = 0
print
for d in final:
    print " = ".join(map(lambda x: str(x)[:-2],d))
    for single_d in d:
        #print str(single_d)[:-2],#results[str(single_d)[:-2]]
        ring += 1
    #print
    ring -= 1 ## I leave one diag from each group

print "ring =", ring