import networkx as nx
import matplotlib.pyplot as plt
import random as rand
from collections import defaultdict
import numpy as np
from scipy import sparse
import csv
from contextlib import redirect_stdout

import edgelist_g500 as edgeg500
import graph_construct as multig500
import bfs.bfs_serial as bfs
import sssp.sssp_serial as sssp
import validate

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

def CSRtoDict(csr):
    csr = csr.toarray()
    D = defaultdict(list)

    for i, row in enumerate(csr):
        for j, num in enumerate(row):
            if num:
                D[i].append((j, float(csr[i][j]))) #

    fields = ['node1', 'node2', 'weight']
    filename = 'csv/graph_generation_001.csv'

    with open(filename, 'w') as csvfile:
        # creating a csv dict writer object
        writer = csv.writer(csvfile)

        # writing headers (field names)
        writer.writerow(fields)

        # write rows - node1, node2, weight
        for k, v in D.items():
            for x in v:
                writer.writerow([k, x[0], x[1]])

    return D

def main():
    NBFS = 16 # number of BFS searches to do

    #### Generate Edgelist ####
    edgeg500.kronecker_generator(SCALE_TEENY, EDGEF_TEENY)

    edgelist = read_file() # edgelist = [[list of start verts][list of corresponding end verts][weights]]
    
    '''for x in edgelist:
        for k in x:
            print(k, end=' ')
        print(end='\n\n') '''

    #### Construct Graph  & put into CSV file ####
    edgelist[0] = list(map(int, edgelist[0])) # make start and end verts ints
    edgelist[1] = list(map(int, edgelist[1]))

    # k1 time start
    G = multig500.kernel1_g500(edgelist) 
    # k1 time end

    #### Search Keys BFS #### Graph500
    N = len(G.toarray()[0])

    coldeg = [0]*N # counts of nonzeroes per column

    for j in range(N):
       coldeg[j] = len(np.nonzero(G[:][j])[0])

    search_key = np.random.permutation(N)
    
    # Remove values in search key where the column degrees are 0 -- they're not connected to anything
    for k, x in enumerate(search_key): # sk[0]\sk[1] OR where coldeg is 0?
        if coldeg[search_key[k]] == 0: # where coldeg==0, eliminates corresponding value in search_key
            np.delete(search_key, k)          # search_key[k]=vertex, if coldeg[vertex] is zero, it's not connected to anything and should be taken out of search keys
    if len(search_key) > NBFS:  
        search_key = search_key[0:NBFS]
    else:
        NBFS = len(search_key)

    #k2 time = [np.inf]*NBFS
    #k2 nedge = [0]*NBFS
    #k3 time = [np.inf]*NBFS
    #k3 nedge = [0]*NBFS

    #indeg = [0]*len(edgelist[0]) # idk???
    #for i,row in enumerate(edgelist):
    #    indeg[i] = np.digitize(row, range(N)) # histc (ijw(:), 1:N)

    for k in range(NBFS):
        #k2 time start
        parent2 = bfs.bfs_g500_serial(G, search_key[k])
        #k2 time end
        err = 0 # validate.validate(parent2, edgelist, search_key[k], 0, False)
        if err < 0:
            print()
            #print(f"BFS {k} from search key {search_key[k]} failed to validate: ")
        
        # k2_nedge[k] = sum([x if x >= 0 for x in parent2])/2 # ???? 'Volume/2'

        # k3 start time
        parent3, d = sssp.sssp_g500_serial(G, search_key[k])
        # k3 end time
        err = 0 # validate.validate(parent3, edgelist, search_key[k], d, True)
        if err < 0:
            print()
            #print(f'SSSP {k} from search key {search_key[k]} failed to validate: {err}')
        
        # k3_nedge[k] = sum([x if x >= 0 for x in parent3])/2 # ???? 'Volume/2'
    
    # METRICS: SCALE, NBFS, k1_time, k2_time, k2_nedge, k3_time, k3_nedge

    with open('text/driver_graph_000.txt', 'w') as f:
        with redirect_stdout(f):
            print(G)

    return

if __name__ == '__main__':
    main()