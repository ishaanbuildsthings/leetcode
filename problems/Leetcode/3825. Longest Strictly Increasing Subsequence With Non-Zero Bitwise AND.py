# Given an array, returns a lis length + a lis in N log N time

from bisect import bisect_left

def lisLengthSequence(nums):
    n = len(nums)
    if n == 0:
        return 0, []

    tails = []
    tailsIndex = []
    prevIndex = [-1] * n

    for i, val in enumerate(nums):
        pos = bisect_left(tails, val)
        if pos == len(tails):
            tails.append(val)
            tailsIndex.append(i)
        else:
            tails[pos] = val
            tailsIndex[pos] = i
        if pos > 0:
            prevIndex[i] = tailsIndex[pos - 1]

    length = len(tails)
    seq = []
    idx = tailsIndex[-1]
    while idx != -1:
        seq.append(nums[idx])
        idx = prevIndex[idx]
    seq.reverse()

    return length, seq

class Solution:
    def longestSubsequence(self, nums: List[int]) -> int:
        res = 0
        for bit in range(32):
            nums2 = [x for x in nums if x & (1 << bit)]
            res = max(res, lisLengthSequence(nums2)[0])
        return res