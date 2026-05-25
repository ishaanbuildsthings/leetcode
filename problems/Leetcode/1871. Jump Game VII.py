# SOLUTION 1 silly-maxxing with segment tree graph representation
# class Solution:
#     def canReach(self, s: str, minJump: int, maxJump: int) -> bool:
#         n = len(s)
#         NODES = n + (4 * n) # N range-jump nodes + 4N seg tree nodes

#         g = [[] for _ in range(NODES + 1)]

#         leafIds = [None] * n # maps index -> node id
        
#         def build(nodeI, tl, tr):
#             if tl == tr:
#                 leafIds[tl] = nodeI
#                 return
#             left = 2 * nodeI
#             right = 2 * nodeI + 1
#             tm = (tl + tr) // 2
#             if tl != tm:
#                 g[nodeI].append(left)
#             else:
#                 if s[tl] == '0':
#                     g[nodeI].append(left)

#             if tr != tm + 1:
#                 g[nodeI].append(right)
#             else:
#                 if s[tr] == '0':
#                     g[nodeI].append(right)
            
#             build(2 * nodeI, tl, tm)
#             build(2 * nodeI + 1, tm + 1, tr)
            
#         build(1, 0, n - 1)

#         # NODES 1-4N are seg tree nodes
#         # NODES 4N+1 - 5N are query range nodes

#         def decompose(l, r):
#             output = []
#             def query(nodeI, tl, tr, ql, qr):
#                 # edge case dont allow any flow into a 1
#                 if tl == tr:
#                     if s[tl] == '1':
#                         return
#                 # fully inside
#                 if ql <= tl and qr >= tr:
#                     output.append(nodeI)
#                     return
#                 # disjoint
#                 if qr < tl or ql > tr:
#                     return
#                 tm = (tl + tr) // 2
#                 query(2 * nodeI, tl, tm, ql, qr)
#                 query(2 * nodeI + 1, tm + 1, tr, ql, qr)
#             query(1, 0, n - 1, l, r)
#             return output

#         for i in range(n):
#             # pruning
#             if s[i] == '1':
#                 continue
#             L = i + minJump
#             R = i + maxJump
#             if L >= n:
#                 continue
#             leafId = leafIds[i]
#             jumpId = 4 * n + i + 1
#             decomposition = decompose(L, R)
#             g[leafId].append(jumpId)
#             for nodeId in decomposition:
#                 g[jumpId].append(nodeId)
        
#         seenIds = [False] * (NODES + 1)
#         def dfs(idx):
#             seenIds[idx] = True
#             for adjN in g[idx]:
#                 if not seenIds[adjN]:
#                     dfs(adjN)
#         dfs(leafIds[0])

#         return seenIds[leafIds[-1]]

                



# solution 2, sliding window DP
# class Solution:
#     def canReach(self, s: str, minJump: int, maxJump: int) -> bool:
#         n = len(s)
#         dp = [False] * n
#         if s[-1] == '0':
#             dp[-1] = True
        
#         count = 0

#         for i in range(n - 2, -1, -1):
#             # enters the window
#             if i + minJump < n and dp[i + minJump]:
#                 count += 1
            
#             # exits
#             if i + maxJump + 1 < n and dp[i + maxJump + 1]:
#                 count -= 1
            
#             if s[i] == '0':
#                 dp[i] = count > 0
        
#         return dp[0]



# solution 3, amortized BFS
class Solution:
    def canReach(self, s: str, minJump: int, maxJump: int) -> bool:
        n = len(s)
        q = deque()
        q.append(0)
        right = 0
        while q:
            popped = q.popleft()
            if popped == n - 1:
                return True
            L = popped + minJump
            R = popped + maxJump
            nright = right
            for j in range(max(L, right + 1), min(R + 1, n)):
                nright = max(nright, j)
                if s[j] == '0':
                    q.append(j)
            right = nright
        return False
            




        