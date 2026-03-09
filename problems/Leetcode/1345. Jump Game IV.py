class Solution:
    def minJumps(self, arr: List[int]) -> int:
        seen = set() # indices
        q = deque()
        q.append(0)
        seen.add(0)
        steps = 0
        numToIdxs = defaultdict(list)
        for i, v in enumerate(arr):
            numToIdxs[v].append(i)
        while q:
            length = len(q)
            for _ in range(length):
                idx = q.popleft()
                if idx == len(arr) - 1:
                    return steps
                # idx-1
                if idx and idx-1 not in seen:
                    seen.add(idx-1)
                    q.append(idx-1)
                # idx+1
                if idx != len(arr) - 1 and idx+1 not in seen:
                    seen.add(idx+1)
                    q.append(idx+1)
                # same number
                for idx2 in numToIdxs[arr[idx]]:
                    if idx2 not in seen:
                        seen.add(idx2)
                        q.append(idx2)
                numToIdxs[arr[idx]] = []
            steps += 1
                