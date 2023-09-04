n = 3
LOG = 1
depths = { 0 : 0, 1 : 1, 2 : 2 }
parents = { 0 : 0, 1 : 0, 2 : 1 }

# General reqs:
# An arbitrarily rooted tree or a directed graph works.

# Time Complexity:
# Preprocess: O(NlogN)
# Query LCA: O(logN)
# _______________________________________________________________________________________________________________________
# TEMPLATE
# Variables:
# n is the number of nodes
# depths[node] tells us the depth
# parents[node] tells us the parent, if we are at a root in a tree or parent, IT MUST POINT TO ITSELF
# LOG floor(log2(n)). This is the biggest jump we need to make. If n is a power of 2, technically we can jump less. However, if n=1, LOG is 0. If we say we need to make no jumps, the may get messed up. It's also harder to code that LOG can be 1 less if n is a power of 2.

# initialize the lift with 1 jump above
# lift[node][jump_pow] tells us the 2^power-th ancestor of node, always ending at 0
lift = [[-1 for _ in range(LOG + 1)] for _ in range(n)]
for i in range(n):
    lift[i][0] = parents[i]
lift[0][0] = 0
# fill the lift
for jump_pow in range(1, LOG + 1):
    for node in range(n):
        old_parent = lift[node][jump_pow - 1]
        doubled = lift[old_parent][jump_pow - 1]
        lift[node][jump_pow] = doubled

# gets the kth ancestor of a node by jumping up by powers of 2, or 0 if more than k
def get_kth_ancestor(node, k):
    result = node
    for bit in range(LOG, -1, -1):
        if (k >> bit) & 1:
            result = lift[result][bit]
    return result

# gets the lowest common ancestor of two nodes
def get_lca(u, v):
    if depths[u] < depths[v]: # make u lower than v
        u, v = v, u
    depth_diff = depths[u] - depths[v]
    u = get_kth_ancestor(u, depth_diff) # bring nodes to same height

    if u == v: # edge case, same node means, as we return parent otherwise
        return u

    # from higher power of 2s, jump both nodes if their LCA doesn't match, at the end, the parent of each node will be the LCA
    for jump_pow in range(LOG, -1, -1):
        if lift[u][jump_pow] != lift[v][jump_pow]:
            u = lift[u][jump_pow]
            v = lift[v][jump_pow]

    return parents[u]

