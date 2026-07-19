class Solution:
    def watchedVideosByFriends(self, watchedVideos: List[List[str]], friends: List[List[int]], id: int, level: int) -> List[str]:
        adj = defaultdict(list)
        for i in range(len(friends)):
            for fr in friends[i]:
                adj[i].append(fr)

        steps = 0
        q = deque()
        q.append(id)
        seen = {id}
        while q:
            if steps == level:
                break
            length = len(q)
            for _ in range(length):
                poppedId = q.popleft()
                for adjF in adj[poppedId]:
                    if adjF in seen:
                        continue
                    q.append(adjF)
                    seen.add(adjF)
            steps += 1
        
        c = Counter()
        for kAway in q:
            for vid in watchedVideos[kAway]:
                c[vid] += 1
        
        res = sorted(
                list(
                    c.keys()
                ),
                key=lambda x : (c[x], x)
            )
        return res

