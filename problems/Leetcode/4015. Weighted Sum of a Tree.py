class Solution:
    def weightedSum(self, parent: list[int], nums: list[int]) -> int:

        children = defaultdict(list)
        for i in range(len(parent)):
            par = parent[i]
            if par == -1:
                continue
            children[par].append(i)

        def findHeight(node):
            if not children[node]:
                return 1
            res = 1
            for child in children[node]:
                res = max(res, 1 + findHeight(child))
            return res

        height = findHeight(0)

        ans = 0

        def dfs(node, currDepth):
            nonlocal ans
            weight = nums[node] * (height - currDepth + 1)
            ans += weight
            for child in children[node]:
                dfs(child, currDepth + 1)
        dfs(0, 1)

        return ans