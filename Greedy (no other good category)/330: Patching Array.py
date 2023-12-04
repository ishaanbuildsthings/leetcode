# https://leetcode.com/problems/patching-array/description/
# difficulty: hard
# tags: greedy

# Problem
# Given a sorted integer array nums and an integer n, add/patch elements to the array such that any number in the range [1, n] inclusive can be formed by the sum of some elements in the array.

# Return the minimum number of patches required.

# Solution, O(n + log m) time, O(1) space
# We keep a variable which indicates we can make everything from 0:acc. When we iterate, say we have [1,1,1] and we are trying to make a 4, we cannot (say acc=3 here), we choose to add a 4 coin, because we can also make 5, 6, and 7, since we just add a 4 to the construction of 1, 2, or 3.

class Solution:
    def minPatches(self, nums: List[int], n: int) -> int:
        acc = 0 # implies we can make all the numbers from 0 to acc
        res = 0

        for num in nums:
            if acc >= n:
                return res

            # edge case, prevents them from putting huge coins that we try to fill up to but we don't even need
            if num > n:
                break


            # say our acc is 5 and the incoming num is 6, then we can make 6, and everything up to 11
            # technically not needed
            if num == acc + 1:
                acc += num
                continue

            # say our acc is 5 and the incoming num is 8, we cannot produce 6 or 7, so we first add a num of 6, now we can produce up to 11
            # but if our acc is 5 and the new num is 1000000, we basically need to add a 6, then a 12, and so on
            if num > acc + 1:
                while num > acc + 1:
                    res += 1
                    acc += (acc + 1) # the new num we create
                acc += num
                continue

            # if our acc is 5 and the incoming num is <= 5, we can just add it
            acc += num

        # even after all nums are added, we still might not even reach the total, so keep adding
        while acc < n:
            res += 1
            acc += (acc + 1)

        return res





