import networkx as nx
import matplotlib.pyplot as plt
import random as rand
import numpy as np
from scipy import sparse
from collections import defaultdict
import csv

import convert_graph_formats as convert

def random_graph_gen(n, G): # not Tree

    # n == rand number of nodes (by hundreds for now)

    # rand number of edges
    randEdges = rand.randint(0, (n*(n-1))) # max edges = n*n-1

    print(f"{n}")
    print(f"{randEdges}")

    # rand verts
    for edge in range(randEdges):
        addEdge = False

        randx = rand.randint(0, n-1)
        randy = rand.randint(0, n-1)
        vert = (randx, randy)

        while not addEdge: # while so true amount of edges is added
            if vert not in G and randx != randy: # vertice not added yet and not self vert
                G.add_edge(randx, randy)
                addEdge = True
            else:         # if edge not added, try again
                randx = rand.randint(0, n-1)
                randy = rand.randint(0, n-1)
                vert = (randx, randy)
                addEdge = False
  
    adjMatrix = [0]*(n*n)

    for x, nbrs in G.adj.items():
        for nbr, eattr in nbrs.items():
            adjMatrix[(x*n)+nbr] = 1
            #print(f"({x}, {nbr})", end=' ')   
     
    #l=[(n, nbrdict) for n, nbrdict in G.adjacency()]
    #print(l)     

    # Matplot draw graph            
    #fig, ax = plt.subplots()
    #pos = nx.random_layout(G)
    #nx.draw_networkx(G, pos=pos, ax=ax)
    #ax.set_title(f"DiGraph n={n}, num_edges={randEdges}")
    #plt.show()

    return adjMatrix

def print_dG(n, adjMatrix):
    #print('[', end='')
    for cnt, i in enumerate(adjMatrix):
        if cnt == (n*n)-1: # if last number, don't put comma at end
            print(i, end='')
            continue
        print(i, end=' ') # defualt print #, 
        #if cnt%(n-1) == 0 and cnt != 0: # if at end of line, newline
        #    print()
    #print(']')
    return
    
def kernel1_g500(edgelist):
    
    # Remove self edges
    for k, x in enumerate(edgelist):
        if edgelist[0][k] == edgelist[1][k]:
            #edgelist[:][k] = None
            np.delete(edgelist[:], k) 

    # Find the maximum label for sizing
    N = max(list(map(max,edgelist[0:1]))) + 1 # vertices go from 0 to N-1, +1 for N verts

    # Create matrix & make sure it's square

    # F = sparse.csr_matrix((np.ones((len(edgelist[0]),), dtype=int), (edgelist[0], (edgelist[1]))), shape=(N,N), dtype=float)
    FW = sparse.csr_matrix((list(edgelist[2]), (edgelist[0], (edgelist[1]))), shape=(N,N), dtype=float)

    # Symmetrize to model an undirected graph
    FW = FW + FW.transpose()
    H = FW.copy().tocsr()
    G = H
    
    # G[G != 0] = 1         # turn vertex matrix values into 1s so graph is undirected?

    DictG = convert.CSRtoDict(G) # generates CSV file of graph
    convert.dictToCSV(DictG)

    return G

def main():

    ## Graph 500 Generator Method 1 ##
    edgelist = convert.read_file()

    edgelist[0] = list(map(int, edgelist[0])) # make start and end verts ints
    edgelist[1] = list(map(int, edgelist[1]))
    
    G = kernel1_g500(edgelist)

    sparse.save_npz("text/test_csr_matrix_000.npz", G)

    # Generation Method 2 -- IGNORE
    #plt.clf()
    #G = nx.DiGraph()
    #node = rand.randint(1,9)
    #n = node * 100
    #adjMatrix = random_graph_gen(n, G)
    #print_dG(n, adjMatrix)


if __name__ == '__main__':
    main()
