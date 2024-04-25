# https://leetcode.com/problems/time-needed-to-inform-all-employees/description/
# difficulty: medium
# tags: dfs

# Solution, O(n) time O(n) space


class Solution:
    def numOfMinutes(self, n: int, headID: int, manager: List[int], informTime: List[int]) -> int:
        children = defaultdict(list)

        for i in range(len(manager)):
            if manager[i] == -1:
                root = i
            else:
                children[manager[i]].append(i)

        def dfs(node):
            # base case
            if not children[node]:
                return 0

            return informTime[node] + max(dfs(child) for child in children[node])

        return dfs(root)