# -*- coding: utf-8 -*-
## идентифицируем диаграммы в расчётах Соколова
## каждой диаграмме сопоставляем номенклатуру Никеля

from xlrd import open_workbook
import sympy
import graphine, graph_state

def symmetryCoefficient(nickel):
    graph = graphine.Graph(graph_state.GraphState.fromStr("%s::" % nickel))
    edges = graph.allEdges()
    unique_edges = dict()
    for idx in edges:
        if idx in unique_edges:
            unique_edges[idx] += 1
        else:
            unique_edges[idx] = 1
    C = sympy.factorial(len(graph.edges(graph.externalVertex))) / len(graph.toGraphState().sortings)

    for idxE in unique_edges:
        C = C / sympy.factorial(unique_edges[idxE])
    return C


aString = open('sokolov_diags.xls','rb').read()
wb = open_workbook(file_contents=aString)

diags = []
for s in wb.sheets():
    print 'Sheet:',s.name
    for row in range(s.nrows):
        values = []
        for col in range(s.ncols):
            values.append(s.cell(row,col).value)
        diags += [values]

f_mkompan = open("phi4_d2_s2-5loop-e4-100M-6loop-e2-1M.py")
mkompan = eval(f_mkompan.read())
f_mkompan.close()

matched = []
for a in diags:
    n = int(a[3][-1:])+1
    for d,c in mkompan.items():
        if abs(c[0][0]-((-1)**n)*a[0]) < c[1][0] and abs(symmetryCoefficient(d) - a[2])< 0.01:
            matched += [d]
            #print d
            #print "mkompan:",[-c[0][0],c[1][0]]
            #print "Sokolov:",a
            #print
            #count +=1
            mkompan.pop(d)
        if a[3] == '5-7-2' and d == 'e112-23-e4-444--':
            print "mkompan:",[-c[0][0],c[1][0]]
            print "Sokolov:",a
            print ((-1)**n)*a[0], c[0][0],n,symmetryCoefficient(d)

#print matched
print "Matches:",len(matched)
