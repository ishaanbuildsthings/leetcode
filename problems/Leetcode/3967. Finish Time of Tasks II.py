class Solution:
    def finishTime(self, n: int, edges: List[List[int]], baseTime: List[int]) -> int:
        # 2 * latest + own - earliest

        children = [[] for _ in range(n)]
        for p, c in edges:
            children[p].append(c)

        # just our finish time going down
        down = [None] * n
        downLight = [None] * n # which child had the smallest finish time
        downHeavy = [None] * n # which child had the largst finish time
        downLight2 = [None] * n
        downHeavy2 = [None] * n
        earlyBelow = [inf] * n # earlyBelow[node] is the earliest finish times of node's children
        lateBelow = [-inf] * n

        def dfs1(node):
            if not children[node]:
                down[node] = baseTime[node]
                return down[node]
            options = [] # will hold (finishTime, child)
            for child in children[node]:
                options.append((dfs1(child), child))
            options.sort()
            mx = options[-1][0]
            mn = options[0][0]
            ownD = mx - mn + baseTime[node]
            down[node] = ownD + mx
            downLight[node] = options[0][1]
            downHeavy[node] = options[-1][1]

            if len(options) > 1:
                downLight2[node] = options[1][1]
                downHeavy2[node] = options[-2][1]
            
            earlyBelow[node] = mn
            lateBelow[node] = mx

            return down[node]
        
        dfs1(0)

        up = [None] * n # if we go up from this node, what is the finish time of that UPWARDS node (assuming it does not go back down)

        res = [None] * n
        res[0] = down[0]

        def dfs2(node):
            # at child, we want to consider the min and max finish times of all adjacent nodes
            
            for child in children[node]:
                # we can get the child's childrens min and max finish times via earlyBelow and lateBelow
                childEarlyDown = earlyBelow[child]
                childLateDown = lateBelow[child]

                # OR the child can go up, and then back down but not through child, we want the min and max finish times in those cases

                upDownLow = None
                if downLight[node] == child:
                    upDownLow = down[downLight2[node]] if downLight2[node] is not None else inf
                else:
                    upDownLow = down[downLight[node]]
                
                upDownHigh = None
                if downHeavy[node] == child:
                    upDownHigh = down[downHeavy2[node]] if downHeavy2[node] is not None else -inf
                else:
                    upDownHigh = down[downHeavy[node]]
                
                upUpFinishTime = up[node]

                # we need node's finish time (assuming it cannot go back down through child)
                nodesMin = min(upDownLow, up[node] if up[node] is not None else inf)
                nodesMax = max(upDownHigh, up[node] if up[node] is not None else -inf)
                nodesFinish = nodesMax - nodesMin + baseTime[node] + nodesMax
                
                if nodesMax == -inf:
                    up[child] = baseTime[node]
                else:
                    up[child] = nodesMax - nodesMin + baseTime[node] + nodesMax

                mnAdj = min(childEarlyDown, up[child])
                mxAdj = max(childLateDown, up[child])
                ownD = mxAdj - mnAdj + baseTime[child]
                finishTime = ownD + mxAdj
                res[child] = finishTime

                dfs2(child)

        dfs2(0)

        return min(res)

                

                


