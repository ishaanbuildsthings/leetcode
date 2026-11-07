# TEMPLATE BY ISHAAN AGRAWAL, github: ishaanbuildsthings
# edgeList = [[a, b], [c, d], ...]
# roots the tree at `root` (any node id) and returns `children`, sized to fit the largest label
# 0-indexed input -> children goes up to children[n-1]; 1-indexed -> up to children[n], children[0] empty and unused
def edgeListToTree(edgeList, root):
    size = max(max(a, b) for a, b in edgeList) + 1
    edgeMap = [[] for _ in range(size)]
    for a, b in edgeList:
        edgeMap[a].append(b)
        edgeMap[b].append(a)
    children = [[] for _ in range(size)]
    parent = [-1] * size
    stack = [root]
    while stack:
        node = stack.pop()
        for adj in edgeMap[node]:
            if adj == parent[node]:
                continue
            parent[adj] = node
            children[node].append(adj)
            stack.append(adj)
    return children

class Solution:
    def collectTheCoins(self, coins: List[int], edges: List[List[int]]) -> int:
        if not edges:
            return 0
        children = edgeListToTree(edges, 0)
        n = len(coins)

        # farthest coin inside node's subtree, measured from node (top two, by child)
        far1 = [-inf] * n
        child1 = [None] * n
        far2 = [-inf] * n

        def dfs1(node):
            if coins[node]:
                far1[node] = 0
            for child in children[node]:
                dfs1(child)
                candidate = far1[child] + 1
                # new farthest
                if candidate > far1[node]:
                    far2[node] = far1[node]
                    far1[node] = candidate
                    child1[node] = child
                # improves second farthest
                elif candidate > far2[node]:
                    far2[node] = candidate

        dfs1(0)

        # farthest coin outside node's subtree, measured from node
        up = [-inf] * n
        res = 0

        def dfs2(node):
            nonlocal res
            for child in children[node]:
                # farthest coin on the parent's side of this edge, measured from the parent
                if child1[node] != child:
                    parentSide = max(up[node], far1[node])
                else:
                    parentSide = max(up[node], far2[node])

                # farthest coin on each side, measured from the node across the edge
                childSideFromParent = far1[child] + 1
                parentSideFromChild = parentSide + 1

                # skip if either side can be collected without crossing
                canSkip = childSideFromParent <= 2 or parentSideFromChild <= 2
                if not canSkip:
                    res += 1

                up[child] = 1 + parentSide
                dfs2(child)

        dfs2(0)

        return 2 * res