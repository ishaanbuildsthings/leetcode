class Solution:
    def maximumMatchingIndices(self, nums1: List[int], nums2: List[int]) -> int:
        # can do O(1) space with no deque
        q1 = deque(nums1)
        def diffs():
            return sum(q1[i] != nums2[i] for i in range(len(q1)))
        smallDiffs = inf
        for _ in range(len(q1)):
            smallDiffs = min(smallDiffs, diffs())
            q1.appendleft(q1.pop())
        return len(q1) - smallDiffs