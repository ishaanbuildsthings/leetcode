class Solution:
    def sortArray(self, nums: List[int], pre: List[int]) -> int:
        s = tuple(sorted(nums))
        q = deque()
        q.append(tuple(nums))
        seen = {tuple(nums)}
        steps = 0
        while q:
            length = len(q)
            for _ in range(length):
                popped = q.popleft()
                if popped == s:
                    return steps
                for op in pre:
                    narr = popped[:op][::-1] + popped[op:]
                    if narr in seen:
                        continue
                    seen.add(narr)
                    q.append(narr)
            steps += 1
        return -1
