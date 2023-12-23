# https://leetcode.com/problems/node-with-highest-edge-score/description/
# Difficulty: Medium
# Tags: graph, directed, disconnected

# Problem
# You are given a directed graph with n nodes labeled from 0 to n - 1, where each node has exactly one outgoing edge.

# The graph is represented by a given 0-indexed integer array edges of length n, where edges[i] indicates that there is a directed edge from node i to node edges[i].

# The edge score of a node i is defined as the sum of the labels of all the nodes that have an edge pointing to i.

# Return the node with the highest edge score. If multiple nodes have the same edge score, return the node with the smallest index.

# Solution, O(n) time and space
# For each node, count how much score it gets. We could also find the max during this but when I wrote the code I did it in a second loop.

class Solution:
    def edgeScore(self, edges: List[int]) -> int:
        scores = defaultdict(int) # maps a node to the amount of score it gets
        for node in range(len(edges)):
            receiver = edges[node]
            amount = node
            scores[receiver] += amount

        maxEdgeScore = -1
        maxNode = None
        for node in scores.keys():
            score = scores[node]
            if score > maxEdgeScore or (score == maxEdgeScore and node < maxNode):
                maxNode = node
                maxEdgeScore = score
        return maxNode