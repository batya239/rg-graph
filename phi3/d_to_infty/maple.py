#! /usr/bin/python
# ! encoding: utf8
import pexpect  # <-- see docs here: http://pexpect.readthedocs.org/en/stable/

__author__ = 'kirienko'


def maple(expr, Digits=10):
    """
    Quick and dirty Maple interface.
    Executes expression 'expr' in Maple and returns the result as a string.
    Inspired by SAGE:
    see https://github.com/sagemath/sage/blob/master/src/sage/interfaces/maple.py 
    """
    __maple_iface_opts = [
        'screenwidth=infinity',
        'errorcursor=false']
    MW = 'maple -t -c "interface({})"'.format(','.join(__maple_iface_opts))
    child = pexpect.spawn(MW)
    child.expect('#-->')
    assumption = "assume(%s):" % ", ".join(["k%s>1" % i for i in xrange(5)])
    child.sendline(assumption)
    child.expect('#-->')
    if Digits != 10:
        child.sendline('Digits = %d:' % Digits)
        child.expect('#-->')
    child.sendline(expr)
    child.expect('#-->', timeout=None)
    out = child.before
    if len(out.split(';')) > 1:
        out = out[out.find(';') + 1:].strip()
        out = ''.join(out.split('\r\n'))
        return out
    elif len(out.split(';')) == 1 and expr[:9] == 'simplify(':
        print "\t\t*** Simplification E R R O R ***\nExpression:\n"+expr+"\n*** END OF ERROR LOG"
        return expr[8:-1]
    else:
        return "\n\t\t*** M A P L E ()  E R R O R ***\nExpression:\n"+expr+"\nResult:\n"+out+"\n*** END OF ERROR LOG"


if __name__ == "__main__":
    cmd = "2+2;"
    out = maple(cmd)
    print cmd[:-1] + " = " + out
