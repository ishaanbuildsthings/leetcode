class Solution:
    def maxRequests(self, requests: list[list[int]], k: int, window: int) -> int:
        userToTimes = defaultdict(list)
        for user, time in requests:
            userToTimes[user].append(time)
        def drop(u):
            times = userToTimes[u]
            times.sort()
            q = deque()
            kept = 0
            for t in times:
                if not q:
                    kept += 1
                    q.append(t)
                    continue
                while q and (t - q[0]) > window:
                    q.popleft()
                if len(q) < k:
                    q.append(t)
                    kept += 1
            return kept
        
        s = set()
        for user, time in requests:
            s.add(user)
        
        return sum(drop(t) for t in s)