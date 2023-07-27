#!/usr/bin/python3
from pulp import *
import sys
import network_gen as ng
from prg import relaxed_program, jain_index

a = 0.99

#print("========== Generate topology ==========")
nov = num_nodes    # the number of vertices of the QKD network
prob = 0.05  # the probability of generating edges in the QKD network
UG = ng.gen(nov,prob)   # generate the undirected topology

l_argv = sys.argv
l_argv.pop(0)
l_demand = list()
for i in l_argv:
    j = i.strip()
    j = j.replace('(','').replace(')','')
    j = j.split(',')
    l_demand.append((int(j[0]),int(j[1]),int(j[2]),int(j[3])))
demands = l_demand

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

    flow_list = dict()
    demands_total_flow = dict()
    for d in demands:
        if demand_edge[d] == {}:
            demands_total_flow[d] = 0
            continue    # if a demand doesn't have flow because its remaining time slots exceeds the objective. In other words, it has not been served
                        # therefore, some demands is not in the flow_list
        temp_total_flow = 0
        flow_list[d] = ng.det_flow(d,demand_edge[d])    # determine the flow passing over each edge for each demand
        for e in flow_list[d]:
            if e[0] == d[0]: temp_total_flow = temp_total_flow + flow_list[d][e]
        demands_total_flow[d] = temp_total_flow

    # update the network and demands
    cap_used = dict()
    for d in demands:
        if d in flow_list:
            for e in flow_list[d]:
                if e[0] > e[1]: temp_e = (e[1],e[0])
                else: temp_e = e
                if temp_e not in cap_used: cap_used[temp_e] = flow_list[d][e]
                else: cap_used[temp_e] = cap_used[temp_e] + flow_list[d][e]
        
    node_cap_used = dict()
    for (u,v) in cap_used:
        if u not in node_cap_used: node_cap_used[u] = cap_used[(u,v)]
        else: node_cap_used[u] = node_cap_used[u] + cap_used[(u,v)]

        if v not in node_cap_used: node_cap_used[v] = cap_used[(u,v)]
        else: node_cap_used[v] = node_cap_used[v] + cap_used[(u,v)]
    
    UG = ng.network_update(node_cap_used,cap_used,UG,False)
    
    temp_demands = [(d[0],d[1],d[2]+demands_total_flow[d],d[3]) for d in demands]
    demands = temp_demands

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
    #    if d[0] not in UG or d[1] not in UG:
    #        no_node = True
    #        break
    #if no_node: break

total_key = total_remaining_key - init_remaining_key
j_id = jain_index(demands)
fptr1 = open("result_m.txt","a")
fptr2 = open("result_ttk.txt","a")
fptr3 = open("result_j.txt","a")
fptr1.write(f"{cur_min_time_slot}\n")
fptr2.write(f"{total_key}\n")
fptr3.write(f"{j_id}\n")
fptr1.close()
fptr2.close()
fptr3.close()