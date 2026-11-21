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
    def maxScore(self, parent: list[int], op: list[int], score: list[int]) -> int:

        n = len(parent)
        children = [[] for _ in range(n)]
        for i in range(n):
            par = parent[i]
            if par != -1:
                children[par].append(i)

        # print(children)

        # return max sum score of this subtree
        def dfs(node):
            if not children[node]:
                return score[node]
            childScores = [dfs(child) for child in children[node]]

            # print('-----')
            # print(f'answering for node: {node}')
            mn = min(childScores)
            tot = sum(childScores)
            operation = op[node]
            scoreHere = score[node]
            # print(f'my score: {scoreHere}')
            # print(f'mn below: {mn}')

            # must
            if operation == 1:
                # print(f'must do')
                ntot = tot - mn
                ret = ntot + scoreHere
                # print(f'returning: {ret}')
                return ret

            # print(f'optional on node: {node')
            # print(f'optional')
            if mn >= 0:
                ret = tot + scoreHere
                # print(f'mn was big, we do not zero anything, ret: {ret}')
                return ret
            ret = tot - mn + scoreHere
            # print(f'mn was small, we zero it out, ret: {ret}')
            return ret

        return dfs(0)
                
                
                