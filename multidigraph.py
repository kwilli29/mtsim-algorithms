import networkx as nx
import matplotlib.pyplot as plt
import random as rand
import numpy as np
from scipy import sparse

def read_file():
    with open('text/edgelist_test_002.txt') as f:
         ls = f.read()

    startVerts, endVerts, weights = ls.splitlines()

    startVerts = map(float, startVerts.split(" ")[:-1])
    endVerts = map(float, endVerts.split(" ")[:-1])
    weights = map(float, weights.split(" ")[:-1])

    edgelist = [startVerts,endVerts,weights]

    return edgelist

def digraphGen(n, G): # not Tree

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
    
def kernel1_g500(edgelist): # Tree?
    
    # Remove self edges
    for k, x in enumerate(edgelist):
        if edgelist[0][k] == edgelist[1][k]:
            #edgelist[:][k] = None
            np.delete(edgelist[:], k) 

    # Find the maximum label for sizing
    N = max(list(map(max,edgelist[0:1]))) + 1 # vertices go from 0 to N-1, +1 for N verts

    # Create matrix & make sure it's square

    F = sparse.csr_matrix((np.ones((len(edgelist[0]),), dtype=int), (edgelist[0], edgelist[1])), shape=(N,N), dtype=int)


    # Symmetrize to model an undirected graph
    F = F + F.transpose() # get the undirected graph?
    H = F.copy().tocsr()
    G = H
    
    G[G != 0] = 1         # turn vertex matrix values into 1s so graph is undirected?

    return G


def main():
    # Generation Method 1 -- IGNORE
    # plt.clf()
    #G = nx.DiGraph()
    #node = rand.randint(1,9)
    #n = node * 100
    #adjMatrix = digraphGen(n, G)
    #print_dG(n, adjMatrix)

    ## Graph 500 Generator Method 2 ##
    edgelist = read_file()

    edgelist[0] = list(map(int, edgelist[0])) # make start and end verts ints
    edgelist[1] = list(map(int, edgelist[1]))

    '''
    for x in edgelist:
        for k in x:
            print(k, end=" ")
        print(end="\n\n") 
    #'''
    
    G = kernel1_g500(edgelist)
    #for x in G.toarray(): # 2d array of 1s for edges and 0s
    #    print(x, end=' ')
    # print(G)

    sparse.save_npz("text/test_csr_matrix_000.npz", G)


if __name__ == '__main__':
    main()
