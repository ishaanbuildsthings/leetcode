# TEMPLATE BY ISHAANBUILDSTHINGS on github
import random
MASK = (1 << 64) - 1
FIXED = random.getrandbits(64)

def mix(x):
    x = (x + 0x9e3779b97f4a7c15 + FIXED) & MASK
    x = ((x ^ (x >> 30)) * 0xbf58476d1ce4e5b9) & MASK
    x = ((x ^ (x >> 27)) * 0x94d049bb133111eb) & MASK
    return x ^ (x >> 31)

# in:  children = [[], [2,3], [4,5], [], [], []]   # children[v], parent excluded; root matches indexing
# out: hashes   = [0, h1, h2, mix1, mix1, mix1]    # hashes[v] = 64-bit hash of v's subtree
# hashes[u] == hashes[v] iff those subtrees are isomorphic as rooted unordered trees. O(n log n) time, O(n) space
def subtreeHashes(children, root):
    hashes = [0] * len(children)
    order = []
    stk = [root]
    while stk:
        node = stk.pop()
        order.append(node)
        stk.extend(children[node])
    for node in reversed(order):
        h = 1
        for childHash in sorted(hashes[child] for child in children[node]):
            h = (h * 1000000007 + childHash) & MASK
        hashes[node] = mix(h)
    return hashes