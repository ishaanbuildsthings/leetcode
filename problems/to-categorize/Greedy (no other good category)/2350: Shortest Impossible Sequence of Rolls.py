# https://leetcode.com/problems/shortest-impossible-sequence-of-rolls/description/
# difficulty: hard
# tags: greedy

# Problem
# You are given an integer array rolls of length n and an integer k. You roll a k sided dice numbered from 1 to k, n times, where the result of the ith roll is rolls[i].

# Return the length of the shortest sequence of rolls that cannot be taken from rolls.

# A sequence of rolls of length len is the result of rolling a k sided dice len times.

# Note that the sequence taken does not have to be consecutive as long as it is in order.

# Solution, O(n) time, O(k) space
# Just iterate until we find all k characters, then add one to result. Basically we're looking for the worst sequence possible.

class Solution:
    def shortestSequence(self, rolls: List[int], k: int) -> int:
        # starting from l to r, find the first index of the last number
        def lastIndex(l):
            seen = set()
            for i in range(l, len(rolls)):
                seen.add(rolls[i])
                if len(seen) == k:
                    return i
            return None

        res = 0
        r = 0
        while r < len(rolls):
            j = lastIndex(r)
            if j == None:
                break

            r = j + 1
            res += 1

        return res + 1
