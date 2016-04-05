#! /usr/bin/python
# ! encoding: utf8

import os
import pexpect  # <-- see docs here: http://pexpect.readthedocs.org/en/stable/
import tempfile

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
    k_s = ", ".join(["k%s>1" % i for i in xrange(5)])
    a_s = ", ".join(["a%s>0" % i for i in xrange(5)])
    assumption = "assume(%s, %s):" % (k_s, a_s)

    ###
    # If expression is huge, put it in a temporary file

    #if len(expr) > 16380:
    fd_source = tempfile.NamedTemporaryFile(prefix='tmp_rggraph_maple', delete=False)
    fd_dest = tempfile.NamedTemporaryFile(prefix='tmp_rggraph_maple', delete=False)
    fd_source.write(assumption + "\n")
    if Digits != 10:
        fd_source.write('Digits = %d:' % Digits)
    fd_source.write(expr + '\n')
    fd_source.close()
    fd_dest.close()
    os.system('maple -t -q %s > %s' % (fd_source.name, fd_dest.name))
    with open(fd_dest.name) as fd:
        out = fd.read().strip()
    os.remove(fd_source.name)
    os.remove(fd_dest.name)
    # print "sent/received symbols: %d / %d" % (len(expr), len(out))
    """
    else:
        child = pexpect.spawn(MW)
        child.expect('#-->')
        child.sendline(assumption)
        child.expect('#-->')
        if Digits != 10:
            child.sendline('Digits = %d:' % Digits)
            child.expect('#-->')
        sended = child.sendline(expr)
        child.expect('#-->', timeout=None)
        out = child.before
        if len(out.split(';')) > 1:
            out = out[out.find(';') + 1:].strip()
            out = ''.join(out.split('\r\n'))
            # print "sent/received symbols: %d / %d" % (sended, len(out))
        elif len(out.split(';')) == 1 and expr[:9] == 'simplify(':
            print "\t\t*** Simplification E R R O R ***\nExpression:\n"+expr+"\n*** END OF ERROR LOG"
        else:
            return "\n\t\t*** M A P L E ()  E R R O R ***\nExpression:\n"+expr+"\nResult:\n"+out+"\n*** END OF ERROR LOG"
    """
    #if len(expr) - 10 < len(out) and expr[:9] == 'simplify(':
    #    out = expr[8:-1]
    return out

if __name__ == "__main__":
    cmd = "2+2;"
    out = maple(cmd)
    print cmd[:-1] + " = " + out
