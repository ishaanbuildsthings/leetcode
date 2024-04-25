# https://leetcode.com/problems/open-the-lock/description/
# difficulty: medium
# tags: bfs, graph

# Solution, O(lock combinations * log(one combination)) time and space

class Solution:
    def openLock(self, deadends: List[str], target: str) -> int:
        q = collections.deque()
        q.append('0000')
        seen = {'0000'}
        deadendsSet = set(deadends)
        LOCK_SIZE = 4
        steps = 0

        # edge case
        if '0000' in deadendsSet:
            return -1

        while q:
            qSize = len(q)
            for _ in range(qSize):
                popped = q.popleft()
                if popped == target:
                    return steps

                for i in range(LOCK_SIZE):
                    strNum = popped[i]
                    num = int(strNum)
                    if 1 <= num <= 8:
                        adj1, adj2 = num - 1, num + 1
                    elif num == 0:
                        adj1, adj2 = 9, 1
                    else:
                        adj1, adj2 = 8, 0
                    adjLockDown = popped[:i] + str(adj1) + popped[i + 1:]
                    adjLockUp = popped[:i] + str(adj2) + popped[i + 1:]
                    if not adjLockDown in seen and not adjLockDown in deadendsSet:
                        q.append(adjLockDown)
                        seen.add(adjLockDown)
                    if not adjLockUp in seen and not adjLockUp in deadendsSet:
                        q.append(adjLockUp)
                        seen.add(adjLockUp)
            steps += 1

        return -1

