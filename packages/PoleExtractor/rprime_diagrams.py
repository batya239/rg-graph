__author__ = 'gleb'

import pole_extractor.rprime as rpr


print 'e112-22-e-'
print rpr.r_prime('e112-22-e-', 4)
print 'e12-e3-33--'
print rpr.r_prime('e12-e3-33--', 3)
print 'e12-33-44-5-5-e-'
print rpr.r_prime('e12-33-44-5-5-e-', 3)
print 'e12-e3-44-55-6-6-e-'
print rpr.r_prime('e12-e3-44-55-6-6-e-', 3)
print '####'
ls = ('e12-e3-33--', 'e12-23-3-e-', 'e12-e3-e4-44--', 'e12-e3-34-4-e-', 'e12-34-34-e-e-')
for l in ls:
    print "R'{" + l + "} = " + str(rpr.r_prime(l, 3))[1:-1]