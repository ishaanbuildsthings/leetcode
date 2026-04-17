class Solution:
    def minMirrorPairDistance(self, nums: List[int]) -> int:
        nums = nums[::-1]
        late = {}
        res = inf
        for i, v in enumerate(nums):
            mirrored = str(v)[::-1].lstrip('0')
            if mirrored in late:
                distance = i - late[mirrored]
                res = min(res, distance)
            late[str(v)] = i
        return res if res != inf else -1
        