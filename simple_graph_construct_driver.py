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

def main():

    #### Generate Edgelist & CSV ####
    filename = 'src/text/edgelist_test_003.txt' # where to save edgelist file
    edgeg500.kronecker_generator(SCALE_TEENY, EDGEF_TEENY, filename)

    edgelist = convert.read_file(filename) # edgelist = [[list of start verts][list of corresponding end verts][weights]]

    ###########################################


    #### Construct Graph  & put into CSV file ####
    edgelist[0] = list(map(int, edgelist[0])) # make start and end verts ints and not floats
    edgelist[1] = list(map(int, edgelist[1]))

    G = multig500.kernel1_g500(edgelist) 

    ###########################################

    with open('src/text/simple_driver_graph_000.txt', 'w') as f:
        with redirect_stdout(f):
            print(G)

    print('Complete')

    return

if __name__ == '__main__':
    main()