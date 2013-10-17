__author__ = 'gleb'


def unique(seq):
    seen = set()
    return [x for x in seq if str(x) not in seen and not seen.add(str(x))]


def unite(seq):
    """
    turns sequence of sequences in sequence of elements of sequences, e.g.
    [[1, 2, 3], [4, 5], [6,]] -> [1, 2, 3, 4, 5, 6]
    """
    result = []
    for i in range(len(seq)):
        result.extend(seq[i])
    return result


def merge_map(func, lst):
    tmp = map(func, lst)
    result = []
    while tmp:
        result.extend(tmp.pop(0))
    return result


def merge_filter(func, lst):
    tmp = filter(func, lst)
    result = []
    while tmp:
        result.extend(tmp.pop(0))
    return result