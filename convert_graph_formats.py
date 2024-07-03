import networkx as nx
import matplotlib.pyplot as plt
import random as rand
import csv
from collections import defaultdict
import heapq
import numpy as np
from scipy import sparse

import edgelist_g500 as edgeg500
import graph_construct as multig500

def read_kfile(filename):
    # read in file of:

    # N
    # num_edges
    # adj_matrix

    with open(filename) as f:
         ls = f.read()

    n, numEdges, adjMatrix = ls.splitlines()

    n = int(n)
    numEdges = int(numEdges)

    adjMatrix = map(int, adjMatrix.split(" "))

    return n, numEdges, adjMatrix

def read_file(filename):
    # read in file of g500 edgelist format

    with open(filename) as f:
         ls = f.read()

    startVerts, endVerts, weights = ls.splitlines()

    startVerts = map(float, startVerts.split(" ")[:-1])
    endVerts = map(float, endVerts.split(" ")[:-1])
    weights = map(float, weights.split(" ")[:-1])

    edgelist = [startVerts,endVerts,weights]

    return edgelist

def matToCSR(matrix, n):
    # convert a matrix to CSR

    matrix = list(matrix)
    matrix = np.reshape(matrix, (n,n))
    csr_mat = sparse.csr_matrix(matrix)

    return csr_mat

def CSRtoMat(csr, n):
    # Convert CSR to 1D matrix

    matrix = np.reshape(csr.toarray(), (1, n*n))
    return matrix[0] # reshape = [*[0 0 ... 0 0]*]

def matTolist(matrix, n):
    # convert a matrix to adjacency list
    # matrix = generator object of some type
    matrix = list(matrix)

    adjList = defaultdict(list)

    for index, k in enumerate(matrix):
        
          i = index//n
          j = index%n

          if k != 0:
            adjList[i].append(j)

    return adjList

def CSRtoDict(csr):
    # Convert CSR graph to Dictionary

    csr = csr.toarray()
    D = defaultdict(list)

    for i, row in enumerate(csr):
        for j, num in enumerate(row):
            if num:
                D[i].append((j, float(csr[i][j])))

    return D

def read_g500_file(filename):
    G = sparse.load_npz(filename)
    return G

def read_csv_file(N):
    # read in csv file - take in number of vertices
    # sparse matrix = [i][j] = weight
    sep=','
    i = []
    j = []
    w = []
    with open('csv/graph_generation_000.csv', mode ='r')as file:
        csvFile = csv.reader(file)
        headers = next(csvFile, None)
        for data in csvFile:
            i.append(int(data[0]))
            j.append(int(data[1]))
            w.append(float(data[2]))

    G = sparse.csr_matrix((w, (i, j)), shape=(N, N), dtype=float) 

    return G
