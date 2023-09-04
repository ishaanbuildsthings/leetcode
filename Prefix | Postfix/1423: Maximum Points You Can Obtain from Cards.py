# https://leetcode.com/problems/maximum-points-you-can-obtain-from-cards/
# Difficulty: Medium
# Tags: prefix, range query

# Problem
# There are several cards arranged in a row, and each card has an associated number of points. The points are given in the integer array cardPoints.

# In one step, you can take one card from the beginning or from the end of the row. You have to take exactly k cards.

# Your score is the sum of the points of the cards you have taken.

# Given the integer array cardPoints and the integer k, return the maximum score you can obtain.

# Solution, O(n) time and O(n) space
# We can just test taking 0-n cards from the left, and the remaining from the right. We use a range query to get our score in O(1).

class Solution:
    def maxScore(self, cardPoints: List[int], k: int) -> int:
        n = len(cardPoints)
        # prefix[i] tells us the sum for all the numbers before it
        prefix = []
        running_sum = 0
        for i in range(n):
            prefix.append(running_sum)
            running_sum += cardPoints[i]
        prefix.append(running_sum)

        # returns the sum for prefix[l:r]
        def range_query(l, r):
            return prefix[r + 1] - prefix[l]

        result = 0

        for take_from_left in range(k + 1):
            if take_from_left == 0:
                score_left = 0
            else:
                score_left = range_query(0, take_from_left - 1)
            take_from_right = k - take_from_left
            if take_from_right == 0:
                score_right = 0
            else:
                score_right = range_query(n - take_from_right, n - 1)
            result = max(result, score_left + score_right)

        return result