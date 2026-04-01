# Solution 1, two sorted lists, O(n log n)
# from sortedcontainers import SortedList
# class Solution:
#     def minReverseOperations(self, n: int, p: int, banned: List[int], k: int) -> List[int]:

#         slEven = SortedList([i for i in range(n) if not i % 2])
#         slOdd = SortedList([i for i in range(n) if i % 2])
#         if p % 2:
#             slOdd.remove(p)
#         else:
#             slEven.remove(p)
#         q = deque()
#         q.append(p)
#         bset = set(banned)
#         minDist = [inf] * n
#         steps = 0
#         while q:
#             length = len(q)
#             for _ in range(length):
#                 poppedI = q.popleft()
#                 if poppedI in bset:
#                     continue
#                 minDist[poppedI] = steps
            
#                 # swap to the right
#                 ri = poppedI + k - 1
#                 li = poppedI - k + 1
#                 # but note for something like [0, 1, 0, 0] k=4 where we are at 1, we cannot access all positions
#                 if poppedI <= k - 1:
#                     dist = (k - 1) - poppedI
#                     li = max(li, li + 2 * dist)
                
#                 if poppedI >= n - k:
#                     dist = ri - (n - 1)
#                     ri = min(ri, ri - 2 * dist)

#                 if k % 2 == 0:
#                     nparity = (1 + poppedI) % 2
#                     sl = slOdd if nparity else slEven
#                 else:
#                     nparity = poppedI % 2
#                     sl = slOdd if nparity else slEven

#                 idxs = list(sl.irange(li, ri))
#                 for idx in idxs:
#                     q.append(idx)
#                     sl.remove(idx)
#             steps += 1
        
#         minDist = [x if x != inf else -1 for x in minDist]
#         return minDist
                    

                

# Solution 2, DSU with nxt[i]

class Solution:
    def minReverseOperations(self, n: int, p: int, banned: List[int], k: int) -> List[int]:
        nxt = [i for i in range(n + 2)]

        def find(idx):
            if nxt[idx] == idx:
                return idx
            nxt[idx] = find(nxt[idx])
            return nxt[idx]

        q = deque()
        q.append(p)
        bset = set(banned)
        seen = {p}
        steps = 0
        dist = [inf] * n
        while q:
            length = len(q)
            for _ in range(length):
                poppedI = q.popleft()
                if poppedI in bset:
                    continue
                dist[poppedI] = steps
                
                li = poppedI - k + 1
                leftSurplus = -li
                li = max(li, li + 2 * leftSurplus)

                ri = poppedI + k - 1
                rightSurplus = ri - (n - 1)
                ri = min(ri, ri - 2 * rightSurplus)

                j = find(li)
                while j <= ri:
                    if j not in seen:
                        q.append(j)
                        seen.add(j)
                    nxt[j] = j + 2
                    j = find(j + 2)
                
            steps += 1
        
        return [x if x != inf else -1 for x in dist]
        