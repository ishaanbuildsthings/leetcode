# notes:
# say our nodes are strings instead of numbers, we can map the words to 0 to n-1 numbers. I think even easier is to put the words into an array then use the words directly and iterate over that array.

# template by: https://github.com/agrawalishaan/leetcode
# if nodes are not 0 to n-1, provide a list of every node
# nodes^3 time and space
class FloydWarshall:
    def __init__(self, edgeList, n, allNodesList=None):
        self.n = n
        self.allNodesList = allNodesList if allNodesList != None else range(n)
        self.edgeMap = self._buildEdgeMap(edgeList)

    def _buildEdgeMap(self, edgeList):
        edgeMap = [[inf] * (self.n+1) for _ in range(self.n+1)]
        # initialize nodes to themselves
        for node in self.allNodesList:
            edgeMap[node][node] = 0

        # fill initial edge weights from the provided edge list
        for node1, node2 in edgeList:
            edgeMap[node1][node2] = 1
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

class Solution:
    def countOfPairs(self, n: int, x: int, y: int) -> List[int]:
        edges = []
        for i in range(1, n):
            edges.append((i, i + 1))
            edges.append((i + 1, i))
        edges.append((x, y))
        edges.append((y, x))
        floyd = FloydWarshall(edges, n, list(range(1,n+1)))

        res = []
        for k in range(1, n + 1):
            resHere = 0
            for node1 in range(1, n + 1):
                for node2 in range(node1 + 1, n + 1):
                    if node1 == node2:
                        continue
                    dist = floyd.getDist(node1, node2)
                    resHere += dist == k
            res.append(resHere * 2)
        return res


