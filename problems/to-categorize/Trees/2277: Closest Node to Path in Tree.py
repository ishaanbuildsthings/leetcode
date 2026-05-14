# https://leetcode.com/problems/closest-node-to-path-in-tree/
# Difficulty: hard
# Tags: binary lift, lca

# Problem
# You are given a positive integer n representing the number of nodes in a tree, numbered from 0 to n - 1 (inclusive). You are also given a 2D integer array edges of length n - 1, where edges[i] = [node1i, node2i] denotes that there is a bidirectional edge connecting node1i and node2i in the tree.

# You are given a 0-indexed integer array query of length m where query[i] = [starti, endi, nodei] means that for the ith query, you are tasked with finding the node on the path from starti to endi that is closest to nodei.

# Return an integer array answer of length m, where answer[i] is the answer to the ith query.

# Solution
# For each query, I get all nodes in the path by using LCA and parent pointers. This takes path time, which is O(n) for a linked list or O(log n) for a balanced tree. Then for each node on that path, I compute the distance in logn time with the binary lift.
# O(n log n) preprocess + O(queries * path time * logN), O(n log n) space

class Solution:
    def closestNode(self, n: int, edges: List[List[int]], query: List[List[int]]) -> List[int]:
        edgeMap = defaultdict(list)
        for a, b in edges:
            edgeMap[a].append(b)
            edgeMap[b].append(a)

        children = defaultdict(list) # maps a node to its children
        seen = set()

        def buildTree(node):
            seen.add(node)

            for adj in edgeMap[node]:
                # skip nodes we have already seen to prevent back and forth
                if adj in seen:
                    continue
                children[node].append(adj)
                buildTree(adj)
        buildTree(0) # arbitrary root at 0

        parents = {} # maps a node to its parent
        parents[0] = 0
        depths = {}
        def dfs(node, depth):
            depths[node] = depth
            for child in children[node]:
                parents[child] = node
                dfs(child, depth + 1)
        dfs(0, 0)

        LOG = math.floor(math.log2(n))

        # construct the lift table which will help us compute the LCA
        # lift[node][jumpPow] tells us the 2^power-th ancestor of node, always ending at 0
        lift = [[-1 for _ in range(LOG + 1)] for _ in range(n)]
        for i in range(n):
            lift[i][0] = parents[i]
        lift[0][0] = 0
        # fill the lift
        for jumpPow in range(1, LOG + 1):
            for node in range(n):
                old_parent = lift[node][jumpPow - 1]
                doubled = lift[old_parent][jumpPow - 1]
                lift[node][jumpPow] = doubled

        # gets the kth ancestor of a node by jumping up by powers of 2, or 0 if more than k
        def getKthAncestor(node, k):
            result = node
            for bit in range(LOG, -1, -1):
                if (k >> bit) & 1:
                    result = lift[result][bit]
            return result

        # gets the lowest common ancestor of two nodes
        def getLca(u, v):
            if depths[u] < depths[v]: # make u lower than v
                u, v = v, u
            depthDiff = depths[u] - depths[v]
            u = getKthAncestor(u, depthDiff) # bring nodes to same height

            if u == v: # edge case, same node means, as we return parent otherwise
                return u

            # from higher power of 2s, jump both nodes if their LCA doesn't match, at the end, the parent of each node will be the LCA
            for jumpPow in range(LOG, -1, -1):
                if lift[u][jumpPow] != lift[v][jumpPow]:
                    u = lift[u][jumpPow]
                    v = lift[v][jumpPow]

            return parents[u]

        def allOnPath(start, end):
            lca = getLca(start, end)
            path = []
            # edge cases
            if lca == start:
                p = end
                while p != lca:
                    path.append(p)
                    p = parents[p]
                path.append(lca)
            elif lca == end:
                p = start
                while p != lca:
                    path.append(p)
                    p = parents[p]
                path.append(lca)
            else:
                p1 = start
                while p1 != lca:
                    path.append(p1)
                    p1 = parents[p1]
                p2 = end
                while p2 != lca:
                    path.append(p2)
                    p2 = parents[p2]
                path.append(lca)
            return path

        def getDistance(node1, node2):
            lca = getLca(node1, node2)
            lcaHeight = depths[lca]
            node1Height = depths[node1]
            node2Height = depths[node2]
            dist1 = node1Height - lcaHeight
            dist2 = node2Height - lcaHeight
            return dist1 + dist2


        res = []
        for start, end, goalNode in query:
            lca = getLca(start, end)
            path = allOnPath(start, end)
            smallestDistance = float('inf')
            resNode = None
            for nodeInPath in path:
                distance = getDistance(nodeInPath, goalNode)
                if distance < smallestDistance:
                    smallestDistance = distance
                    resNode = nodeInPath
            res.append(resNode)

        return res


