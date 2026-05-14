# https://leetcode.com/problems/find-players-with-zero-or-one-losses/
# difficulty: medium

# Problem
# You are given an integer array matches where matches[i] = [winneri, loseri] indicates that the player winneri defeated player loseri in a match.

# Return a list answer of size 2 where:

# answer[0] is a list of all players that have not lost any matches.
# answer[1] is a list of all players that have lost exactly one match.
# The values in the two lists should be returned in increasing order.

# Note:

# You should only consider the players that have played at least one match.
# The testcases will be generated such that no two matches will have the same outcome.

# Solution, O(n log n) time, O(n) space
# I counted each match then sorted the result lists.
# We could iterate my the team in increasing order to prevent needing to sort


class Solution:
    def findWinners(self, matches: List[List[int]]) -> List[List[int]]:
        losses = {}
        for a, b in matches:
            if not b in losses:
                losses[b] = 1
            else:
                losses[b] += 1
            if not a in losses:
                losses[a] = 0

        res = [[], []]
        for team in losses.keys():
            lossAmount = losses[team]
            if not lossAmount:
                res[0].append(team)
            elif lossAmount == 1:
                res[1].append(team)
        res[0].sort()
        res[1].sort()
        return res