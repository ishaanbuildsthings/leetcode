# https://leetcode.com/problems/boats-to-save-people/description/
# difficulty: medium
# tags: two pointers

# Problem
# You are given an array people where people[i] is the weight of the ith person, and an infinite number of boats where each boat can carry a maximum weight of limit. Each boat carries at most two people at the same time, provided the sum of the weight of those people is at most limit.

# Return the minimum number of boats to carry every given person.

# Solution, O(n log n) time, O(sort) space
# Standard clever two pointer trick. Say we pick the biggest person to go into a boat. Normally we might think we need to greedily select the biggest person who can fit with them, but we can actually just put the smallest person. This is because the 2nd biggest person would free up more space anyway, so any bigger smaller person we could put with the biggest person, would also be able to be put with the second biggest person.

class Solution:
    def numRescueBoats(self, people: List[int], limit: int) -> int:
        people.sort()
        l = 0
        r = len(people) - 1
        res = 0
        while l <= r:
            if people[l] + people[r] <= limit:
                l += 1
                r -= 1
            else:
                r -= 1
            res += 1
        return res
