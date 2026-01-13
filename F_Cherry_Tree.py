# TEMPLATE BY ISHAAN AGRAWAL, github: ishaanbuildsthings
# takes nodes from 0 to n-1 and constructs a children map rooted at 0
from collections import defaultdict
def edgeListToTree(edgeList, n):
    edgeMap = [[] for _ in range(n)]
    for a, b in edgeList:
        edgeMap[a].append(b)
        edgeMap[b].append(a)

    children = [[] for _ in range(n)]
    parent = [-1] * n
    parent[0] = -2

    st = [0]
    order = []
    while st:
        v = st.pop()
        order.append(v)
        for nei in edgeMap[v]:
            if nei == parent[v]:
                continue
            parent[nei] = v
            children[v].append(nei)
            st.append(nei)

    return children

from types import GeneratorType

def bootstrap(f, stack=[]):
    def wrappedfunc(*args, **kwargs):
        if stack:
            return f(*args, **kwargs)
        else:
            to = f(*args, **kwargs)
            while True:
                if type(to) is GeneratorType:
                    stack.append(to)
                    to = next(to)
                else:
                    stack.pop()
                    if not stack:
                        break
                    to = stack[-1].send(to)
            return to
    return wrappedfunc
from functools import lru_cache
T = int(input())
for t in range(T):
    n = int(input())
    edges = []
    for _ in range(n - 1):
        a, b = map(int, input().split())
        a -= 1
        b -= 1
        edges.append((a, b))

    children = edgeListToTree(edges, n)

    cache = [None] * n

    @bootstrap
    def dfs(node):
        if cache[node]:
            yield cache[node]
            return

        # base case, a single leaf
        if not children[node]:
            yield [False, True, False] # remainder 1 is doable
            return
        
        dp = yield dfs(children[node][0]) # first child
        for childNumber in range(1, len(children[node])):
            child = children[node][childNumber]
            childDp = yield dfs(child)
            ndp = [False, False, False]
            # no remainder is doable with [0, 0] [1, 2] [2, 1]
            if (dp[0] and childDp[0]) or (dp[1] and childDp[2]) or (dp[2] and childDp[1]):
                ndp[0] = True
            
            # 1 remainder is doable with [0, 1] [1, 0] [2, 2]
            if (dp[0] and childDp[1]) or (dp[1] and childDp[0]) or (dp[2] and childDp[2]):
                ndp[1] = True

            # 2 remainder is doable with [0, 2] [2, 0] [1, 1]
            if (dp[0] and childDp[2]) or (dp[2] and childDp[0]) or (dp[1] and childDp[1]):
                ndp[2] = True
            
            dp = ndp
        
        # 1 remainder is just always doable, we shake this subtree
        dp[1] = True

        cache[node] = dp
        
        yield dp
    
    print('YES' if dfs(0)[0] else 'NO')


    
    