#!/usr/bin/python3
from pulp import *
import sys
import network_gen as ng
from prg import *

a = 0.99

#print("========== Generate topology ==========")
nov = 100    # the number of vertices of the QKD network
prob = 0.05  # the probability of generating edges in the QKD network
UG = ng.gen(nov,prob)   # generate the undirected topology
#DG = ng.ug2dg(UG)       # generate the directed topology

#nodes = list(UG.nodes)  # the list of nodes
#edges = list(UG.edges)  # the list of undirected edges
#for v in list(UG.nodes):
#    node_capa = UG.nodes[v]["cap"]
#    print(f"Node {v}: cap: {node_capa}")
#for e in edges:
#    channels = UG.edges[e]["channel"]
#    cap = UG.edges[e]["cap"]
    #print(f"edges: {e}, channels: {channels}, capacity: {cap}")
#d_edges = list(DG.edges)    # the list of directed edges

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
#demands = [(22,27,10,1),(23,5,2,1),(22,18,20,1),(12,2,3,1),(26,27,8,1),(23,21,9,1),(13,4,12,1),(26,11,6,1)]
#demands = [(16,9,7,1),(28,5,5,1),(0,49,12,1),(33,29,7,1),(3,22,6,1),(28,3,13,1),(30,2,7,1),(8,23,11,1),(33,36,15,1),(28,35,6,1),(4,44,8,1),(1,12,12,1),(3,48,5,1),(37,43,10,1),(22,27,9,1),(16,32,12,1),(28,38,10,1),(41,49,9,1),(42,4,13,1),(6,2,12,1)] # Sample 100
demands = [(34,20,4,1),(8,48,18,1),(33,19,21,1),(4,8,15,1),(7,46,13,1),(7,2,9,1),(19,10,3,1),(13,33,9,1),(12,2,14,1),(48,36,15,1),(16,45,12,1),(12,38,19,1),(32,24,6,1),(27,20,2,1),(36,8,9,1),(47,5,14,1),(34,42,17,1),(38,19,23,1),(13,38,17,1),(45,44,18,1)] # Sample 11
#demands = [(19,32,176,16),(80,92,40,5),(69,31,38,19),(12,31,25,15),(43,9,64,24),(10,50,20,5),(23,30,50,10),(99,1,100,22)]
#demands_total_flow = dict()
#for d in demands:
#    demands_total_flow[d] = 0
cur_min_time_slot = min([d[2]/d[3] for d in demands])
total_remaining_key = sum([d[2] for d in demands])
init_remaining_key = total_remaining_key
k_flag = False
t_flag = False

while True:
    DG = ng.ug2dg(UG)       # generate the directed topology
    # call the linear program
    (obj,m,f_i_uv,f_i) = relaxed_program(a,UG,DG,demands)

    demand_edge = dict()
    for d in demands:
        demand_edge[d] = dict()

    for var in f_i_uv:
        if f_i_uv[var].varValue > 0:
            demand_edge[var[0]][var[1]] = f_i_uv[var].varValue

    #for var in f_i_uv:
    #    temp_1 = f_i_uv[var]
    #    temp_2 = f_i_uv[var].varValue
    #    fptr.write(f"{var} = {temp_1} = {temp_2}\n")

    #fptr.write("=================================================\n")

    flow_list = dict()
    demands_total_flow = dict()
    for d in demands:
        if demand_edge[d] == {}:
            demands_total_flow[d] = 0
            continue    # if a demand doesn't have flow because its remaining time slots exceeds the objective. In other words, it has not been served
                        # therefore, some demands is not in the flow_list
        temp_total_flow = 0
        print(f"{d}, {demand_edge[d]}")
        flow_list[d] = ng.det_flow(d,demand_edge[d])    # determine the flow passing over each edge for each demand
        for e in flow_list[d]:
            if e[0] == d[0]: temp_total_flow = temp_total_flow + flow_list[d][e]
        demands_total_flow[d] = temp_total_flow + demands_total_flow[d]
        #print(f"demand {d}, total flow: {temp_total_flow}")

    # update the network and demands
    cap_used = dict()
    for d in demands:
        if d in flow_list:
            for e in flow_list[d]:
                if e[0] > e[1]: temp_e = (e[1],e[0])
                else: temp_e = e
                if temp_e not in cap_used: cap_used[temp_e] = flow_list[d][e]
                else: cap_used[temp_e] = cap_used[temp_e] + flow_list[d][e]
        #print(demand_edge[d])
        #print("=================================================================================")
        #print(flow_list[d])
        #print("=================================================================================")

    #print(cap_used)
    #print("=========================================")
    node_cap_used = dict()
    for (u,v) in cap_used:
        if u not in node_cap_used: node_cap_used[u] = cap_used[(u,v)]
        else: node_cap_used[u] = node_cap_used[u] + cap_used[(u,v)]

        if v not in node_cap_used: node_cap_used[v] = cap_used[(u,v)]
        else: node_cap_used[v] = node_cap_used[v] + cap_used[(u,v)]
    #print(node_cap_used)
    #print("The status of the network before updating")
    #for e in edges:
    #    total_cap_e = UG.edges[e]["tot_cap"]
        #print(f"edge: {e}, total capacity: {total_cap_e}")
    #print("==================================================================")
    UG = ng.network_update(node_cap_used,cap_used,UG,False)
    #print("The status of the network after updating")
    #for e in list(UG.nodes):
    #    total_cap_e = UG.nodes[e]["cap"]
    #    print(f"node: {e}, capacity: {total_cap_e}")

    #print(demands_total_flow)
    # update the remaining keys of the demands
    temp_demands = [(d[0],d[1],d[2]+demands_total_flow[d],d[3]) for d in demands]
    demands = temp_demands

    #print(temp_demands)
    #print(demands)

    temp_total_remaining_key = sum(d[2] for d in demands)
    print(f"new total key: {temp_total_remaining_key}")
    print(f"current total key: {total_remaining_key}")

    if temp_total_remaining_key > total_remaining_key: total_remaining_key = temp_total_remaining_key
    else: k_flag = True

    new_min_time_slot = min([d[2]/d[3] for d in demands])
    print(f"new: {new_min_time_slot}")
    print(f"cur: {cur_min_time_slot}")

    if new_min_time_slot > cur_min_time_slot: cur_min_time_slot = new_min_time_slot
    else: t_flag = True

    if k_flag and t_flag: break

    # check if a node in demands in the network
    #no_node = False
    #for d in demands:
    #    if (not UG.has_node(d[0])) or (not UG.has_node(d[1])):
    #        no_node = True
    #        break
    #if no_node: break

#fptr.close()
distributed_keys = total_remaining_key - init_remaining_key
print(f"Objective: {cur_min_time_slot}")
print(f"Total keys that the network can distribute: {distributed_keys}")