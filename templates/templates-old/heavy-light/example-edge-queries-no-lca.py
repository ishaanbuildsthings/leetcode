# We have a tree of weighted edges, rooted at 1
# Support queries of the form (1, node) which tell us the sum of the path from 1 to node
# Support queries of the form (2, node1, node2, newWeight) which updates the weight of the edge between node1 and node2
# https://leetcode.com/contest/biweekly-contest-154/problems/shortest-path-in-a-weighted-tree/

from collections import defaultdict
class Solution:
    def treeQueries(self, n: int, edges: list[list[int]], queries: list[list[int]]) -> list[int]:

        adjMap = defaultdict(list)
        for node1, node2, weight in edges:
            adjMap[node1].append((node2, weight))
            adjMap[node2].append((node1, weight))

        # Map a node to its parent node
        parents = [None] * (n + 1)
        # Map a node to its depth
        depths = [0] * (n + 1)
        # Map a node to its subtree size
        sizes = [0] * (n + 1)
        # Map a node to its heaviest child
        heaviestChild = [None] * (n + 1)
        # Map a node to the weight of the edge going up from it
        edgeWeightsGoingUp = [None] * (n + 1)

        # This fills out all the above arrays
        def dfs(node, parent, currDepth):
            depths[node] = currDepth
            parents[node] = parent
            sizeHere = 1
            maxChildSubtreeSize = -1
            heaviestChildHere = None

            for adjacentNode, edgeWeight in adjMap[node]:
                if adjacentNode == parent:
                    continue
                dfs(adjacentNode, node, currDepth + 1)
                childSubtreeSize = sizes[adjacentNode]
                sizeHere += childSubtreeSize
                if childSubtreeSize > maxChildSubtreeSize:
                    maxChildSubtreeSize = childSubtreeSize
                    heaviestChildHere = adjacentNode
                edgeWeightsGoingUp[adjacentNode] = edgeWeight

            heaviestChild[node] = heaviestChildHere
            sizes[node] = sizeHere

        # Now we need to label all the nodes in an order such that any heavy chain forms a contiguous subarray in our labeled order
        # We also want to map nodes to the top of their heavy chains (or themselves if the edge going up from a node is a light edge, this simplifies the implemtnation)

        labels = [None] * (n + 1)
        nodeToTopOfHeavyChain = [None] * (n + 1)
        currentPosition = 0
        def decompose(node, parent, topOfHeavyChain):
            nonlocal currentPosition
            labels[node] = currentPosition
            currentPosition += 1
            nodeToTopOfHeavyChain[node] = topOfHeavyChain

            # leaf node
            if heaviestChild[node] is None:
                return

            # always dfs to heavy child first
            decompose(heaviestChild[node], node, topOfHeavyChain)

            for adj, _ in adjMap[node]:
                if adj == parent:
                    continue
                if adj == heaviestChild[node]:
                    continue
                # here we are visiting a light child, so reset the topOfHeavyChain
                decompose(adj, node, adj)

        decompose(1, None, 1)














