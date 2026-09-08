# https://leetcode.com/problems/k-divisible-elements-subarrays/description/
# difficulty: medium
# tags: rolling hash, prefix

# Problem
# Given an integer array nums and two integers k and p, return the number of distinct subarrays, which have at most k elements that are divisible by p.

# Two arrays nums1 and nums2 are said to be distinct if:

# They are of different lengths, or
# There exists at least one index i where nums1[i] != nums2[i].
# A subarray is defined as a non-empty contiguous sequence of elements in an array.

# Solution
# Check all subarrays and use prefix query + rolling hash. We can / should cap the hash with MOD and use naive checks. Can also use two hashes instead for higher accuracy.

class Solution:
    def countDistinct(self, nums: List[int], k: int, p: int) -> int:
        pf = [] # number of elements divisible by p
        count = 0
        for num in nums:
            count += (num / p) == math.floor(num / p)
            pf.append(count)
        print(pf)

        def queryDivis(l, r):
            if l == 0:
                return pf[r]
            return pf[r] - pf[l - 1]

        seen = set() # stores hashes

        res = 0
        for l in range(len(nums)):
            hash = 0
            for r in range(l, len(nums)):
                hash *= 200
                hash += nums[r]
                countDivis = queryDivis(l, r)
                res += countDivis <= k and not hash in seen
                seen.add(hash)
        return res
