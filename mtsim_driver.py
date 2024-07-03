import networkx as nx
import matplotlib.pyplot as plt
import random as rand
from collections import defaultdict
import numpy as np
from scipy import sparse

import edgelist_g500 as edgeg500
import graph_construct as multig500
import bfs.bfs_parallel as bfs
import sssp.sssp_parallel as sssp

import mtsim

# APROX. CUSTOM TEENY #
SCALE_TEENY = 10
EDGEF_TEENY = 16
SIZEBFS64TE = 0.00000026
SIZEBFS48TE = 0.00000020

# TOY #
SCALE_TINY = 26
EDGEF_TINY = 16
SIZEBFS64TI = 0.017
SIZEBFS48TI = 0.013

# random seed if you want one

def read_file():
    with open('text/edgelist_test_003.txt') as f:
         ls = f.read()

    startVerts, endVerts, weights = ls.splitlines()

    startVerts = map(float, startVerts.split(" ")[:-1])
    endVerts = map(float, endVerts.split(" ")[:-1])
    weights = map(float, weights.split(" ")[:-1])

    edgelist = [startVerts,endVerts,weights]

    return edgelist

def drive_bfs(args):
    # bfs(G, root)
    # args = {'arg1': <G_csr>, 'arg2': [root1, root2 ...]}

    #mt_for_all(bfs.bfs_g500_serial, args, i, args['arg2'])# ?

    for x in args['arg2']: # since no for all

        mtsim.mt_spawn(bfs.bfs_g500_migrate, {'arg1': args['arg1'], 'arg2': x})
    
    # where do returns go?

    mtsim.mt_die()

    return

def drive_sssp(args):
    # sssp(G, root)
    # args = {'arg1': <G_csr>, 'arg2': [root1, root2 ...]}

    #mt_for_all(bfs.bfs_g500_serial, args, i, args['arg2'])# ?

    for x in args['arg2']: # since no for_all

        mtsim.mt_spawn(sssp.sssp_g500_migrate, {'arg1': args['arg1'], 'arg2': x})
    
    # where do returns go?

    mtsim.mt_die()

    return

def main():
    NBFS = 16 # number of BFS/SSSP searches to do 

    #### Generate Edgelist ####
    edgeg500.kronecker_generator(SCALE_TEENY, EDGEF_TEENY)
    print('Edgelist generated')

    edgelist = read_file() # edgelist = [[list of start verts][list of corresponding end verts][weights]]
    
    # print edgelist
    '''for x in edgelist:
        for k in x:
            print(k, end=' ')
        print(end='\n\n') '''

    #### Construct Graph ####
    edgelist[0] = list(map(int, edgelist[0])) # make start and end verts ints
    edgelist[1] = list(map(int, edgelist[1])) # keep generated weights floats

    G = multig500.kernel1_g500(edgelist)
    print('Graph Constructed')

    #### Search Keys BFS #### - Graph500 method
    N = len(G.toarray()[0])

    coldeg = [0]*N # counts of nonzeroes per column

    for j in range(N):
        coldeg[j] = len(np.nonzero(G[:][j])[0])

    search_key = np.random.permutation(N)    

    # Remove values in search key where the column degrees are 0 -- they're not connected to anything
    for k, x in enumerate(search_key): #### Double Check: sk[0]\sk[1] OR where coldeg is 0?
        if coldeg[search_key[k]] == 0: # where coldeg==0, eliminates corresponding value in search_key
            np.delete(search_key, k)          # search_key[k]=vertex, if coldeg[vertex] is zero, it's not connected to anything and should be taken out of search keys

            
    if len(search_key) > NBFS:  
        search_key = search_key[0:NBFS]
    else:
        NBFS = len(search_key)


    # Level 1 Nodes = search_key

    # OR choose a root and put children in level1_array
    # This commented out chunk is a second potential way tp get start values for a BFS
    '''rand_root = rand.randint(0, N-1)

    level1_rand_nodes = [] ######### 'malloc'?
    #***************#
    #mtsim.mt_array_malloc(level1_rand_nodes, mtsim.mt_block_cyclic, [0,16,1])

    I = np.nonzero(G[:][rand_root])[1]
    for i in I:
        level1_rand_nodes.append(i)  # and THESE are the level 1 nodes
    #***************#
    #cnt=0
    #for i in G[:][rand_root]:
    #    if i != 0: 
    #        mtsim.mt_array_write(level1_rand_nodes, cnt, i)
    #        cnt+=1
            
        
    if len(level1_rand_nodes) > NBFS:  
        level1_rand_nodes = level1_rand_nodes[0:NBFS]
        #***************#
        # idk about the 'shortening'
    else:
        NBFS = len(level1_rand_nodes)
    print(f'{rand_root}: {level1_rand_nodes}') '''

    print('Arranged chosen starting nodes')

    args = {'arg1': G, 'arg2': search_key}
    # OR
    #args = {'arg1': G, 'arg2': level1_rand_nodes} # if second method used

    # allocate NBFS search keys - 1/node

    mtsim.mt_run(drive_bfs, args, 0, 0, 16)

    mtsim.mt_run(drive_sssp, args, 0, 0, 16)


    # METRICS: SCALE, NBFS, k1_time, k2_time, k2_nedge, k3_time, k3_nedge
    with open('text/driver_graph_002.txt', 'w') as  d:
        print(G, file=d)

    return


if __name__ == '__main__':
    main()