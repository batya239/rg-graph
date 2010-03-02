#!/usr/bin/python
# -*- coding:utf8

'''
Created on Mar 2, 2010

@author: mkompan
'''
import utils

def ShortPath(G,subG,tMomenta):
#для двуххвостого подграфа находит коротчайший путь для внешнего импульса, незатрагивающий линии с простыми импульсами.
# пердположительно работает только для phi^3
    Lines=G.lines
#    print Lines
    reducedsubG=set(subG.internal_lines)-set(tMomenta)
    subEL=list(subG.external_lines)
#    print subEL
    subN=subG.internal_nodes

    if Lines[subEL[0]].start in subN: 
        startNode=Lines[subEL[0]].start
    else: 
        startNode=Lines[subEL[0]].end
    
    if Lines[subEL[1]].end in subN: 
        endNode=Lines[subEL[1]].start
    else: 
        endNode=Lines[subEL[1]].end
#    print "======================"
#    print startNode,endNode
    flag=0
    path=[[startNode,],]
#    (set(G._Lines_nOfNode(startNode))& set(subEL)) - set(tMomenta)
#как бы рекурсивно составляем список путей
#выражение выше - список линий исходящих из данной вершины и содержащихся в подграфе и не являющихся простыми,т.е. по которым может протекать внешний импульс.
#вообще говоря написанное ниже кривовато и может работать только для фи3, когда будет более разумная структура данных можно будет переписать.
    while(flag==0):
        flag=1
        for curpath in path:
#            print "-------------"
#            print "curpath",curpath
            curNode=curpath[len(curpath)-1]
            if curNode<>endNode:
                outLines=set(subG.nodes[curNode].lines) - set(tMomenta)
                outNodes=[]
                for coutLines in outLines:
                    outNodes=outNodes+list(set(Lines[coutLines].Nodes())-set([curNode,]))

#                flag2=0
                for coutNodes in outNodes:
                    if coutNodes not in curpath:
                        path.append(curpath+[coutNodes,])
#                        flag2=1
                        flag=0
#               if flag2==1: path.remove(curpath)
                path.remove(curpath)

    minpathlen=1000000000000
    minpath=[]
    for idx in path:
        if len(idx)<minpathlen: 
            minpath=idx
            minpathlen=len(idx)
    return minpath


def GetMomentaIndex(G,Momenta):
# для данного расположения простых импульсов генерим число характеризующее хорошесть данного расположения
#1. если какой-то из подграф не содержит нужного количества простых импульсов: +1000000
    badSub=1000000
#2. если в сигмовый подграф втекает составной импульс: +1000
    badIn=1000
#3. если протечка внешнего импульса не оптимальна. +1 за каждую лишнюю линию. (для графа и подграфа разный штраф?)
    longInPath=1
#4. нет пути по которому можно пропустить внешний импульс +100? непонятно на сколько это важно
    badInPath=100
## сейчас за внеший импульс к диаграмме и внешний импульс в подграфе один и тот же штраф, т.к. делается это в одном цикле.
#5. нарушение законов киргхоффа +1000000
    badKirghoff=1000000


    result=0
    subGE=list(G.subgraphs)

    if len(G.external_lines)==2:
        # для определения оптимальности протечки внешнего для подграфа импульса, а заодно и в самой диаграмме
        tMomenta=list(Momenta)+[list(G.external_lines)[0],]
        subGE.append(G)
    else: 
        tMomenta=list(Momenta)



# строим протечку импульсов по киргхофу длф фи3!!!
    kMoment={}
    for tM in tMomenta:
        kMoment[tM]={tM:+1}
    ## в треххвостых втекающий импульс 0
    if len(G.external_lines)==3:
        for tM in G.external_lines:
            kMoment[tM]={}
    flag=0
    kRes=0
    while(flag==0 and kRes==0):
        flag=1
        for Node in G.internal_nodes:
            Lines=G.nodes[Node].lines
            NodeKirghoff={}
            cntLines=0
            Line=-1
            for idxLines in Lines:
                if G.lines[idxLines].end == Node:
                    sign=+1
                else:
                    sign=-1
                if idxLines in kMoment:
                    cntLines=cntLines+1
                    for idxM in kMoment[idxLines]:
                        if idxM in NodeKirghoff:
                            NodeKirghoff[idxM]= NodeKirghoff[idxM]+sign*kMoment[idxLines][idxM]
                        else:
                            NodeKirghoff[idxM]= sign*kMoment[idxLines][idxM]
                else:
                    Line=idxLines
            if len(Lines)==cntLines:
                for idxM in NodeKirghoff:
                    if NodeKirghoff[idxM]<>0: 
#                        print "bad Node:",Node, NodeKirghoff 
                        kRes=1
                        break
            elif len(Lines)-cntLines==1:
                kMoment[Line]={}
                if G.lines[Line].start==Node:
                    sign=1
                else:
                    sign=-1
                for idxM in NodeKirghoff:
                    if NodeKirghoff[idxM]<>0:
                        kMoment[Line][idxM]=sign*NodeKirghoff[idxM]
                flag=0

    for idxM in G.lines:
        if idxM not in kMoment: kRes=1                

    result=result+kRes*badKirghoff
    if kRes==1: return (result,kMoment)

# подсчет количества импульсов в подграфе.
    for subG in subGE:

        subEL=subG.external_lines
        #print  "subG ", subG.internal_lines,subG.external_lines, "tmomenta",tMomenta, "res ",result
        momentcount=0
# подсчет количества импульсов в подграфе.
        for i in tMomenta:
            if i in subG.internal_lines: 
                momentcount=momentcount+1
        if momentcount<>subG.NLoops():
            result=result+badSub
        if len(subEL)==2:
            sIn=0
#нам не нужно чтобы там была назначенная простая линия, может быть любая другая но простая. (ну я и кривоязык :) )
            for i in subEL:
                if len(kMoment[i])==1: sIn=1
                
            if sIn==0: result=result+badIn
            sPath=ShortPath(G,subG,tMomenta)
            if len(sPath)-2<0 :result=result+badInPath
            else: result=result+(len(sPath)-2)*longInPath
       
    return (result,kMoment)
    

def Generate(G):
    G.FindSubgraphs()
    minMomentIndex=10000000000000
    for i in utils.xUniqueCombinations(list(G.internal_lines),G.NLoops()):
        (curIndex,curkMoment)=GetMomentaIndex(G,i)
        if curIndex<minMomentIndex:
            minMomentIndex=curIndex
            minMoment=i
            kMoment=curkMoment
            if minMomentIndex==0: 
                break
            
    #print minMoment, minMomentIndex
    mapmoment={}
    if len(G.external_lines)==2:
        mapmoment[list(G.external_lines)[0]]="p"
    n=1
    for i in G.lines:
        if i in minMoment:
            mapmoment[i]="q"+str(n)
            n=n+1
    #   else:
    #      moment[i]=""
    moment={}
    for idxM in kMoment:
        tmpMoment=""
        for idxM2 in kMoment[idxM]:
    #      print idxM, idxM2, kMoment[idxM], mapmoment
            if kMoment[idxM][idxM2]==1:
                tmpMoment=tmpMoment+"+"+mapmoment[idxM2]
            elif kMoment[idxM][idxM2]==-1:
                tmpMoment=tmpMoment+"-"+mapmoment[idxM2]
            else:
                raise ValueError, "invalid moment factor %s" %kMoment[idxM][idxM2]
        moment[idxM]=tmpMoment
    return moment
