#!/usr/bin/python3
# generate networks randomly, including undirected and directed networks
# the properties of an undirected network:
#   + edge: the number of wavelength and the capacity of each wavelength
#   + node: the capacity of key storages

import networkx as nx
import numpy as np

def gen(nov,prob,seed=1,channel_num_lb=1,channel_num_ub=10,channel_cap_lb=1,channel_cap_ub=5,node_cap_lb=10,node_cap_ub=60):  #nov: number of vertices, prob: the probability of generating edges
    check_connected = 0
    s = seed   #random seed
    i = 0
    while check_connected == 0:
        check_connected = 1
        UG = nx.erdos_renyi_graph(nov,prob,seed=s)
        if not nx.is_connected(UG):
            print("The network is not connected. Generate again!!!")
            check_connected = 0
            i = i+1
            s = seed*100 + i

    n_edges = list(UG.edges)
    n_nodes = list(UG.nodes)
    channel_num_ub = channel_num_ub    # the upper bound of number of channels on an edge
    channel_cap_ub = channel_cap_ub      # the upper bound of capacity of a channel on an edge
    node_cap_ub = node_cap_ub        # the upper bound of capacity of a node
    np.random.seed(seed)
    channels_num = list(np.random.randint(channel_num_lb,channel_num_ub,size=len(n_edges)))
    channels_cap = list(np.random.randint(channel_cap_lb,channel_cap_ub,size=len(n_edges)))
    nodes_cap = list(np.random.randint(node_cap_lb,node_cap_ub,size=len(n_nodes)))
    edge_property_dict = dict() # dictionary containing the edge properties
    node_property_dict = dict() # dictionary containing the node property
    
    # set property for edges
    for id,e in enumerate(n_edges):
        edge_property_dict[e] = {"channel":channels_num[id],"cap":channels_cap[id],"tot_cap":channels_num[id]*channels_cap[id]}

    for id,v in enumerate(n_nodes):
        node_property_dict[v] = {"cap":nodes_cap[id]}

    nx.set_node_attributes(UG,node_property_dict)
    nx.set_edge_attributes(UG,edge_property_dict)

    return UG

def ug2dg(ug):
    edges = list(ug.edges)
    temp_edges = list()
    
    for e in edges:
        temp_edges.append((e[0],e[1]))
        temp_edges.append((e[1],e[0]))
    DG = nx.DiGraph()
    DG.add_edges_from(temp_edges)
    return DG

def det_flow(demand,edge_flow_dict):
    temp_dict = dict()
    edge_flow_dict_copy = edge_flow_dict.copy()
    src = demand[0]
    dst = demand[1]
    G = nx.DiGraph()
    edge_list = [e for e in edge_flow_dict]
    G.add_edges_from(edge_list)
    if (G.has_node(src)) and (G.has_node(dst)):
        for e in edge_flow_dict:
            temp_dict[e] = 0
            if edge_flow_dict[e] < 1: G.remove_edge(*e) # remove edges whose flow is less than 1
        
        has_path = nx.has_path(G,src,dst)
        while has_path:
            p = nx.shortest_path(G,src,dst)
            temp_edge_list = list()
            for i in range(len(p)-1):
                temp_edge_list.append((p[i],p[i+1]))
            temp_edge_flow = list()
            for e in temp_edge_list:    # the list of the edges along the path
                temp_edge_flow.append(edge_flow_dict_copy[e])
            min_flow = min(temp_edge_flow)
            int_min_flow = int(min_flow)
            for e in temp_edge_list:
                edge_flow_dict_copy[e] = edge_flow_dict_copy[e] - int_min_flow
                temp_dict[e] = temp_dict[e] + int_min_flow
                if edge_flow_dict_copy[e] < 1: G.remove_edge(*e)
            has_path = nx.has_path(G,src,dst)

    return temp_dict

def network_update(node_cap_used,cap_used,ug,remove_edge):
    # update the capacity of edges
    for e in cap_used:
        ug.edges[e]["tot_cap"] = ug.edges[e]["tot_cap"] - cap_used[e]
        if ug.edges[e]["tot_cap"] <= 0:
            if remove_edge: ug.remove_edge(*e) #   for the PSA
            else: ug.edges[e]["tot_cap"] = 0 # for the LPR-RA

    # update the capacity of nodes
    for v in node_cap_used:
        ug.nodes[v]["cap"] = ug.nodes[v]["cap"] - node_cap_used[v]

    return ug

if __name__ == "__main__":
    ug = gen(20,0.6)
    for v in ug.nodes:
        temp = ug.nodes[v]["cap"]
        print(f"Node: {v}, capacity: {temp}")

    for e in ug.edges:
        temp_chan = ug.edges[e]["channel"]
        temp_cap = ug.edges[e]["cap"]
        print(f"Edge: {e}, channels: {temp_chan}, capacity: {temp_cap}")

    dg = ug2dg(ug)
    e_dg = list(dg.edges)
    print (e_dg)