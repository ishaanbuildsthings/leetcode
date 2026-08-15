class Solution:
    def minOperations(self, s: str) -> int:
        def dist(a, b):
            sz = abs(ord(a) - ord(b))
            return min(sz, 26 - sz)
        
        q = deque(list(s))
        res = inf
        n = len(s)
        for i in range(n):
            L = 0
            R = n - 1
            ops = i
            while L < R:
                ops += dist(q[L], q[R])
                L += 1
                R -= 1
            res = min(res, ops)
            q.append(q.popleft())
        
        return res

