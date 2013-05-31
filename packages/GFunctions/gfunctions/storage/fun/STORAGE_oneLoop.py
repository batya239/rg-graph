#!/usr/bin/python
# -*- coding: utf8

__author__ = 'daddy-bear'


def __oneLoop(graph):
    graphStateStr = str(graph.toGraphState())
    if graphStateStr[:graphStateStr.index("::")] != "e11-e-":
        return None
    vertexes = list(graph.vertexes() - set([graph.externalVertex]))
    edges = filter(lambda e: graph.externalVertex not in e.nodes,graph.edges(vertexes[0]))

    import gfunctions.lambda_number

    alpha = gfunctions.lambda_number.lambdaNumber(edges[0].colors)
    beta = gfunctions.lambda_number.lambdaNumber(edges[1].colors)
    return ("G(" + str(alpha) + ", " + str(beta) + ")", gfunctions.lambda_number.toRainbow(
        (alpha + beta - gfunctions.lambda_number.lambdaNumber((1, 1)))))




