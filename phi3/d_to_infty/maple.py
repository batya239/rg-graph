#! /usr/bin/python
#! encoding: utf8

__author__ = 'kirienko'

import pexpect # <-- see docs here: http://pexpect.readthedocs.org/en/stable/

def maple(expr):
    """
    Quick and dirty Maple interface.
    Executes expression 'expr' in Maple and returns the result as a string.
    Inspired by SAGE:
    see https://github.com/sagemath/sage/blob/master/src/sage/interfaces/maple.py 
    """
    __maple_iface_opts = [
            'screenwidth=infinity',
            'errorcursor=false',]
    MW = 'maple -t -c "interface({})"'.format(','.join(__maple_iface_opts))
    child = pexpect.spawn(MW)
    child.expect('#-->')
    assumption = "assume(%s):"%", ".join(["k%s>1"%i for i in xrange(5)])
    child.sendline(assumption)
    child.expect('#-->')
    child.sendline(expr)
    child.expect('#-->')
    out = child.before
    out = out[out.find(';')+1:].strip()
    out = ''.join(out.split('\r\n'))
    return out

if __name__ == "__main__":
    cmd = "2+2;"
    out = maple(cmd)
    print cmd[:-1] + " = " + out 
