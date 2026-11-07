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
    def lastMarkedNodes(self, edges: List[List[int]]) -> List[int]:
        
        n = len(edges) + 1
        mx1 = [None] * n # holds (maxDist, furthestNode)
        mx2 = [None] * n

        children = edgeListToTree(edges, 0)

        def dfs1(node):
            if not children[node]:
                mx1[node] = [0, node]
                return
            
            mxDist1 = -inf
            mxDist2 = -inf
            furthest1 = None
            furthest2 = None

            for child in children[node]:
                dfs1(child)

                childMaxDist, deepNode = mx1[child]
                childMaxDist += 1

                if childMaxDist > mxDist1:
                    mxDist2 = mxDist1
                    furthest2 = furthest1

                    mxDist1 = childMaxDist
                    furthest1 = deepNode

                elif childMaxDist <= mxDist2:
                    continue
                
                # new best 2nd
                else:
                    mxDist2 = childMaxDist
                    furthest2 = deepNode
            
            mx1[node] = [mxDist1, furthest1]
            mx2[node] = [mxDist2, furthest2]
        
        dfs1(0)

        up = [0] * n # max distance if we go up
        upNode = [i for i in range(n)]

        res = [None] * n

        def dfs2(node):
            if mx1[node][0] >= up[node]:
                res[node] = mx1[node][1]
            else:
                res[node] = upNode[node]
            
            for child in children[node]:
                # child can go down
                bestDist = mx1[child][0]
                bestNode = mx1[child][1]

                bestChildUp = up[node] + 1
                bestNodeChildUp = upNode[node]

                # child can go up via node
                if up[node] + 1 > bestDist:
                    bestDist = up[node] + 1
                    bestNode = upNode[node]
                    
                
                # child can go up then down via somewhere else
                # node's best went through child exactly when it ends at child's own furthest node
                if mx1[node][1] != mx1[child][1]:
                    upDown = 1 + mx1[node][0]
                    targetNode = mx1[node][1]
                    if upDown > bestChildUp:
                        bestChildUp = upDown
                        bestNodeChildUp = targetNode
                else:
                    upDown = 1 + mx2[node][0]
                    targetNode = mx2[node][1]
                    if upDown > bestChildUp:
                        bestChildUp = upDown
                        bestNodeChildUp = targetNode

                up[child] = bestChildUp
                upNode[child] = bestNodeChildUp
                dfs2(child)
        
        dfs2(0)

        return res