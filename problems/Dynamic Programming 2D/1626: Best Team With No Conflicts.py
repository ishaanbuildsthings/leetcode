# https://leetcode.com/problems/best-team-with-no-conflicts/
# difficulty: medium
# tags: dynamic programming 2d

# Problem
# You are the manager of a basketball team. For the upcoming tournament, you want to choose the team with the highest overall score. The score of the team is the sum of scores of all the players in the team.

# However, the basketball team is not allowed to have conflicts. A conflict exists if a younger player has a strictly higher score than an older player. A conflict does not occur between players of the same age.

# Given two lists, scores and ages, where each scores[i] and ages[i] represents the score and age of the ith player, respectively, return the highest overall score of all possible basketball teams.

# Solution
# I had some notes about amortization or binary search tricks

class Solution:
    def bestTeamScore(self, scores: List[int], ages: List[int]) -> int:
        # I think TC gets amortized, could maybe do some binary search tricks inside the dp

        zipped = [[ages[i], scores[i]] for i in range(len(scores))]
        zipped.sort()

        nextIndex = {} # maps an age to the index for the next age
        currNextIndex = None
        for i in range(len(zipped) - 1, -1, -1):
            age, score = zipped[i]
            if i == len(zipped) - 1 or age != zipped[i + 1][0]:
                currNextIndex = i + 1
            nextIndex[age] = currNextIndex

        @cache
        def dp(i, maxScoreTaken):
            if i == len(scores):
                return 0

            age = zipped[i][0]
            nextAgeIndex = nextIndex[age]

            resThis = dp(nextAgeIndex, maxScoreTaken) # if we skip everyone of this age

            tot = 0
            accMax = maxScoreTaken
            for j in range(i, nextAgeIndex):
                score = zipped[j][1]
                if score < maxScoreTaken:
                    continue

                tot += score
                accMax = max(accMax, score)
                resThis = max(resThis, dp(nextAgeIndex, accMax) + tot)


            return resThis

        return dp(0, float('-inf'))