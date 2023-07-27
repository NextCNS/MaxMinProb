#!/usr/bin/python3
from pulp import *
#import sys
import network_gen as ng
from prg import jain_index

a = 0.99

#print("========== Generate topology ==========")
nov = 100    # the number of vertices of the QKD network
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
#l_argv = sys.argv
#l_argv.pop(0)
#l_demand = list()
#for i in l_argv:
#    j = i.strip()
#    j = j.replace('(','').replace(')','')
#    j = j.split(',')
#    l_demand.append((int(j[0]),int(j[1]),int(j[2]),int(j[3])))
#demands = l_demand
#demands = [(1,2,6,4),(10,20,8,5),(3,7,10,3)]
demands = [(19,32,176,16),(80,92,40,5),(69,31,38,19),(12,31,25,15),(43,9,64,24),(10,50,20,5),(23,30,50,10),(99,1,100,22)]
#demands = [(34,20,4,1),(8,48,18,1),(33,19,21,1),(4,8,15,1),(7,46,13,1),(7,2,9,1),(19,10,3,1),(13,33,9,1),(12,2,14,1),(48,36,15,1),(16,45,12,1),(12,38,19,1),(32,24,6,1),(27,20,2,1),(36,8,9,1),(47,5,14,1),(34,42,17,1),(38,19,23,1),(13,38,17,1),(45,44,18,1)] # Sample 11

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
#prob += m
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
#fptr = open("result.txt","a")
#fptr.write(f"{obj}\n")
#fptr.close()
print(f'Objective: {obj}')

#for var in lp_f_i_uv:
#    print(var,"=",lp_f_i_uv[var],"=",lp_f_i_uv[var].varValue)

for var in lp_f_i:
    print(var,"=",lp_f_i[var],"=",lp_f_i[var].varValue)

print("Maximum of minimal time slot:",m.varValue)
total_key = sum([lp_f_i[var].varValue for var in lp_f_i])
print("Total key the network can distribute:",total_key)
temp_demands = [(d[0],d[1],d[2]+lp_f_i[d].varValue,d[3]) for d in lp_f_i]
demands = temp_demands
# calculate Jane index
j_id = jain_index(demands)
#tt = 0
#tt2 = 0
#for var in lp_f_i:
#    remaining_slot = float((var[2]+lp_f_i[var].varValue)/var[3])
#    tt = tt + remaining_slot
#    tt2 = tt2 + remaining_slot**2

#jain_index = float(tt**2/(len(lp_f_i)*tt2))
print("Jain index:",j_id)