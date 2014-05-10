__author__ = 'yura'

test = [[(1,'a'),(1,'b')],[(1,'a'),(2,'b')],[(2,'c'),(2,'d'),(3,'e')],[(3,'e'),(3,'f'),(3,'g'),(4,'h'),(4,'h')]]
print "test =",test
#old_0 = [[y[0] for y in x] for x in test]
#old_1 = [[y[1] for y in x] for x in test]
#print "old_0 =",old_0
#print "old_1 =",old_1
new = []
for l in test:
    while l:
        a = l.pop(0)
        #print "a =",a," current l =",l
        #print "[x[0] for x in l] =", [x[0] for x in l]
        if [x[0] for x in l].count(a[0])>0:
            new += [[a[1]]]
            #print "l.count(a[0]) =",[x[0] for x in l].count(a[0])
            for i in range([x[0] for x in l].count(a[0])):
                #new[-1] += [a[1]]
                idx = [x[0] for x in l].index(a[0])
                new[-1] += [l[idx][1]]
                #print "l =",l, "\t a =",a, "\tl.index(a) ="
                l.pop([x[0] for x in l].index(a[0]))

print "new =",new

def __separate(old):
    """
    old --> new
    old = [[1, 1, 0], [1, 2], [2, 2, 3], [3, 3, 3, 4, 4, 5, 5, 5, 5]]
    new = [[1, 1], [2, 2], [5, 5, 5, 5], [4, 4], [3, 3, 3]]
    """
    new = []
    for l in old:
        while l:
            a = l.pop()
            if l.count(a)>0:
                new += [[a]]
                for i in range(l.count(a)):
                    new[-1] += [a]
                    l.pop(l.index(a))
    return new
