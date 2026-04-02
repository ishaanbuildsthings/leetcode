from sortedcontainers import SortedList
class Solution:
    def maxDepthBST(self, order: List[int]) -> int:
        nodeToDepth = {}

        nodes = SortedList()
        nodes.add(order[0])
        nodeToDepth[order[0]] = 0
        for i in range(1, len(order)):
            node = order[i]

            predecessor = None
            successor = None

            idx = nodes.bisect_left(node)
            # largest < node
            if idx > 0:
                predecessor = nodes[idx - 1]

            # smallest > node
            if idx < len(nodes):
                successor = nodes[idx]
            
            nodes.add(node)
            
            if predecessor is None:
                oldDepth = nodeToDepth[successor]
                nodeToDepth[node] = oldDepth + 1
            elif successor is None:
                oldDepth = nodeToDepth[predecessor]
                nodeToDepth[node] = oldDepth + 1
            else:
                oldDepth1 = nodeToDepth[successor]
                oldDepth2 = nodeToDepth[predecessor]
                nodeToDepth[node] = 1 + max(oldDepth1, oldDepth2)
        
        return max(nodeToDepth.values()) + 1



