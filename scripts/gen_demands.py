#!/usr/bin/python3

import random
import sys
import numpy as np

# syntax: ./gen_demands #demands #nodes the_average_value_of_remaining_time_slot the_deviation_of_the_distribution consumption_rate
# the consumption_rate can get "random" to indicate that it will be generated randomly between [1,20]

num_cases = 100
l_argv = sys.argv
l_argv.pop(0)
con_rate = l_argv.pop() # the consumption rate
# the number of remaining time slots is generated randomly according to the normal distribution with the average and deviation
deviation = float(l_argv.pop()) # the deviation of the remaining time slot
avrg = int(l_argv.pop())        # the average value of the remaining time slot
##################################################################################
num_nodes = int(l_argv.pop())   # the number of nodes
num_demands = int(l_argv.pop()) # the number of demands

#(DG,UG) = read_graph(graph)
#nodes = [n for n in range(100)]
#demand_list = list(permutations(nodes,2))
fptr = open(f"Sample_{num_nodes}_nodes_{num_demands}_demands.txt",'w')

for k in range(num_cases):
    temp_list_demand = list()
    for i in range(num_demands):
        src = random.randint(0,num_nodes-1)
        dst = random.randint(0,num_nodes-1)
        while (src == dst) or (src,dst) in temp_list_demand or (dst,src) in temp_list_demand:
            src = random.randint(0,num_nodes-1)
            dst = random.randint(0,num_nodes-1)
        temp_list_demand.append((src,dst))
    list_demand = list()
    ok = True
    while ok:
        temp_time_slot = np.random.normal(avrg,deviation,(num_demands,))
        time_slot = np.rint(temp_time_slot) # the remaining number of time slots
        flag = time_slot <= 0   # check if there is any negative element
        ok = np.any(flag)
    if con_rate == "random":
        consumption_rate = np.random.randint(1,20,(num_demands,))
    else:
        consumption_rate = int(con_rate)*np.ones(num_demands)
    for id,d in enumerate(temp_list_demand):
        num_key = int(time_slot[id]) * int(consumption_rate[id])
        fptr.write(f"({d[0]},{d[1]},{num_key},{int(consumption_rate[id])}) ")
    #fptr.write(str(list_demand))
    if k < num_cases-1: fptr.write("\n")
fptr.close()