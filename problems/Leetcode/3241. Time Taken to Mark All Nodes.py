class Solution:
    def timeTaken(self, edges: List[List[int]]) -> List[int]:
        
        n = len(edges) + 1
        adj = [[] for _ in range(n)] # adj[node] -> [(childNode, w), ...]
        for a, b in edges:
            if b % 2:
                adj[a].append((b, 1))
            else:
                adj[a].append((b, 2))
            if a % 2:
                adj[b].append((a, 1))
            else:
                adj[b].append((a, 2))
        
        children = [[] for _ in range(n)]

        def makeChildren(node, par):
            for adjN, w in adj[node]:
                if adjN == par:
                    continue
                children[node].append((adjN, w))
                makeChildren(adjN, node)
        makeChildren(0, -1)

        down1 = [None] * n # down1[node] is the max time a leaf takes going down through one of our children
        down2 = [None] * n # down2[node] is the second max time going through a different child
        heavy1 = [None] * n
        heavy2 = [None] * n

        def dfs1(node):
            if not children[node]:
                down1[node] = 0
                return
            options = []
            for child, w in children[node]:
                dfs1(child)
                nw = w + down1[child]
                options.append((nw, child))
            options.sort(reverse=True)
            down1[node] = options[0][0]
            heavy1[node] = options[0][1]

            if len(options) > 1:
                down2[node] = options[1][0]
                heavy2[node] = options[1][1]
        
        dfs1(0)

        # max cost where we must go up from this node, then out to any other node (either up again, or down through another)
        up = [None] * n
        up[0] = 0

        res = [None] * n

        def dfs2(node):
            res[node] = max(up[node], down1[node])

            for child, w in children[node]:
                newEdge = 2 if node % 2 == 0 else 1

                # the child could go down from itself
                badDown = down1[child]

                # the child could go up to `node`, then down elsewhere
                if heavy1[node] == child:
                    upDown = newEdge + (down2[node] if down2[node] is not None else 0)
                else:
                    upDown = newEdge + down1[node]
                
                # the child could go up to `node` then up again
                upUp = newEdge + up[node]

                up[child] = max(upUp, upDown)
                dfs2(child)

        dfs2(0)

        return res

