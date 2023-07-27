#!/usr/bin/python3

import sys
import network_gen as ng
import networkx as nx
from prg import jain_index

INF = 10000

l_argv = sys.argv
l_argv.pop(0)

#print("========== Generate topology ==========")
nov = int(l_argv.pop())    # the number of vertices of the QKD network
prob = 0.05  # the probability of generating edges in the QKD network
UG = ng.gen(nov,prob)   # generate the undirected topology

#l_argv = sys.argv
#l_argv.pop(0)
l_demand = list()
for i in l_argv:
    j = i.strip()
    j = j.replace('(','').replace(')','')
    j = j.split(',')
    l_demand.append((int(j[0]),int(j[1]),int(j[2]),int(j[3])))
demands = l_demand

#demands = [(1,2,6,4),(10,20,8,5),(3,7,10,3)]    # the list of demands
#demands = [(98,97,13,1),(89,26,15,1),(55,91,17,1),(63,51,11,1),(92,0,11,1),(89,43,8,1),(19,2,16,1),(57,10,9,1)]
#demands = [(64,95,5,1),(72,43,16,1),(18,70,9,1),(72,24,7,1),(87,14,6,1),(61,11,20,1),(16,97,7,1),(76,33,10,1),(0,9,10,1),(40,8,12,1),(94,56,14,1),(68,78,19,1),(23,95,3,1),(7,92,13,1),(63,68,2,1),(47,24,16,1),(41,65,15,1),(2,41,11,1),(52,16,6,1),(8,2,14,1)]
#demands = [(74,66,16,1),(25,26,8,1),(4,44,1,1),(29,73,4,1),(97,62,13,1),(66,45,10,1),(15,87,11,1),(80,91,13,1),(89,46,7,1),(98,78,9,1),(41,93,10,1),(50,81,6,1),(2,91,3,1),(22,5,8,1),(48,14,11,1),(20,83,13,1),(23,12,16,1),(54,0,15,1),(90,27,7,1),(66,71,15,1),(46,63,25,1),(43,91,8,1),(1,89,7,1),(18,31,13,1),(12,61,6,1),(16,87,7,1),(32,30,18,1),(32,98,7,1),(1,34,11,1),(46,49,5,1)]
#cur_time_slot = min([d[2]/d[3] for d in demands])
demands_copy = demands.copy()
demands_final = list()
while len(demands_copy) > 0:
    has_demand = False
    cur_time_slot = min([d[2]/d[3] for d in demands_copy])
    d_list = list()
    min_slot = INF
    # determine all demands with the smallest number of remaining time slots (return in d_list set)
    for d in demands_copy:
        if d[2]/d[3] < min_slot:
            min_slot = float(d[2]/d[3])
            d_list = list()
            d_list.append(d)
        elif d[2]/d[3] == min_slot:
            d_list.append(d)

    # choose the request need to be served (these requests have the same number of remaining time slots)
    # the request with the minimum number of hops will be prioritized serving
    hop_cnt = INF
    node_ok = True
    path_chk_ok = True
    for d in d_list:
        src = d[0]
        dst = d[1]
        # check if the source and destination have enough memory or not
        if (UG.nodes[src]["cap"] <= 0) or (UG.nodes[dst]["cap"] <= 0):
            #node_ok = False
            demands_final.append(d)
            demands_copy.remove(d)
            continue    # if the source or destination of the demand is insufficient key memory, the demand cannot be satified any more
                        # hence the demand need to be removed from the original demand set

        copy_UG = UG.copy()
        for v in list(copy_UG.nodes):
            if v == src or v == dst: continue
            if copy_UG.nodes[v]["cap"] <= 1: copy_UG.remove_node(v) # remove the node with insufficient capacity (memory) from the network
        
        if not nx.has_path(copy_UG,src,dst):    # check if there is a path between the source and the destination after removing some nodes
            demands_final.append(d)
            demands_copy.remove(d)
            #path_chk_ok = False                 # if not we cannot serve this request, hence cannot improve the result
            continue   # break if the network cannot satisfy the demand any more due to the insufficient capacity of edges
        
        has_demand = True
        d_path = nx.shortest_path(copy_UG,src,dst)
        if len(d_path) < hop_cnt:
            hop_cnt = len(d_path)
            selected_demand = d             # the demand
            selected_demand_path = d_path   # the demand path
    
    #if (not node_ok) or (not path_chk_ok): break
    if not has_demand: continue
    else:
        node_cap_used = dict()
        edge_cap_used = dict()
        for i in range(len(selected_demand_path)):
            cur_n = selected_demand_path[i]
        
            if i == 0 or i == len(selected_demand_path) - 1:    # if the node is the end node
                node_cap_used[cur_n] = 1
            else:                                               # intermediate nodes
                node_cap_used[cur_n] = 2

            if i < len(selected_demand_path)-1:
                next_n = selected_demand_path[i+1]
                if next_n < cur_n:
                    edge_cap_used[(next_n,cur_n)] = 1
                else:
                    edge_cap_used[(cur_n,next_n)] = 1

    UG = ng.network_update(node_cap_used,edge_cap_used,UG,True)  # update the network
    temp_d = (selected_demand[0],selected_demand[1],selected_demand[2]+1,selected_demand[3])
    demands_copy.remove(selected_demand)
    demands_copy.append(temp_d)

maxmin = min([d[2]/d[3] for d in demands_final])

original = sum([d[2] for d in demands])
target = sum([d[2] for d in demands_final])

total_key = target - original
j_id = jain_index(demands_final)
fptr1 = open("result_m.txt","a")
fptr2 = open("result_ttk.txt","a")
fptr3 = open("result_j.txt","a")
fptr1.write(f"{maxmin}\n")
fptr2.write(f"{total_key}\n")
fptr3.write(f"{j_id}\n")
fptr1.close()
fptr2.close()
fptr3.close()