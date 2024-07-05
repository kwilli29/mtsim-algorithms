import networkx as nx
import matplotlib.pyplot as plt
import random as rand
import csv
from collections import defaultdict
import numpy as np
from scipy import sparse

import mtsim

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
    #mtsim.mt_array_malloc(to_visit, mtsim.mt_single, [mtsim.current_node]) # allocate vector
    mtsim.mt_array_malloc(to_visit, mtsim.mt_block_cyclic, [0, 2, 16])
    for i,x in enumerate(to_visit): mtsim.mt_array_write(to_visit, i, 0) # write

    to_visit[0] = root
    #***************#
    mtsim.mt_array_write(to_visit, 0, root) # write

    lastk = 1 # 0?, 1 I thknk
    for k in range(N):
        v = to_visit[k]
        #***************#
        v = mtsim.mt_array_read(to_visit, k)

        if v == 0: break
        I = np.nonzero(G[:][v])[0] # vector allocated
        #***************#
        #mtsim.mt_array_malloc(I, mtsim.mt_single, [mtsim.current_node])
        mtsim.mt_array_malloc(I, mtsim.mt_block_cyclic, [0, 2, 16])
        cnt = 0
        for j in range(len(G)):
            # G[j][v] READ
            if G[j][v] != 0:
                mtsim.mt_array_write(I, cnt, j) 
                cnt+=1

        next = [] #  'malloc'
        #***************#
        #mtsim.mt_array_malloc(next, mtsim.mt_single, [mtsim.current_node])
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
        #mtsim.mt_array_malloc(nums, mtsim.mt_single, [mtsim.current_node])
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