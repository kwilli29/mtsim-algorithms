import networkx as nx
#import matplotlib.pyplot as plt
import random as rand
import numpy as np
import csv
import convert_graph_formats as convert

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

def kronecker_generator(SCALE, edgefactor):
    # Set number of verts N and edges M
    N = 2**SCALE
    M = edgefactor*N

    # Set initiator probabilities
    init_probs = [0.57, 0.19, 0.19]
    A, B, C = init_probs

    # Create index arrays
    # return_array = [[1]*M]*3
    return_array = np.ones((3, M), dtype=float)

    #  Loop over each order of bit 
    ab = A + B
    c_norm = C/(1-(A+B))
    a_norm = A/(A+B)

    # Compare w/ probabilities and set bits of inidicies
    #print('Compare w/ probabilities')
    for bit_i in range(1, SCALE+1):
        #print(bit_i)

        randib = np.random.random_sample((M,))  # generate random 1d array every cycle
        randjb = np.random.random_sample((M,))

        ii_bit = [1 if i > ab else 0 for i in randib] # create some sort of random 1/0 mapping

        jj_bit = [1 if j > ( c_norm*ii_bit[k] + (a_norm*(int(ii_bit[k]) ^ 1)) ) else 0 for k,j in enumerate(randjb)]
        # different A,B,C values affect how generally high/lox the numbers are in i&j

        iijj_arr = np.array([ii_bit,jj_bit])

        scalar_iijj_arr = np.multiply((2**(bit_i-1)), iijj_arr) # make the numbers not 0 or 1
 
        return_array[0][:] = return_array[0][:] + scalar_iijj_arr[0]   # create & accum. random assortment of numbers in row 0 and 1
        return_array[1][:] = return_array[1][:] + scalar_iijj_arr[1]

        #return_array[0:1][:] = return_array[0:1][:] + scalar_iijj_arr # np.multiply((2**(bit_i-1)), iijj_arr[0:1])

        # [ [...] [...] ]         [ [...] [...] ]
    # print(return_array)

    # Generate weights
    #print('Generate weights')
    return_array[2] = np.random.uniform(0, 1, M)

    # Permute vertex labels
    #print('Permute vertex labels')
    p = np.random.permutation(N)

    for i, rows in enumerate(return_array[0:1]):  # unsure if this is correct - but I think it is
        for j, cols in enumerate(rows):
            if int(return_array[i][j]) == 1024:
                print(int(return_array[i][j]))
                print(return_array[i][j])
                print(i, j)
                exit()
            return_array[i][j] = p[int(return_array[i][j])]

    # return_array[0:1][:] = p[return_array[0:1][:]]

    # Permute edgelist
    #print('Permute edgelist')
    p = np.random.permutation(M)

    for i, rows in enumerate(return_array):      # unsure if this is correct - but I think it is
        for j, cols in enumerate(rows):
            return_array[i][j] = return_array[i][p[j]]

    # return_array = return_array[:][p]

    # Adjust to zero-based labels
    # print('No need to zero-based labels in Python')

    with open('text/edgelist_test_003.txt', 'w') as f:
        for x in return_array:
            for k in x:
                print(k, end=' ', file=f)
            print(file=f)

    return return_array


def main():

    # edgelist = kronecker_generator(SCALE_TINY, EDGEF_TINY)
    edgelist = kronecker_generator(SCALE_TEENY, EDGEF_TEENY)
    
    convert.edgelistToCSV(edgelist)

    #for x in edgelist:
    #    for k in x:
    #        print(k, end=' ')
    #    print()

if __name__ == '__main__':
    main()
