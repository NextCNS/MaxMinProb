#!/usr/bin/python3
from pulp import *
#import sys
import network_gen as ng
from prg import *

a = 0.99

#print("========== Generate topology ==========")
nov = 300    # the number of vertices of the QKD network
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

#demands = [(16,9,7,1),(28,5,5,1),(0,49,12,1),(33,29,7,1),(3,22,6,1),(28,3,13,1),(30,2,7,1),(8,23,11,1),(33,36,15,1),(28,35,6,1),(4,44,8,1),(1,12,12,1),(3,48,5,1),(37,43,10,1),(22,27,9,1),(16,32,12,1),(28,38,10,1),(41,49,9,1),(42,4,13,1),(6,2,12,1)] # Sample 100
demands = [(34,20,4,1),(8,48,18,1),(33,19,21,1),(4,8,15,1),(7,46,13,1),(7,2,9,1),(19,10,3,1),(13,33,9,1),(12,2,14,1),(48,36,15,1),(16,45,12,1),(12,38,19,1),(32,24,6,1),(27,20,2,1),(36,8,9,1),(47,5,14,1),(34,42,17,1),(38,19,23,1),(13,38,17,1),(45,44,18,1)] # Sample 11
#demands = [(19,32,176,16),(80,92,40,5),(69,31,38,19),(12,31,25,15),(43,9,64,24),(10,50,20,5),(23,30,50,10),(99,1,100,22)]
demands_total_flow = dict()
for d in demands:
    demands_total_flow[d] = 0

(obj,m,f_i_uv,f_i) = relaxed_program(a,UG,DG,demands)

#fptr = open("result.txt","a")
#fptr.write(f"{obj}\n")
#fptr.close()
print("Objective value:",obj)
print("The maximum time slot:",m.varValue)
#total_key = sum([f_i[var].varValue for var in f_i])
total_key = 0
for var in f_i:
    rts = f_i[var].varValue + var[2]
    print(var,"=",f_i[var],"=",f_i[var].varValue,"rts =",rts)
    total_key = total_key + f_i[var].varValue
print("The total key that the network can distribute:",total_key)