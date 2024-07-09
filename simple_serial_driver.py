import networkx as nx
import matplotlib.pyplot as plt
import random as rand
from collections import defaultdict
import numpy as np
from scipy import sparse
import csv
from contextlib import redirect_stdout

import src.convert_graph_formats as convert
import src.edgelist_g500 as edgeg500
import src.graph_construct as multig500
import src.bfs_serial as bfs
import src.sssp_serial as sssp
import validate

## Driver derived from Graph500 driver code ##

# APROX. CUSTOM TEENY #
SCALE_TEENY = 10 # adjust graph size -- 2**scale number of vertices
EDGEF_TEENY = 16
SIZEBFS64TE = 0.00000026
SIZEBFS48TE = 0.00000020

# TOY #
SCALE_TINY = 26
EDGEF_TINY = 16
SIZEBFS64TI = 0.017
SIZEBFS48TI = 0.013

# random seed if you want one

def main():
    NBFS = 16 # number of BFS searches to do

    #### Generate Edgelist & CSV ####
    edgeg500.kronecker_generator(SCALE_TEENY, EDGEF_TEENY)

    edgelist = convert.read_file() # edgelist = [[list of start verts][list of corresponding end verts][weights]]

    ###########################################


    #### Construct Graph  & put into CSV file ####
    edgelist[0] = list(map(int, edgelist[0])) # make start and end verts ints
    edgelist[1] = list(map(int, edgelist[1]))

    G = multig500.kernel1_g500(edgelist) 

    ###########################################


    ######## Search Keys BFS ######## Graph500
    # generate random starting nodes to run BFS & SSSP from

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

    ###########################################


    #### Run Algorithms ####

    for k in range(NBFS):

        parent2 = bfs.bfs_g500_serial(G, search_key[k])

        parent3, d = sssp.sssp_g500_serial(G, search_key[k])

    ###########################################

    with open('src/text/simple_driver_graph_000.txt', 'w') as f:
        with redirect_stdout(f):
            print(G)

    return

if __name__ == '__main__':
    main()