import networkx as nx
import matplotlib.pyplot as plt
import random as rand
import csv
from collections import defaultdict
import heapq
import numpy as np
from scipy import sparse

import mtsim

def sssp_g500_migrate(args): #(F, root):
    G = args['arg1'].toarray()
    root = args['arg2']

    #G = F.toarray() # unpack into a 2d array 

    # N = array of sizes of all the lists in graph I think?
    N = len(G[0]) # N = # of verts / row of matrix I 

    d = [np.inf]*N #### allocate array
    #***************#
    mtsim.mt_array_malloc(d, mtsim.mt_block_cyclic, [0, 2, 16])
    for i,x in enumerate(d): mtsim.mt_array_write(d, i, np.inf) # write

    d[root] = 0 # write
    #***************#
    mtsim.mt_array_write(d, root, 0)

    parent = [-1]*N #### allocate array
    #***************#
    mtsim.mt_array_malloc(parent, mtsim.mt_block_cyclic, [0, 2, 16])
    for i,x in enumerate(parent): mtsim.mt_array_write(parent, i, -1) # write

    parent[root] = root # write
    #***************#
    mtsim.mt_array_write(parent, root, root)

    vist ={}           # don't need to allocate -- not involved in algorithm
    vist[root] = root  # dictionary solely for path tracing and verification

    Q = range(N)       #### allocate array
    #***************#
    mtsim.mt_array_malloc(Q, mtsim.mt_block_cyclic, [0, 2, 16])
    cnt=0
    for i,x in enumerate(parent): 
        mtsim.mt_array_write(parent, i, cnt) # write  
        cnt+=1  

    while len(Q) > 0:
        #print('Q: ', end='')
        #for x in Q: print(x, end=' ')
        #print()

        mini_dist = np.inf
        for i,k in enumerate(Q):
            if d[k] < mini_dist or mini_dist == np.inf:
                mini_ind = i
                mini_dist = d[k] # read
                #***************#
                mini_dist = mtsim.mt_array_read(d, k)

        v = Q[mini_ind] # read
        #***************#
        v = mtsim.mt_array_read(Q, k)

        Q = np.setdiff1d(Q, [v])        #### how to reallocate array ?
        #***************#
        # alloc                         #### might need to be double checked
        # write if value not v
        mtsim.mt_array_malloc(Q, mtsim.mt_block_cyclic, [0, 2, 16])
        cnt=0
        for i,x in enumerate(Q):
            if x != v:
                mtsim.mt_array_write(Q, i, cnt) # write  
            cnt+=1


        I = np.nonzero(G[:][v])[0]      #### allocate array
        #***************#
        mtsim.mt_array_malloc(I, mtsim.mt_block_cyclic, [0, 2, 16])
        cnt = 0
        for j in range(len(G)):
            if G[j][v] != 0:
                mtsim.mt_array_write(I, cnt, j) 
                cnt+=1


        V = G[:][v][I] # G[:][v][I] = all nonzero values in specified col
        #***************#           #### allocate array 
        # for all nonzero vals in all rows of G
        # in column v
        # in I?
        mtsim.mt_array_malloc(V, mtsim.mt_block_cyclic, [0, 2, 16])

        # TODO: unsure how to write to V         

        for k in range(len(I)):
            u = I[k] # read
            #***************#
            u = mtsim.mt_array_read(I, k)

            dist_tmp = d[v] + V[k] # read x2
            #***************# 
            dt1 = mtsim.mt_array_read(d, v)
            dt2 = mtsim.mt_array_read(V, k)
            dist_tmp = dt1 + dt2

            if dist_tmp < d[u]: # read?
                d[u] = dist_tmp
                #***************# # write
                mtsim.mt_array_write(d, u, dist_tmp) # write 

                vist[int(u)] = int(v) # path verification

                parent[u] = v
                #***************# # write
                mtsim.mt_array_write(parent, u, v) # write 

    # reconstruct path
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

    mtsim.mt_die()
    return (parent, d)