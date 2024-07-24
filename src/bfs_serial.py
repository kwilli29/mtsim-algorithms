import networkx as nx
import matplotlib.pyplot as plt
import random as rand
import csv
from collections import defaultdict
import numpy as np
from scipy import sparse

import convert_graph_formats as convert

## This is a serial Breadth First Search Algorithm that can take in a few different types of graphs formats ##
## For reference mostly ##

def bfs_simple_serial(adjList, root):

    queue = [root]
    visited = []

    while queue:
        node = queue.pop(0)

        if node not in visited:
            visited.append(node) 

            if adjList[node]:
                for neighbor in adjList[node]:
                    queue.append(neighbor) 

    return visited 
     
def bfs_g500_serial(F, root):

    G = F.toarray() # unpack into a 2d array 

    N = len(G[0]) # N = # of verts / row of square matrix

    parent = [-1]*N
    parent[root] = root

    to_visit = [0]*N
    to_visit[0] = root

    lastk = 1 
    for k in range(N):  # look at column k of Graph G -- for its children -- add children to to_visit
        v = to_visit[k]
        if v == 0: break
        I = np.nonzero(G[:][v])[0] # list of children

        next = [] 
        
        for i in I:
            if parent[i] == -1:
                parent[i] = v
                next.append(i)  # have a list of next vertices

        nums = list(range(lastk, len(next)+lastk))
        for k, x in enumerate(nums): 
            to_visit[x] = next[k] # add vertices to the to_visit list

        lastk = lastk + len(next)

    print('Parent: [')
    for x in parent: print(x, end=' ')
    print(']')

    return parent

    ## TODO: Think of better way to keep track of info ##

def main():
    
    G = convert.read_g500_file('text/test_csr_matrix_000.npz')

    # Kernel 2
    root = 1 # serial bfs
    parent = bfs_g500_serial(G, root)

    print(f'Parent: {list(map(int, parent))}\nLength:{len(parent)}')
    print()
    #print(f'Visited: {list(map(int, visited))}\nLength:{len(visited)}')
    print()
    print('end')


    '''
    n, numEdges, adjMatrix = convert.read_kfile()
    # adjList = convert.matTolist(adjMatrix, n)
    # print(adjList)

    F = convert.matToCSR(adjMatrix, n)
    root = 1 # 
    # serial_visited = bfs_simple_serial(adjList, root)
    serial_parent = bfs_g500_serial(F, root)

    print(f'Parent: {serial_parent}\nLength:{len(serial_parent)}')
    print()
    print(f'Visited: {serial_visited}\nLength:{len(serial_visited)}')
    print()
    '''

    return

if __name__ == '__main__':
        main()