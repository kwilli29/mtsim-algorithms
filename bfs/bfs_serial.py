import networkx as nx
import matplotlib.pyplot as plt
import random as rand
import csv
from collections import defaultdict
import numpy as np
from scipy import sparse

## This is a serial Breadth First Search Algorithm that can take in a few different types of graphs formats ##
## For reference mostly ##

## Only need to worry about the bfs_g500_serial function ##

def read_kfile():
    with open('../text/output.txt') as f:
         ls = f.read()

    n, numEdges, adjMatrix = ls.splitlines()

    n = int(n)
    numEdges = int(numEdges)

    adjMatrix = map(int, adjMatrix.split(" "))
    # adjMatrix = 1D array here, adjMat[k] = (i*n)+j = {i: [j, ...], ...}

    return n, numEdges, adjMatrix

def matToCSR(matrix, n):
    
    matrix = list(matrix)
    matrix = np.reshape(matrix, (n,n))
    csr_mat = sparse.csr_matrix(matrix)

    return csr_mat

def matTolist(matrix, n):

    matrix = list(matrix)

    adjList = defaultdict(list)

    for index, k in enumerate(matrix):
        
          i = index//n
          j = index%n

          if k != 0:
            adjList[i].append(j) ######### 'malloc'?

    return adjList

def CSRtoDict(csr):
    csr = csr.toarray()
    D = defaultdict(list)

    for i, row in enumerate(csr):
        for j, num in enumerate(row):
            if num:
                D[i].append(j)

    return D

def read_g500_file():

    G = sparse.load_npz("../text/test_csr_matrix_000.npz")
    return G

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

    '''
    n, numEdges, adjMatrix = read_kfile()
    # adjList = matTolist(adjMatrix, n)
    # print(adjList)

    F = matToCSR(adjMatrix, n)
    root = 1 # ?
    # serial_visited = bfs_simple_serial(adjList, root)
    serial_parent = bfs_g500_serial(F, root)

    print(f'Parent: {serial_parent}\nLength:{len(serial_parent)}')
    print()
    print(f'Visited: {serial_visited}\nLength:{len(serial_visited)}')
    print()
    '''
    
    #'''

    G = read_g500_file()
    
    # Parallel: search keys for a handful of random starting points to concurrently run bfs from

    # Kernel 2
    root = 1 # serial bfs
    parent = bfs_g500_serial(G, root)

    print(f'Parent: {list(map(int, parent))}\nLength:{len(parent)}')
    print()
    #print(f'Visited: {list(map(int, visited))}\nLength:{len(visited)}')
    print()
    print('end')
    #'''

    return

if __name__ == '__main__':
        main()