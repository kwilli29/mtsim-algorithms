#!/usr/bin/env python3

# runtime_support: basic routines to manage state

from collections import defaultdict

# Initialize global variables
thread_matrix = {}
node_matrix = {}
migration_matrix = []
remote_matrix = []
runnable = []
suspended = []
current_tid = None
current_node = 0
num_nodes = 0
threads_active = 0
runtime = {}
thread_matrix = defaultdict(lambda: {
    'thread_id': None,
    'parent_tid': None,
    'node_born': None,
    'node_died': None,
    'migrations': 0,
    'children_spawned': 0,
    'active_children': 0,
    'data_reads': 0,
    'data_writes': 0,
    'atomic_ops': 0,
    'remote_atomics': 0,
    'remote_stores': 0,
    'multi_maps': 0
})
node_matrix = defaultdict(lambda: {
    'threads_spawned': [],
    'threads_died': [],
    'migrations_to': 0,
    'migrations_from': 0,
    'data_reads': None,
    'data_writes': None,
    'atomic_ops': None,
    'remote_atomics': None,
    'remote_stores': None,
    'multi_maps': None
})

def migration_matrix_constructor(nodes):
    global migration_matrix
    migration_matrix = [[0] * nodes for _ in range(nodes)] # initialize migration matrix

# This routine runs an mt-threaded program
# It executes mt-threads one at a time until there are no more
def mt_run(fcn, args, tid, node, nodes):
    # start an mt-thread with the specified tid on node node in a system with nodes nodes in it
    global thread_matrix, node_matrix, migration_matrix, remote_matrix
    global runnable # stack of runnable states
    global current_tid, current_fcn, current_node, num_nodes
    runnable = [] # clear the stack
    runnable.append((fcn, args, tid, node)) # add first_thread
    thread_matrix[tid]['thread_id'] = tid
    thread_matrix[tid]['parent_tid'] = None
    thread_matrix[tid]['node_born'] = node
    node_matrix[node]['threads_spawned'].append(tid)
    # initialize
    num_nodes = nodes
    current_tid = tid
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
        # print("Starting new thread ", current_tid, " on node ", current_node)
        # now run that thread
        result = next_fcn(current_args)
    # print out the stats
    print()
    for i in range(0, len(thread_matrix)):
        mt_stats_thread(i)
        print()
    print()
    for i in range(0, len(node_matrix)):
        mt_stats_node(i)
        print()

    return result

# terminate current thread called as last executable statement in an mt-thread code function
def mt_die():
    global current_tid, current_fcn, current_node, num_nodes
    # record which node the current thread died on
    # then print out message
    # node_matrix[current_tid].append(current_node)
    thread_matrix[current_tid]['node_died'] = current_node
    parent_tid = thread_matrix[current_tid]['parent_tid']
    if parent_tid is not None:
        thread_matrix[parent_tid]['active_children'] -= 1
    node_matrix[current_node]['threads_died'].append(current_tid)
    # print("Thread ", current_tid, " died on node ", current_node)


def get_new_tid():
    return len(thread_matrix)

def mt_spawn(thread_body, args):
    global current_node, current_tid
    new_tid = get_new_tid()
    runnable.append((thread_body, args, new_tid, current_node)) # stack the new thread
    thread_matrix[new_tid]['thread id'] = new_tid
    thread_matrix[new_tid]['parent_tid'] = current_tid 
    thread_matrix[new_tid]['node_born'] = current_node
    thread_matrix[current_tid]['children_spawned'] += 1
    thread_matrix[current_tid]['active_children'] += 1
    node_matrix[current_node]['threads_spawned'].append(new_tid)

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

def mt_array_read(x, i, graph=False):
    global current_tid, current_node, migration_matrix
    map_fcn, map_parameters = runtime[id(x)]
    if graph == True:
        vertex, length, nodes = map_parameters
        node = map_fcn(vertex, length, nodes)
    else:
        if len(map_parameters) == 3:
            node = map_fcn(map_parameters, i)
        else:
            node = map_fcn(map_parameters)
    if node != current_node:
        thread_matrix[current_tid]['migrations'] += 1
        node_matrix[current_node]['migrations_from'] += 1
        node_matrix[node]['migrations_to'] += 1 
        migration_matrix[current_node][node] = 1
        # current_node = node
        print(f"Migrating from node {current_node} to node {node}")
        print(f"Accessing x[{i}] at node {node}")
        current_node = node
    else:
        print(f"Accessing x[{i}] at node {current_node}")
    return x[i]

def mt_array_write(x, i, v):
    global current_node, migration_matrix
    map_fcn, map_parameters = runtime[id(x)]
    if len(map_parameters) == 3:
        node = map_fcn(map_parameters, i)
    else:
        node = map_fcn(map_parameters)
    if node != current_node:
        migration_matrix[current_node][node] = 1
        current_node = node
        print(f"Accessing x[{i}] at node {current_node}")
    else:
        print(f"Accessing x[{i}] at node {current_node}")
    x[i] = v

def mt_sync(next_fcn, args):
    global current_tid, current_node, num_nodes
    if thread_matrix[current_tid]['active_children'] == 0:
        runnable.append((next_fcn, args, current_tid, current_node, num_nodes))
    else:
        suspended.append((next_fcn, args, current_tid, current_node))
        while thread_matrix[current_tid]['active_children'] > 0:
            continue
        next_fcn, args, current_tid, current_node, num_nodes = suspended.pop()
        runnable.append((next_fcn, args, current_tid, current_node, num_nodes)) 

def mt_stats_thread(x):
    print(f"Thread ID: {x}")
    for key, value in thread_matrix[x].items():
        print(f"{key}: {value}")

def mt_stats_node(x):
    print(f"Node: {x}")
    for key, value in node_matrix[x].items():
        print(f"{key}: {value}")

def level_1_hash(key, length, nodes):
    '''Level 1 hash function to determine the node.'''
    
    i = 0
    result = 0
    
    while i != length:
        result += key[i]
        result += result << 10
        result ^= result >> 6
        i += 1
    
    result += result << 3
    result ^= result >> 11
    result += result << 15

    node = result % nodes
    return node
    



    



