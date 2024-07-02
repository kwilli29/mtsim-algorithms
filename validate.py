import random as rand
import csv
from collections import defaultdict
import heapq
import numpy as np
from scipy import sparse

## IGNORE - does not work yet ##

def validate(parent, edgelist, search_key, d, is_sssp):

     out = 0 # 0 no error

     # Remove self edges
     for k, x in enumerate(edgelist):
          if edgelist[0][k] == edgelist[1][k]:
            #edgelist[:][k] = None
            np.delete(edgelist[:], k)

     # Root must be the parent of itself
     if parent[search_key] != search_key:
          out = -1
          return out

     # Find the maximum label for sizing
     N = max(list(map(max,edgelist[0:1]))) + 1 # vertices go from 0 to N-1, +1 for N verts

     slice = []
     for x in parent: 
          if x > -1: slice.append(x)

     # Compute levels and check for cycles

     level = [0]*len(parent)
     P = [0]*len(slice)
     for k in range(len(slice)):
          level[slice[k]] = 1
          P[k] = parent[slice[k]]

     mask = []
     for x in P: 
          if x != search_key: mask.append(x)

     k = 0
     while any(ele >=0 for ele in mask):
          for x in parent: print(x, end=' ')
          print()
          for x in slice: print(x, end=' ')
          print()
          for x in P: print(x, end=' ')
          print()
          for x in mask: print(x, end=' ')
          print()
          for x in level: print(x, end=' ')
          print()
          for j in range(len(mask)):
               level[slice[mask[j]]] = level[slice[mask[j]]] + 1
          
          #P = [0]*len(P) ########## ??? DOUBLE CHECK? -- reset it?
          for j in range(len(P)): # len{P}?
               P[j] = parent[P[j]] # reset P?

          mask = []
          for x in P: 
               if x != search_key: mask.append(x)
          
          k+=1
          if k > N:
               # cycle
               out = -3
               return out

     # Check that there are no edges with only one end in the tree.
     # This also checks the component condition.
     ledge =  np.zeros((len(edgelist)-1, len(edgelist[0])), dtype=int)

     for i,row in enumerate(edgelist[0:2]):
          for j,col in enumerate(row):
               ledge[i][j] = level[col]

     neither_in = [0]*len(ledge[0])
     for x in range(len(ledge[0])):     
          neither_in[x] = ledge[0][x] == 0 & ledge[1][x] == 0

     #neither_in = ledge[0][:] == 0 & ledge[1][:] == 0

     both_in = [0]*len(ledge[0])
     for x in range(len(ledge[0])):
          both_in[x] = ledge[0][x] > 0 & ledge[1][x] > 0

     #both_in = ledge[0][:] >= 0 & ledge[1][:] >= 0 #

     nor_arr = [0]*len(neither_in)
     for x in range(len(neither_in)):
          nor_arr[x] = not(neither_in[x] | both_in[x])

     if any(nor_arr):
          out = -4
          return out

     # Validate the distances/levels
     resp_tree_level = [1]*len(edgelist[0])
     abso = np.absolute(ledge[0][:] - ledge[1][:])

     if not is_sssp:
          resp_tree_level = []
          for x in abso: 
               if x <= 1: resp_tree_level.append(x)
          # resp_tree_level = np.where(abso <= 1, abso)
     else:
          dsub = [0]*len(d[0])
          for x in range(len(d[0])):
               dsub[x] = d[0][x] - d[1][x]
          absod = np.absolute(dsub)

          for r,x in enumerate(absod):
               resp_tree_level[r] = 1 if x <= edgelist[2][r] else 0

     nor_arr = [0]*len(neither_in)
     for x in range(len(neither_in)):
          nor_arr[x] = not(neither_in[x] | resp_tree_level[x])

     if any(nor_arr):
          out = -5
          return out

     return out

def read_file():
     with open('text/edgelist_test_002.txt') as f:
          ls = f.read()

     startVerts, endVerts, weights = ls.splitlines()

     startVerts = map(float, startVerts.split(" ")[:-1])
     endVerts = map(float, endVerts.split(" ")[:-1])
     weights = map(float, weights.split(" ")[:-1])

     edgelist = [startVerts,endVerts,weights]

     return edgelist

def main():
     parent = [17, 1, 7, 7, 25, 1, 124, 1, 5, 13, 41, 1, 7, 1, 143, 25, 302, 1, 13, 13, 64, 5, 1, 7, 302, 1, 25, 181, 65, 181, 1, 111, 955, 13, 95, 7, 1, 1, 64, 1, 181, 1, 1, 64, 13, 64, 95, 5, 1, 25, 181, 1, 1, 25, 1, 79, 1, 11, 390, 111, -1, 67, 369, 547, 1, 1, 1, 1, 64, 64, 64, 37, 302, 13, 172, 51, 64, 95, 5, 1, 1, 5, 1, 111, 37, 295, 302, 7, 1, 7, 1, 647, -1, 250, 95, 1, -1, 7, 176, 37, 17, 25, 64, 206, 1, 82, 135, 547, 222, 7, 1, 1, 130, 7, 512, 222, 302, 302, 302, 135, -1, 229, 5, 302, 1, -1, 9, 5, -1, 7, 1, 1, 5, 1, 130, 1, 64, 7, 302, 48, 17, 302, 181, 1, 25, 36, 25, 54, 30, 37, 302, 5, 37, 48, 1, 17, 65, 80, 111, 481, 1, 30, 95, 17, 56, 64, 5, 302, 302, 111, 143, 25, 1, 188, 172, 706, 1, 64, 294, 184, 95, 1, 547, 1, 1, 7, 926, 265, 1, 730, -1, 104, -1, 25, 1, 1, 229, 131, 372, 65, 54, 1, 246, 302, 216, 302, 1, 64, -1, 176, 295, 531, 229, 143, 39, -1, 1, 111, 1, 302, 1, 42, 1, 1, -1, 17, 64, 7, 695, 1, 1, 65, -1, 64, 5, 1, 382, 33, -1, 64, -1, 1, 294, 1, -1, 130, 1, -1, -1, 220, 1, 1, 7, 1, 1, 275, -1, 22, 64, 7, 7, 1, 135, 1, 7, 5, 5, 339, 133, 124, 254, 339, 181, 17, 7, 1, 547, 1, 1, 181, 11, 130, 254, 30, 294, -1, -1, 183, 1, 1, 48, 1, 25, 67, 1, 1, 135, 7, 154, 302, 1, 25, 1, 104, 1, 1, 104, 181, -1, 36, 25, 172, 819, 5, 51, 137, 42, 17, 479, 254, 302, 48, 111, 5, 130, 25, 229, 302, 11, 37, 64, 65, 520, 17, 278, -1, 33, 7, 48, 1, 520, 104, 1, 79, 1, 708, 5, 723, 770, 275, 1, -1, 1, 7, 278, 181, 447, 1, 894, 920, 567, 302, 5, 1, -1, 64, -1, 65, -1, 1, -1, 1, 1, 339, 261, 5, 1, 1, 5, -1, 3, 65, 1, -1, -1, 7, 1, 48, 64, 7, 1, 447, 181, 82, 130, 181, 599, 681, -1, 1, 1, 1, 1, 48, 1, 130, 512, 866, -1, 181, 254, 1, -1, 25, 1, 113, 5, 64, 599, 302, 996, 953, 339, 25, -1, 1, 1004, 1, 1, 1, -1, 1, -1, 135, 201, 131, 65, 11, 1, 111, -1, -1, 1, 17, 513, 97, -1, 1, -1, 7, 181, 1, 1, 104, 723, 181, -1, 79, 460, 9, 1, 216, 811, 5, 25, 254, 1, 37, 675, 111, 1, 313, 1, -1, -1, -1, 131, -1, 1, 1, 65, 11, 1, 243, 13, 635, 1, 1, 810, 1, 1, -1, -1, -1, -1, -1, 35, 1, -1, 21, -1, 11, 17, 54, -1, 5, 67, -1, -1, 254, -1, 277, 1, 7, 48, 11, 339, 64, 1, 1, 1, 17, 42, 1, 48, 154, 25, 11, 21, 11, 17, 1, 1, 184, 302, 104, 1, 135, 294, 1, 35, 1, 129, 41, -1, 52, 13, 1, 64, 104, 7, 411, 1, 7, 130, 229, -1, 1, 925, 65, 201, 7, 65, 1, 1, 95, 51, 7, 1, 372, 735, 104, -1, 95, -1, -1, 1, 7, 5, 48, 39, 48, 13, 133, 154, 48, 254, 302, 25, 254, 992, 1, -1, 1, 254, 1, 13, 48, 563, 1, 547, -1, 17, 104, 737, 849, -1, 229, -1, 1, 64, 64, 17, 1, 5, 1, 66, 1, 1, 41, -1, 1, 1, 518, 5, 518, 17, 65, 5, 894, 497, -1, -1, 135, 402, 1, 137, 515, -1, -1, 5, 11, 17, 5, 302, 17, 64, 1, 65, 13, 37, 172, 1, 104, 520, 289, 9, 7, 1, 295, 695, 254, 618, 1, 1, 181, 737, 894, 65, 254, -1, -1, 2, 17, 37, 1, 1, 25, -1, 181, 9, 7, 37, -1, -1, 1, -1, -1, 925, 22, -1, 1, 1, 104, 25, 1, 577, 7, 1, 33, 201, 5, 37, 1, 66, 25, 1, 1, 1, 143, 22, 5, 1, 17, 7, 1, 206, 5, 25, -1, -1, 520, -1, 1, -1, 176, 323, 489, 5, 133, 13, 1, 17, -1, 235, 1, 7, 1, 65, 1, 277, 131, 1, 302, 1, 65, 229, 834, 1, 181, -1, -1, -1, 64, 229, 487, -1, 5, 513, 547, -1, 7, 277, 5, -1, 5, 1, 261, -1, 25, 5, 1, 111, 1, 104, 1, -1, 25, 1, 48, 1, 172, 41, 695, 172, 52, 1, 181, 41, 37, 25, 246, 561, 176, 302, 431, -1, 13, -1, 41, -1, 13, 1, 531, 243, 56, 5, -1, 17, 1, 1, 1, -1, 48, 1, -1, 265, 302, 254, 1, 1, 657, 42, 275, 643, 1, 1, 1, -1, -1, 195, -1, 385, 7, 1, 1, -1, 66, 992, 95, 302, 302, 65, 104, 1, 172, 13, 129, 13, 1, 692, 48, 1, -1, 17, 811, 130, 302, 3, 300, 131, -1, 5, 529, -1, 65, 1, 1, 41, 1, 17, 1, -1, 431, 323, 41, 1, 344, -1, 113, 129, 54, 67, -1, -1, -1, 7, 67, 1, -1, -1, -1, 1, 17, 1, -1, -1, 1, 1, 67, 497, 64, 64, 17, 5, 183, 5, -1, -1, 181, 1, 275, 302, 302, 460, 131, 1, 1, 1, 17, 1, 254, 1, 5, 1, 1, 1, -1, 1, 1, 253, 302, 447, 520, 201, 1, 1, 66, -1, -1, 33, 411, 1, 259, 5, -1, 1, 235, 2, 302, 130, 1, -1, 1, -1, 1, 1, 1, 1, -1, -1, 66, 1, 133, -1, 695, -1, -1, 1, 561, 104, -1, 131, 302, 955, 1, -1, 1, 17, -1, 17, 1, 5, -1, -1, 1, 42, 1, 1, -1, 1, 1, 1, 1, 25, 706, 7, 2, -1, -1, -1, -1, 1, 65, 1, 5, -1, 1, 1, 51, 181, -1, -1, 263, 21, -1, -1, 1, -1, -1, 275, 1, 3, 54]
     edgelist = read_file()
     edgelist[0] = list(map(int, edgelist[0])) # make start and end verts ints
     edgelist[1] = list(map(int, edgelist[1]))
     search_key = 1
     d = 0
     is_sssp = False
     out = validate(parent, edgelist, search_key, d, is_sssp)

     if not out:
          print('Graph Valid :D')

     else:
          print(f'Error out: {out} D:')


if __name__ == '__main__':
     main()