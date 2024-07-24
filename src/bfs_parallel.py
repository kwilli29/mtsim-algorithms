import networkx as nx
import matplotlib.pyplot as plt
import random as rand
import csv
from collections import defaultdict
import numpy as np
from scipy import sparse

import mtsim
import src.convert_graph_formats as convert

## This file is a Breadth First Search Algorithm weaving MTSim functions in it for 'parallel' simulation ##

def bfs_g500_migrate(args): #(F, root):

    G = args['arg1'].toarray()
    root = args['arg2']

    #G = F.toarray() # unpack into a 2d array  -- IGNORE FOR MTSIM

    # N = array of sizes of all the lists in graph
    N = len(G[0]) # N = # of verts / row of matrix

    parent = [-1]*N 
    #***************#
    # mtsim.mt_array_malloc(parent, mtsim.mt_single, [mtsim.current_node]) # allocate vector
    mtsim.mt_array_malloc(parent, mtsim.mt_block_cyclic, [0, 2, 16])
    for i,x in enumerate(parent): mtsim.mt_array_write(parent, i, -1) # write

    parent[root] = root
    #***************#
    mtsim.mt_array_write(parent, root, root) # write

    to_visit = [0]*N # allocate vector
    #***************#
    mtsim.mt_array_malloc(to_visit, mtsim.mt_block_cyclic, [0, 2, 16])
    for i,x in enumerate(to_visit): mtsim.mt_array_write(to_visit, i, 0) # write

    to_visit[0] = root
    #***************#
    mtsim.mt_array_write(to_visit, 0, root) # write

    lastk = 1
    for k in range(N):
        v = to_visit[k]
        #***************#
        v = mtsim.mt_array_read(to_visit, k)

        if v == 0: break
        I = np.nonzero(G[:][v])[0] # vector allocated
        #***************#
        mtsim.mt_array_malloc(I, mtsim.mt_block_cyclic, [0, 2, 16])
        cnt = 0
        for j in range(len(G)):
            # G[j][v] READ 
            if G[j][v] != 0: # if G[j][v] != 0:
                #***************#
                mtsim.mt_array_write(I, cnt, j) 
                cnt+=1

        next = [] #  'malloc'
        #***************#
        mtsim.mt_array_malloc(next, mtsim.mt_block_cyclic, [0, 2, 16])
        cnt = 0

        # for i in I:
        #***************#
        for j in range(len(I)):
            i = mtsim.mt_array_read(I, j)

            #compare_parenti = parent[i]
            #***************#
            compare_parenti = mtsim.mt_array_read(parent, i)
            if compare_parenti == -1:

                parent[i] = v
                #***************#
                mtsim.mt_array_write(parent, i, v)

                next.append(i)  # have a list of next vertices
                #***************#
                mtsim.mt_array_write(next, cnt, i)
                cnt+=1

        nums = list(range(lastk, len(next)+lastk))
        #***************#
        mtsim.mt_array_malloc(nums, mtsim.mt_block_cyclic, [0, 2, 16])
        for j in range(lastk, len(next)+lastk): mtsim.mt_array_write(nums, j-lastk, j)

        for k, x in enumerate(nums): 
            to_visit[x] = next[k] # add vertices to the to_visit list
            #***************#
            mtsim.mt_array_write(to_visit, x, mtsim.mt_array_read(next, k))

        lastk = lastk + len(next)

    # Print out Root, list of parents -- parent[x]=parent of vertex x, to_visit is just a list of how it viisited nodes and doesn't hold much valuable info
    print(f'Root: {root}')
    print('Parent: [')
    for x in parent: print(x, end=' ')
    print(']\nVisit: [')
    for x in to_visit: print(x, end=' ')
    print(']')

    mtsim.mt_die()
    return parent

    ## TODO: Think of better way to keep track of info ##

def bfs_trad_parallel(CSR, n, dist, frontier, fsize): # fcn itself called parallel, but also employs cilk_for
    frontier_bits = [0]*n # new / malloc
    size = [0]*n          # new / malloc

    for i in range(n): # cilk for 
        if dist[i] == -1:

            for neigh_i in range(CSR[0][i], CSR[0][i+1]): # regular for
                ngh = CSR[1][neigh_i]

                if frontier[ngh]:
                    dist[i] = dist[ngh] + 1
                    size[i] = 1
                    break
    
    # calc new sizes?
    # prefix sum of size array? compute frontier size in memory blocks? -- block cyclic memory?
    fsize = size[n-1]

    # free memory?
    # delete size

    return frontier_bits

def bfs_multithread(CSR, s):
    v = len(CSR[0]) # num of vertices -- DOUBLE CHECK

    # for in parallel?
    d = [-1]*v # ? 
    #***************#
    mtsim.mt_array_malloc(d, mtsim.mt_block_cyclic, [0, 2, 16])

    d[s] = 0
    #***************#
    mtsim.mt_array_write(d, s, -1)

    # mt_array_malloc?
    Q = [] # malloc ? 
    Q.append(s) # push s to Q
    indexQ = 0 # pseudo pointer
    #***************#
    mtsim.mt_array_malloc(Q, mtsim.mt_block_cyclic, [0, 2, 16])
    mtsim.mt_array_write(Q, 0, s)


    while Q: # while Q[indexQ] is an existing value?
        for k, u in enumerate(Q):  # parallel - read?

            Q.pop(0) # pop front I think
            # read_Q = mtsim.mt_array_read(Q, k)

            for neigh in CSR[:][u]:   # parallel # for all v's adj to u

                #***************#
                dist_neigh = mtsim.mt_array_read(d, neigh, False) # thread safe read
                # read
                if dist_neigh ==-1: # if d[neigh] == -1:
                    d[neigh] = d[u] +1
                    #***************#
                    mtsim.mt_array_write(d, neigh, mtsim.mt_array_read(d,u)+1)

                    indexQ+=1       # pseudo pointer
                    Q.append(neigh) # must be thread-safe
                    # write
                    #***************#
                    mtsim.mt_array_write(Q, indexQ, neigh) # thread safe write

                    # atomic d update?
                else:
                    d[neigh] = dist_neigh
                    #***************#
                    mtsim.mt_array_write(d, neigh, dist_neigh) # thread safe write

    mtsim.die()
    return


def bfs_parallel_2d(A, s):
    frontier = [0]*(len(A)**0.5)
    frontier[s] = s

    t = [0]*(len(A)**0.5) # prob not right but for now
    pi = [0]*(len(A)**0.5) # prob not right but for now

    P = [range(10), range(10)] # processors

    n = len(P)

    for i, processor_row in enumerate(P):                 # parallel for
        for j, processor_col in enumerate(processor_row): # parallel for
            single_index = (n*i) + j
            while frontier:
                transpose_vector(frontier[single_index])  

                frontier[processor_row] = all_gather_v(frontier[single_index], P[:][j])

                t[i] = A[i][j] * frontier[i] # some sort of matrix op idk

                t[single_index] = all_to_all_v(t[i], P[i][:])
                t[single_index] = t[single_index] * conjugate(pi[single_index]) # some sort of matrix op idk, **tranpose or conjugate

                pi[single_index] = pi[single_index] + t[single_index]

                frontier[single_index] = t[single_index]
    
    def transpose_vector(f):pass
    def all_gather_v(f, p):pass
    def all_to_all_v(f, p):pass
    def conjugate(m): pass

def main():

    G = convert.read_g500_file('text/test_csr_matrix_000.npz')
    root = 0

    bfs_multithread(G.toarray(), root)

    return

    dist = [-1]*n       # cilk_for
    dist[root] = 0

    fsize = 1
    frontier = [0]*n  # new / malloc pointer int[fsize]

    frontier[0] = root # ?

    n = len(CSR[0])

    while fsize > 0:
        
        frontier = bfs_trad_parallel_2(CSR, n, dist, frontier, fsize)

if __name__ == '__main__':
    main()


