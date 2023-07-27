#!/usr/bin/python3
from pulp import *
import sys
import network_gen as ng
from prg import *

a = 0.99
l_argv = sys.argv
l_argv.pop(0)
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
l_demand = list()
for i in l_argv:
    j = i.strip()
    j = j.replace('(','').replace(')','')
    j = j.split(',')
    l_demand.append((int(j[0]),int(j[1]),int(j[2]),int(j[3])))
demands = l_demand
#demands = [(1,2,6,4),(10,20,8,5),(3,7,10,3)]

#demands = [(18,35,12,1),(40,12,20,1),(31,27,7,1),(11,18,13,1),(37,28,13,1),(40,49,14,1)]
demands_total_flow = dict()
for d in demands:
    demands_total_flow[d] = 0

(obj,m,f_i_uv,f_i) = relaxed_program(a,UG,DG,demands)
total_key = sum([f_i[var].varValue for var in f_i])   # total keys distributed over the network
temp_demands = [(d[0],d[1],d[2]+f_i[d].varValue,d[3]) for d in f_i]
demands = temp_demands
j_id = jain_index(demands)
mm = m.varValue
fptr1 = open("result_m.txt","a")
fptr2 = open("result_ttk.txt","a")
fptr3 = open("result_j.txt","a")
fptr1.write(f"{mm}\n")
fptr2.write(f"{total_key}\n")
fptr3.write(f"{j_id}\n")
fptr1.close()
fptr2.close()
fptr3.close()