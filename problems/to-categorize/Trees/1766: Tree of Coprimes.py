# https://leetcode.com/problems/tree-of-coprimes/description/
# difficulty: hard
# tags: tree, dfs, math

# Problem
# There is a tree (i.e., a connected, undirected graph that has no cycles) consisting of n nodes numbered from 0 to n - 1 and exactly n - 1 edges. Each node has a value associated with it, and the root of the tree is node 0.

# To represent this tree, you are given an integer array nums and a 2D array edges. Each nums[i] represents the ith node's value, and each edges[j] = [uj, vj] represents an edge between nodes uj and vj in the tree.

# Two values x and y are coprime if gcd(x, y) == 1 where gcd(x, y) is the greatest common divisor of x and y.

# An ancestor of a node i is any other node on the shortest path from node i to the root. A node is not considered an ancestor of itself.

# Return an array ans of size n, where ans[i] is the closest ancestor to node i such that nums[i] and nums[ans[i]] are coprime, or -1 if there is no such ancestor.

# Solution, O(50*50*log 50) overhead time, O(50n) time and space
# The number of node values is 50, so we use a 50n solution. First, precompute all coprimes which is a 50*50*log(50) overhead cost. Then, as we dfs, maintain a distance to the nearest above number for all values. We pass a copy of the 50 sized hashmap each time and update distances by 1. For a node, iterate through its coprimes, check them in the above seen parent hashmap, and update the result for that.

def gcd(a, b):
    while b != 0:
        a, b = b, a % b
    return a

coprimes = defaultdict(list) # maps a number to a list of its coprimes
for a in range(1, 51):
    for b in range(a, 51):
        if gcd(a, b) == 1:
            coprimes[a].append(b)
            coprimes[b].append(a)

class Solution:
    def getCoprimes(self, nums: List[int], edges: List[List[int]]) -> List[int]:
        edgeMap = defaultdict(list) # maps a node (not its value) to a list of adjacent nodes
        for fromNode, toNode in edges:
            edgeMap[fromNode].append(toNode)
            edgeMap[toNode].append(fromNode)

        res = [-1 for _ in range(len(nums))]

        # maps a nodeval to its closest distance and the relevant node ID, [distance, nodeId]
        rootSeenDistances = {}
        for i in range(1, 51):
            rootSeenDistances[i] = [float('inf'), None]

        seen = set() # helps tree traversal

        # We start at the top of the tree and dfs down. We track the furthest distance to each of the 50 possible numbers, so when our child receives it, it can determine the result
        def dfs(node, seenDistances):
            seen.add(node)

            nodeVal = nums[node]
            closestForThis = float('inf')
            ancestorNode = -1 # the node id
            for coprime in coprimes[nodeVal]:
                distance, nodeId = seenDistances[coprime]
                if distance < closestForThis:
                    closestForThis = distance
                    ancestorNode = nodeId
            if closestForThis == float('inf'):
                res[node] = -1
            else:
                res[node] = ancestorNode # since the list was not updated

            seenDistancesCopy = {}
            for i in range(1, 51):
                seenDistancesCopy[i] = [seenDistances[i][0] + 1, seenDistances[i][1]]
            seenDistancesCopy[nodeVal] = [0, node]

            children = edgeMap[node]
            for child in children:
                if child in seen:
                    continue
                dfs(child, seenDistancesCopy)


        dfs(0, rootSeenDistances)
        return res

