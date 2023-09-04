# https://leetcode.com/problems/kth-ancestor-of-a-tree-node/
# Difficulty: Hard
# Tags: binary lift

# Problem
# You are given a tree with n nodes numbered from 0 to n - 1 in the form of a parent array parent where parent[i] is the parent of ith node. The root of the tree is node 0. Find the kth ancestor of a given node.

# The kth ancestor of a tree node is the kth node in the path from that node to the root node.

# Implement the TreeAncestor class:

# TreeAncestor(int n, int[] parent) Initializes the object with the number of nodes in the tree and the parent array.
# int getKthAncestor(int node, int k) return the kth ancestor of the given node node. If there is no such ancestor, return -1.

# Solution, O(n log n) time and space for initialization, O(log n) for query
# We create the binary lift array, which takes n log n time and space. Then for each query, we binary jump up in log time.

class TreeAncestor:

    def __init__(self, n: int, parents: List[int]):
        self.LOG = math.floor(math.log2(n))
        # initialize the lift with 1 jump above
        # lift[node][jump_pow] tells us the 2^power-th ancestor of node, always ending at 0
        self.lift = [[-1 for _ in range(self.LOG + 1)] for _ in range(n)]
        for i in range(n):
            self.lift[i][0] = parents[i]
        self.lift[0][0] = -1 # parent of root is -1 as per question spec
        # fill the lift
        for jump_pow in range(1, self.LOG + 1):
            for node in range(n):
                old_parent = self.lift[node][jump_pow - 1]
                if old_parent == -1:
                    doubled = -1
                else:
                    doubled = self.lift[old_parent][jump_pow - 1]
                self.lift[node][jump_pow] = doubled

    def getKthAncestor(self, node: int, k: int) -> int:
        result = node
        for bit in range(self.LOG, -1, -1):
            if (k >> bit) & 1:
                # move up a node
                result = self.lift[result][bit]
                # if we reach -1, return
                if result == -1:
                    return result
        return result


# Your TreeAncestor object will be instantiated and called as such:
# obj = TreeAncestor(n, parent)
# param_1 = obj.getKthAncestor(node,k)