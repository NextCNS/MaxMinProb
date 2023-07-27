#!/usr/bin/python3
from pulp import *
import sys
import network_gen as ng
from prg import jain_index

a = 0.99

#print("========== Generate topology ==========")
nov = num_nodes    # the number of vertices of the QKD network
prob = 0.05  # the probability of generating edges in the QKD network
UG = ng.gen(nov,prob)   # generate the undirected topology
DG = ng.ug2dg(UG)       # generate the directed topology

nodes = list(UG.nodes)  # the list of nodes
edges = list(UG.edges)  # the list of undirected edges
#for e in edges:
#    channels = UG.edges[e]["channel"]
#    cap = UG.edges[e]["cap"]
    #print(f"edges: {e}, channels: {channels}, capacity: {cap}")
d_edges = list(DG.edges)    # the list of directed edges

# the set of demands
# the format of a demand: D_i = (s_i,d_i,k_i,r_i)
# s_i: the source
# d_i: the destination
# k_i: the number of the remaining keys
# r_i: the consumption rate (keys/time slot)
#print("========== The set of demands ==========")
l_argv = sys.argv
l_argv.pop(0)
l_demand = list()
for i in l_argv:
    j = i.strip()
    j = j.replace('(','').replace(')','')
    j = j.split(',')
    l_demand.append((int(j[0]),int(j[1]),int(j[2]),int(j[3])))
demands = l_demand
#demands = [(1,2,6,4),(10,20,8,5),(3,7,10,3)]
#demands = [(22,32,176,16),(85,92,40,5),(69,31,38,19),(21,3,25,5),(43,92,64,4)]

# define the ILP problem
prob = LpProblem("Maximin problem",LpMaximize)

# define the variables of the problem
# f^i_{(u,v)}
f_i_uv = list()
for d in demands:
    for e in d_edges:
        f_i_uv.append((d,e))  # should be a list of tuple

lp_f_i_uv = LpVariable.dicts("Flow f_i_uv",f_i_uv,0,None,cat="Integer")

# f^i
f_i = list()
for d in demands:
    f_i.append(d)

lp_f_i = LpVariable.dicts("Flow f_i",f_i,0,None,cat="Integer")

# m
m = LpVariable("m",0,None,cat="Continuous")

# the objective function
prob += a*m + (1-a)*lpSum([lp_f_i[d] for d in demands])

# the first constraint
for d in demands:
    prob += lpSum([lp_f_i_uv[d,(d[0],v)] for v in nodes if (d[0],v) in d_edges]) - \
            lpSum([lp_f_i_uv[d,(v,d[0])] for v in nodes if (v,d[0]) in d_edges]) == lp_f_i[d]
    
# the second constraint
for v in nodes:
    for d in demands:
        if v != d[0] and v != d[1]:
            prob += lpSum([lp_f_i_uv[d,(v,u)] for u in nodes if (v,u) in d_edges]) - \
                    lpSum([lp_f_i_uv[d,(u,v)] for u in nodes if (u,v) in d_edges]) == 0

# the third constraint
for (u,v) in edges:
    prob += lpSum([lp_f_i_uv[d,(u,v)] for d in demands]) + \
            lpSum([lp_f_i_uv[d,(v,u)] for d in demands]) <= UG.edges[(u,v)]["channel"] * UG.edges[(u,v)]["cap"]
    
# the fourth constraint
for v in nodes:
    temp_1 = list()
    for d in demands:
        for u in nodes:
            if (v,u) in d_edges:
                temp_1.append(lp_f_i_uv[d,(v,u)])
                temp_1.append(lp_f_i_uv[d,(u,v)])
    prob += lpSum(temp_1) <= UG.nodes[v]["cap"]

# the fifth constraint
for d in demands:
    prob += m*d[3] <= lp_f_i[d] + d[2]

#prob.writeLP("ilp.txt")
prob.solve()    # begin to solve the linear programming
obj = value(prob.objective)
total_key = sum([lp_f_i[var].varValue for var in lp_f_i])   # total keys distributed over the network
mm = m.varValue
# calculate the Jane index
temp_demands = [(d[0],d[1],d[2]+lp_f_i[d].varValue,d[3]) for d in lp_f_i]
demands = temp_demands
j_id = jain_index(demands)

fptr1 = open("result_m.txt","a")
fptr2 = open("result_ttk.txt","a")
fptr3 = open("result_j.txt","a")
fptr1.write(f"{mm}\n")
fptr2.write(f"{total_key}\n")
fptr3.write(f"{j_id}\n")
fptr1.close()
fptr2.close()
fptr3.close()