# notes:
# say our nodes are strings instead of numbers, we can map the words to 0 to n-1 numbers. I think even easier is to put the words into an array then use the words directly and iterate over that array.

from collections import defaultdict

# template by: https://github.com/agrawalishaan/leetcode
# if nodes are not 0 to n-1, provide a list of every node
# nodes^3 time and space
class FloydWarshall:
    def __init__(self, edgeList, n, allNodesList=None):
        self.n = n
        self.allNodesList = allNodesList if allNodesList != None else range(n)
        self.edgeMap = self._buildEdgeMap(edgeList)

    def _buildEdgeMap(self, edgeList):
        edgeMap = defaultdict(lambda: defaultdict(lambda: float('inf')))
        # initialize nodes to themselves
        for node in self.allNodesList:
            edgeMap[node][node] = 0

        # fill initial edge weights from the provided edge list
        for node1, node2, weight in edgeList:
            edgeMap[node1][node2] = min(edgeMap[node1][node2], weight)
            # if directed graph, comment the following line:
            # edgeMap[node2][node1] = min(edgeMap[node2][node1], weight)

        # fill minimum between any two edges
        for k in self.allNodesList:
            for fromNode in self.allNodesList:
                for toNode in self.allNodesList:
                    if edgeMap[fromNode][k] + edgeMap[k][toNode] < edgeMap[fromNode][toNode]:
                        edgeMap[fromNode][toNode] = edgeMap[fromNode][k] + edgeMap[k][toNode]

        return edgeMap

    def getDist(self, node1, node2):
        return self.edgeMap[node1][node2]