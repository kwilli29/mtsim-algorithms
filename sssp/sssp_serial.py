import networkx as nx
import matplotlib.pyplot as plt
import random as rand
import csv
from collections import defaultdict
import heapq
import numpy as np
from scipy import sparse

def read_kfile():
    with open('text/output.txt') as f:
         ls = f.read()

    n, numEdges, adjMatrix = ls.splitlines()

    n = int(n)
    numEdges = int(numEdges)

    adjMatrix = map(int, adjMatrix.split(" "))

    return n, numEdges, adjMatrix

def matToCSR(matrix, n):
    
    matrix = list(matrix)
    matrix = np.reshape(matrix, (n,n))
    csr_mat = sparse.csr_matrix(matrix)

    return csr_mat

def CSRtoMat(csr, n):
    matrix = np.reshape(csr.toarray(), (1, n*n))
    return matrix[0] # reshape = [*[0 0 ... 0 0]*]

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
                D[i].append(j) ######### 'malloc'?

    return D

def read_g500_file():
    G = sparse.load_npz("text/test_csr_matrix_000.npz")
    return G

def sssp_simple_serial(D,root):
    # bui prog challenges Dijkstra code
    frontier = []
    visited = {}
    heapq.heappush(frontier, (root,root)) # (0, root, root))
    while frontier:
        source,target = heapq.heappop(frontier) # weight,source,target = heapq.heappop(frontier)

        if target in visited:
            continue
        visited[target] = source

        for neighbor in D[target]:#, cost in D[target].items():
            heapq.heappush(frontier, (target,neighbor)) #(weight+cost, target,neighbor))

    ## reconstruct path ##
    for t in list(D.keys())[1:]:
        path = [] ######### 'malloc'?
        curr = t
        while curr != root:
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

    Q = range(N)

    while len(Q) > 0:
        #print('Q: ', end='')
        #for x in Q: print(x, end=' ')
        #print()

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
                parent[u] = v

    # reconstruct path
     
    for x in range(N):
        if parent[x] == -1: continue
        #print(f'{root} -> {x} = [{root}', end='')
        cnt = d[x]-1
        k = x
        while cnt > 0 and cnt != np.inf:
            #print(f', {parent[k]}', end='')
            k = parent[k]
            cnt = cnt - 1

        #print(f']')

    return (parent, d)

def main():

    '''
    #n, numEdges, adjMatrix = read_kfile()
    #G = matToCSR(adjMatrix, n)
    '''
    # OR
    G = read_g500_file()
    n = len(G.toarray()[0])
    D = CSRtoDict(G)
    root = list(D.keys())[0] #? or search key??
    visited = sssp_simple_serial(D, root)

    print(end='\n\n')

    #'''
    #G = read_g500_file()

    # Parallel: search keys for a handful of random starting points to concurrently run sssp from?

    # Kernel 3
    root = 0 # serial bfs
    parent, d = sssp_g500_serial(G, root)
    print('parent:', end=' ')
    for x in parent: print(x, end=' ')
    print('\nd:', end=' ')
    for x in d: print(x, end=' ')
    print()
    #'''

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
    reg_matrix = CSRtoMat(G, n)
    adjList = matTolist(reg_matrix, n)
    '''
    for k,v in adjList.items():
        print(f'{k}:{v}')
    #'''

    print('\nend')


    return

if __name__ == '__main__':
    main()