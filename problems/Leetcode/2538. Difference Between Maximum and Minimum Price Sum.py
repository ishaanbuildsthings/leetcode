# SOLUTION 1, prefix + suffix
# TEMPLATE BY ISHAAN AGRAWAL, github: ishaanbuildsthings
# takes nodes from 0 to n-1 and constructs a children map rooted at 0
from collections import defaultdict
def edgeListToTree(edgeList):
    edgeMap = defaultdict(list)
    for a, b in edgeList:
        edgeMap[a].append(b)
        edgeMap[b].append(a)

    children = defaultdict(list) # maps a node to its children

    def buildTree(node, parent):
        for adj in edgeMap[node]:
            if adj == parent:
                continue
            children[node].append(adj)
            buildTree(adj, node)
    buildTree(0, -1) # root at 0
    return children

class Solution:
    def maxOutput(self, n: int, edges: List[List[int]], price: List[int]) -> int:
        children = edgeListToTree(edges)

        down = [0] * n # max price sum going down
        def dfs1(node):
            if not children[node]:
                down[node] = price[node]
                return
            resHere = price[node]
            for child in children[node]:
                dfs1(child)
                resHere = max(resHere, price[node] + down[child])
            down[node] = resHere
        
        dfs1(0)

        up = [0] * n # max price going up first
        up[0] = price[0]
        res = [0] * n # max price going any direction
        def dfs2(node):
            res[node] = max(down[node], up[node])
            bucket = children[node]
            pfDown = []
            for i in range(len(bucket)):
                child = bucket[i]
                left = 0 if i == 0 else pfDown[i - 1]
                current = price[node] + down[child]
                pfDown.append(max(left, current))
            suffDown = [0] * len(bucket)
            for i in range(len(bucket) - 1, -1, -1):
                child = bucket[i]
                right = 0 if i == len(bucket) - 1 else suffDown[i + 1]
                current = price[node] + down[child]
                suffDown[i] = max(right, current)
            
            
            for i in range(len(bucket)):
                bestUp = 0
                child = bucket[i]
                left = pfDown[i - 1] if i else 0
                right = suffDown[i + 1] if i < len(bucket) - 1 else 0
                upViaExcl = price[child] + max(left, right)
                bestUp = max(bestUp, upViaExcl)
                bestUp = max(bestUp, price[child] + up[node])
                up[child] = bestUp

                dfs2(child)
        
        dfs2(0)

        ans = 0
        for node in range(len(res)):
            diff = res[node] - price[node]
            ans = max(ans, diff)
        return ans


        

# SOLUTION 2, track best child node from parent
# TEMPLATE BY ISHAAN AGRAWAL, github: ishaanbuildsthings
# takes nodes from 0 to n-1 and constructs a children map rooted at 0
from collections import defaultdict
def edgeListToTree(edgeList):
    edgeMap = defaultdict(list)
    for a, b in edgeList:
        edgeMap[a].append(b)
        edgeMap[b].append(a)

    children = defaultdict(list) # maps a node to its children

    def buildTree(node, parent):
        for adj in edgeMap[node]:
            if adj == parent:
                continue
            children[node].append(adj)
            buildTree(adj, node)
    buildTree(0, -1) # root at 0
    return children

class Solution:
    def maxOutput(self, n: int, edges: List[List[int]], price: List[int]) -> int:
        children = edgeListToTree(edges)

        down = down = [[0, 0] for _ in range(n)] # max price sums going down
        best = [None] * n # which child was best
        def dfs1(node):
            bucket = down[node]
            if not children[node]:
                bucket[0] = price[node]
                return
            bucket[0] = price[node]
            for child in children[node]:
                dfs1(child)
                c1, _ = down[child]
                c1 += price[node]
                if c1 >= bucket[0]:
                    best[node] = child
                    bucket[1] = bucket[0]
                    bucket[0] = c1
                elif c1 >= bucket[1]:
                    bucket[1] = c1
        
        dfs1(0)

        up = [0] * n
        up[0] = price[0]
        full = [0] * n
        full[0] = down[0][0]

        def dfs2(node):
            aboveBest = best[node]
            for child in children[node]:
                parentBest = down[child][0]
                # go up to parent then back down to a sibling
                upThenDown = 0
                if aboveBest == child:
                    upThenDown = down[node][1] + price[child]
                else:
                    upThenDown = down[node][0] + price[child]
                
                upUp = up[node] + price[child]

                fullBest = max(upUp, upThenDown, down[child][0])

                full[child] = fullBest

                up[child] = max(upThenDown, upUp)

                dfs2(child)
        
        dfs2(0)

        res = 0
        for node in range(n):
            mx = full[node]
            mx -= price[node]
            res = max(res, mx)
        return res





