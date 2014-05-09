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
try:
    if __IPYTHON__:
        from IPython.parallel import Client
        rc = Client()
        print rc.ids
        lview = rc.load_balanced_view()
        ipython = True
except NameError:
    ipython = False


def xindex():
    index = 0
    while True:
        yield index
        index += 1

## Берём все диаграммы
with open('../graphs/phi4/e4-4loop.txt') as f:
    diags = [d.split(' ')[0] for d in f.read().split('\n')[:-1] if d.split(' ')[-1] is not 'S']
## Отдаём в графин
diags = [graphine.Graph(gs_builder.graph_state_from_str(d.replace('-','|'))) for d in diags ]


conservations = []
for graph in diags:
    index = xindex()
    edges_map = dict([(index.next(), x) for x in graph.allEdges(nickel_ordering=True)])
    ## внутренние линии:
    internal_edges = dict(map(lambda x: (x[0], x[1].nodes), filter(lambda x: 1 if not x[1].is_external() else None, edges_map.items())))
    #print internal_edges
    conservations += [conserv.Conservations(internal_edges)]

## Количество законов сохранения разной длины:
fingerprints = [''.join(map(str,sorted(map(len,c)))) for c in conservations]
#print fingerprints

## Ищем повторяющиеся отпечатки
duplicates = [(f,i,conservations[i]) for i,f in enumerate(fingerprints) if fingerprints.count(f) > 1]
print "duplicates:",duplicates
dup_dict = {}
for d in duplicates:
    if d[0] in dup_dict:
        dup_dict[d[0]] += [diags[d[1]]]
    else:
        dup_dict[d[0]] = [diags[d[1]]]
print len(dup_dict), dup_dict

## Сравниваем с известными численными ответами
with open('../dvfu_cluster/res_best_6loops.txt') as res:
    results = eval(res.read())

## Вывод ответа
for d in dup_dict.values():
    for single_d in d:
        print single_d,results[str(single_d)[:-2]]
    print