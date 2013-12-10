# -*- coding: utf-8 -*-

from mmap import mmap,ACCESS_READ
from xlrd import open_workbook

aString = open('sokolov_diags_1.xls','rb').read()
wb = open_workbook(file_contents=aString)

diags = []
for s in wb.sheets():
    print 'Sheet:',s.name
    for row in range(s.nrows):
        values = []
        for col in range(s.ncols):
            values.append(s.cell(row,col).value)
            print ','.join(map(str,values))
        diags += [values]

print diags

f_mkompan = open("phi4_d2_s2-5loop-e4-100M-6loop-e2-1M.py")
data2 = eval(f_mkompan.read())
f_mkompan.close()

