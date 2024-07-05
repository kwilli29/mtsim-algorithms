import networkx as nx
import matplotlib.pyplot as plt
import random as rand
import csv
from collections import defaultdict
import heapq
import numpy as np
from scipy import sparse

import convert_graph_formats as convert

SCALE_TEENY = 10
EDGEF_TEENY = 16

def sssp_simple_serial(D,root):
    # bui prog challenges Dijkstra code
    frontier = []
    visited = {}
    heapq.heappush(frontier, (0, root,root)) # (0, root, root))
    while frontier:
        weight,source,target = heapq.heappop(frontier)

        if target in visited:
            continue
        visited[target] = source

        for neighbor in D[target]:#, cost in D[target].items():
            heapq.heappush(frontier, (weight+neighbor[1],target,neighbor[0])) #(weight+cost, target,neighbor))

    ## reconstruct path ##
    for t in list(D.keys())[1:]:
        path = []
        curr = t
        while curr != root and curr in visited.keys():
            path.append(curr)
            curr = visited[curr]
        path.append(root)

        rev_path = np.array(path)[::-1].tolist()
        print(f'{root} -> {t} = {rev_path}')
    print()
    
    return visited

def sssp_g500_serial(F, root):
    
    G = F.toarray() # unpack into a 2d array 

    # N = array of sizes of all the lists in graph I think?
    N = len(G[0]) # N = # of verts / row of matrix I 

    d = [np.inf]*N
    d[root] = 0
    parent = [-1]*N
    parent[root] = root

    vist ={}
    vist[root] = root

    Q = range(N)

    while len(Q) > 0:

        mini_dist = np.inf
        for i,k in enumerate(Q):
            if d[k] < mini_dist or mini_dist == np.inf:
                mini_ind = i
                mini_dist = d[k]

        v = Q[mini_ind]
        
        Q = np.setdiff1d(Q, [v])        

        I = np.nonzero(G[:][v])[0]
        V = G[:][v][I] # G[:][v][I] = all nonzero values in specified col

        for k in range(len(I)):
            u = I[k]
            dist_tmp = d[v] + V[k]
            if dist_tmp < d[u]:
                d[u] = dist_tmp
                vist[int(u)] = int(v)
                parent[u] = v
    
    # reconstruct path
    print(vist)
    
    for t in range(N):
        path = []
        curr = t
        while curr != root and curr in vist.keys():
            path.append(curr)
            curr = vist[curr]
        path.append(root)

        rev_path = np.array(path)[::-1].tolist()
        #print(f'{root} -> {t} = {rev_path}')
    print()

    return (parent, d)

def simple():
    '''
    #n, numEdges, adjMatrix = read_kfile()
    #G = matToCSR(adjMatrix, n)
    '''
    # OR

    #G = convert.read_g500_file()
    G = convert.read_csv_file(7, 'src/csv/simple_graph_001.csv')
    #n = len(G.toarray()[0])
    D = convert.CSRtoDict(G)
    #convert.dictToCSV(D)
    root = list(D.keys())[0]
    visited = sssp_simple_serial(D, root)

    print(f'Visited#1: {visited}')
    print(end='\n\n')
    #'''

def main():

    # Simple Algorithm
    # simple()

    # G500
    #G = convert.read_g500_file()
    G = convert.read_csv_file(7, 'src/csv/simple_graph_001.csv')
    n = len(G.toarray()[0])

    # Kernel 3
    root = 0 # serial bfs
    parent, d = sssp_g500_serial(G, root)


    ####### Print Dictionary #######
    '''
    # kread_file [kelly's random graph file]
    n, numEdges, adjMatrix = read_kfile()
    adjList = matTolist(adjMatrix, n)
    for k,v in adjList.items():
        print(f'{k}:{v}')
    '''

    #'''
    # read_g500_file [g500 graph format]
    reg_matrix = convert.CSRtoMat(G, n)
    adjList = convert.matTolist(reg_matrix, n)
    '''
    for k,v in adjList.items():
        print(f'{k}:{v}')
    #'''

    print('end')

    return

if __name__ == '__main__':
    main()