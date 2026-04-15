class Solution:
    def maxHammingDistances(self, nums: List[int], m: int) -> List[int]:
        fmask = (1 << m) - 1
        def comp(v):
            return v ^ fmask
        
        q = deque(nums)
        
        minDist = [inf] * (2**m)
        seen = set(x for x in nums)
        steps = 0
        while q:
            length = len(q)
            for _ in range(length):
                node = q.popleft()
                minDist[node] = steps
                for b in range(m):
                    adjN = node ^ (1 << b)
                    if adjN in seen:
                        continue
                    seen.add(adjN)
                    q.append(adjN)
            steps += 1
        
        res = []
        for v in nums:
            opposite = comp(v)
            res.append(m - minDist[opposite])
        
        return res

