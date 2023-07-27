#!/usr/bin/python3
from pulp import *

def relaxed_program(a,ug,dg,demands):
    nodes = list(ug.nodes)  # the list of nodes
    edges = list(ug.edges)  # the list of undirected edges
    d_edges = list(dg.edges)    # the list of directed edges

    prob = LpProblem("Maximin problem",LpMaximize)

    # define the variables of the problem
    # f^i_{(u,v)}
    f_i_uv = list()
    for d in demands:
        for e in d_edges:
            f_i_uv.append((d,e))  # should be a list of tuple

    lp_f_i_uv = LpVariable.dicts("Flow f_i_uv",f_i_uv,0,None,cat="Continuous")

    # f^i
    f_i = list()
    for d in demands:
        f_i.append(d)

    lp_f_i = LpVariable.dicts("Flow f_i",f_i,0,None,cat="Continuous")

    # m
    m = LpVariable("m",0,None,cat="Continuous")

    # the objective function
    prob += a*m + (1-a)*lpSum([lp_f_i[d] for d in demands])

    # the first constraint
    for d in demands:
        temp_1 = list()
        temp_2 = list()
        for v in nodes:
            if (d[0],v) in d_edges: temp_1.append(lp_f_i_uv[d,(d[0],v)])
            if (v,d[0]) in d_edges: temp_2.append(lp_f_i_uv[d,(v,d[0])])
        prob += lpSum(temp_1) - lpSum(temp_2) == lp_f_i[d]
    #for d in demands:
    #    prob += lpSum([lp_f_i_uv[d,(d[0],v)] for v in nodes if (d[0],v) in d_edges]) - \
    #            lpSum([lp_f_i_uv[d,(v,d[0])] for v in nodes if (v,d[0]) in d_edges]) == lp_f_i[d]
    
    # the second constraint
    for v in nodes:
        for d in demands:
            if v != d[0] and v!= d[1]:
                temp_1 = list()
                temp_2 = list()
                for u in nodes:
                    if (v,u) in d_edges: temp_1.append(lp_f_i_uv[d,(v,u)])
                    if (u,v) in d_edges: temp_2.append(lp_f_i_uv[d,(u,v)])
                prob += lpSum(temp_1) - lpSum(temp_2) == 0
    #for v in nodes:
    #    for d in demands:
    #        if v != d[0] and v != d[1]:
    #            prob += lpSum([lp_f_i_uv[d,(v,u)] for u in nodes if (v,u) in d_edges]) - \
    #                    lpSum([lp_f_i_uv[d,(u,v)] for u in nodes if (u,v) in d_edges]) == 0

    # the third constraint
    for (u,v) in edges:
        temp_1 = list()
        temp_2 = list()
        for d in demands:
            temp_1.append(lp_f_i_uv[d,(u,v)])
            temp_2.append(lp_f_i_uv[d,(v,u)])
        prob += lpSum(temp_1) + lpSum(temp_2) <= ug.edges[(u,v)]["tot_cap"]
    #for (u,v) in edges:
    #    prob += lpSum([lp_f_i_uv[d,(u,v)] for d in demands]) + \
    #            lpSum([lp_f_i_uv[d,(v,u)] for d in demands]) <= ug.edges[(u,v)]["tot_cap"] 
    
    # the fourth constraint
    for v in nodes:
        temp_1 = list()
        for d in demands:
            for u in nodes:
                if (v,u) in d_edges:
                    temp_1.append(lp_f_i_uv[d,(v,u)])
                    temp_1.append(lp_f_i_uv[d,(u,v)])
        prob += lpSum(temp_1) <= ug.nodes[v]["cap"]

    # the fifth constraint
    for d in demands:
        prob += m*d[3] <= lp_f_i[d] + d[2]

    #prob.writeLP("relaxed_program.txt")
    prob.solve()    # begin to solve the linear programming
    obj = value(prob.objective)

    return (obj,m,lp_f_i_uv,lp_f_i)

def jain_index(demands):
    tt = 0
    tt2 = 0
    for d in demands:
        remaining_slot = float(d[2]/d[3])
        tt = tt + remaining_slot
        tt2 = tt2 + remaining_slot**2
    jain_id = float(tt**2/(len(demands)*tt2))
    return jain_id