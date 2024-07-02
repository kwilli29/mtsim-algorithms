# runtime_support: basic routines to manage state

# Initialize global variables
thread_matrix = {}
node_matrix = []
migration_matrix = []
remote_matrix = []
runnable = []
current_tid = None
current_node = 3
num_nodes = 0
runtime = {}

# This routine runs an mt-threaded program
# It executes mt-threads one at a time until there are no more
def mt_run(fcn, args, tid, node, nodes):
    # start an mt-thread with the specified tid on node node in a system with nodes nodes in it
    global thread_matrix, node_matrix, migration_matrix, remote_matrix
    global runnable # stack of runnable states
    global current_tid, current_fcn, current_node, num_nodes
    runnable = [] # clear the stack
    runnable.append((fcn, args, tid, node)) # add first_thread
    thread_matrix[tid] = 1
    # initialize
    num_nodes = nodes
    node_matrix = [0] * num_nodes # initialize node_matrix with zeros
    migration_matrix = [[0] * num_nodes for _ in range(num_nodes)] # initialize migration matrix
    # initialize the statistics matrices
    # mt_clear_stats()
    # Basic loop to execute mt-threads as long as runnable not empty
    while len(runnable) != 0:
        # run the top mt-thread
        new_thread = runnable.pop() # remove it from stack
        # extract the components of the thread to be run
        next_fcn = new_thread[0]
        current_tid = new_thread[2]
        current_node = new_thread[3]
        current_args = new_thread[1]
        print("Starting new thread ", current_tid, " on node ", current_node)
        # now run that thread
        next_fcn(current_args)
    # print out the stats
    # mt_stats()

# terminate current thread called as last executable statement in an mt-thread code function
def mt_die():
    global current_tid, current_fcn, current_node, num_nodes
    # record which node the current thread died on
    # then print out message
    print("Thread ", current_tid, " died on node ", current_node)

def get_new_tid():
    return len(thread_matrix)

def mt_spawn(thread_body, args):
    global current_node, current_tid
    new_tid = get_new_tid()
    runnable.append((thread_body, args, new_tid, current_node)) # stack the new thread
    thread_matrix[new_tid] = 1 # record new thread's birth
    if current_node >= len(node_matrix):
        node_matrix.append(0)
    node_matrix[current_node] += 1 # update statistics on the node where it was born

def mt_array_malloc(variable, map_fcn, map_parameters):
    global runtime
    runtime[id(variable)] = (map_fcn, map_parameters)
    
def mt_block_cyclic(map_parameters, i):
    s, b, l = map_parameters
    block_number = i // b
    node_offset = block_number % l
    node = (s + node_offset) % l
    return node

def mt_single(map_parameters):
    node = map_parameters[0]
    return node

def mt_array_read(x, i):
    global current_node, migration_matrix
    map_fcn, map_parameters = runtime[id(x)]
    if len(map_parameters) == 3:
        node = map_fcn(map_parameters, i)
    else:
        node = map_fcn(map_parameters)
    if node != current_node:
        migration_matrix[current_node][node] = 1
        current_node = node 
    return x[i]

def mt_array_write(x, i, v):
    global current_node, migration_matrix
    map_fcn, map_parameters = runtime[id(x)]
    if len(map_parameters) == 3:
        node = map_fcn(map_parameters, i)
    else:
        node = map_fcn(map_parameters)
    if node != current_node:
        print(f"Migration: Thread {current_tid} migrating from node {current_node} to node {node}")
        migration_matrix[current_node][node] = 1
        current_node = node
    x[i] = v

# simple test
args = {"arg1": 1, "arg2": 2}

def example0(x):
    print(x)
    mt_die()

def example_spawn(args):
    mt_spawn(example0, args) # thread 1
    mt_spawn(example0, args) # thread 2
    mt_spawn(example0, args) # thread 3
    mt_spawn(example0, args) # thread 4
    mt_die()


def main():
    mt_run(example_spawn, args, 0, 0, 16)

    # Allocate an array with block-cyclic mapping
    example_array_cyclic = list(range(20))
    mt_array_malloc(example_array_cyclic, mt_block_cyclic, [0, 2, 16])

    # Allocate an array with single-node mapping
    example_array_single = list(range(20, 40))
    mt_array_malloc(example_array_single, mt_single, [3])

    # Access the block-cylic variable
    print("Block-cylic mapping:")
    for i in range(10):
        node = mt_block_cyclic([0, 2, 16], i) 
        print(f"Component {i} of example_array_cyclic is on node {node}")

    # Access the single-node variable
    print()
    print("Single-node mapping:")
    for i in range(10):
        node = mt_single([3])
        print(f"Component {i} of example_array_single is on node {node}")

    # Test array read with potential migration
    print()
    print("Testing mt_array_read with block-cyclic array:")
    for i in range(10):
        value = mt_array_read(example_array_cyclic, i)
        print(f"Value at index {i} is {value}")

    print()
    print("Testing mt_array_read with single-node array:")
    for i in range(10):
        value = mt_array_read(example_array_single, i)
        print(f"Value at index {i} is {value}")

    # mt_run(example_spawn, args, 0, 0, 16)


