__author__ = 'gleb'

import multiprocessing
from pole_extractor import utils

jobs = []


def put_d(t, l, res):
    res.put(utils.get_diagrams(t, l))


q = multiprocessing.Queue()
for t in (2, 3):
    for l in (1, 2, 3, 4):
        jobs.append(multiprocessing.Process(target=put_d, args=(t, l, q)))

map(lambda x: x.start(), jobs)
map(lambda x: x.join(), jobs)
print q.get()