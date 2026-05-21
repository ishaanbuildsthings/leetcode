from sortedcontainers import SortedList
class Solution:
    def popcountDepth(self, nums: List[int], queries: List[List[int]]) -> List[int]:
        @cache
        def getDepth(number):
            return (1 + getDepth(number.bit_count())) if number != 1 else 0

        depthToIdxs = defaultdict(lambda: SortedList())
        res = []

        for i, v in enumerate(nums):
            depth = getDepth(v)
            depthToIdxs[depth].add(i)

        for q in queries:
            if len(q) == 3:
                _, index, updateVal = q
                depthToIdxs[getDepth(nums[index])].remove(index)
                nums[index] = updateVal
                depthToIdxs[getDepth(nums[index])].add(index)
            else:
                _, l, r, reqDepth = q
                sl = depthToIdxs[reqDepth]
                res.append(sl.bisect_right(r) - sl.bisect_left(l))
        return res
                
                
        