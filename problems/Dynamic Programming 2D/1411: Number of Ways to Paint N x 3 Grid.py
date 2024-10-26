# https://leetcode.com/problems/number-of-ways-to-paint-n-3-grid/
# difficulty: hard
# tags: dynamic programming 2d

# problem
# You have a grid of size n x 3 and you want to paint each cell of the grid with exactly one of the three colors: Red, Yellow, or Green while making sure that no two adjacent cells have the same color (i.e., no two cells that share vertical or horizontal sides have the same color).

# Given n the number of rows of the grid, return the number of ways you can paint this grid. As the answer may grow large, the answer must be computed modulo 109 + 7.

# Solution, O(n * 12 * 12) time, O(n * 12) space.
# Maintain the prior state. We can use one of up to 12 new states (really this upper bound is less). I left commented code in to see how I initially solved it, but I quickly refactored to a faster solution that cached a better state.

MOD = 10**9 + 7
STATES = ['ryr', 'yry', 'gry', 'ryg', 'yrg', 'grg', 'rgr', 'ygr', 'gyr', 'rgy', 'ygy', 'gyg']

@cache
def validStates(prev):
    valid = []
    for state in STATES:
        errorFound = False
        for i in range(3): # n x 3 size
            if prev[i] == state[i]:
                errorFound = True
                break
        if not errorFound:
            valid.append(state)
    return valid

class Solution:
    def numOfWays(self, n: int) -> int:
        # @cache
        # def isValidNext(oldState, newState):
        #     for i in range(3): # n x 3 size
        #         if oldState[i] == newState[i]:
        #             return False
        #     return True


        @cache
        def dp(i, prev):
            # base case
            if i == n:
                return 1

            resForThis = 0
            valids = validStates(prev)
            for valid in valids:
                resForThis += dp(i + 1, valid)
            # for state in STATES:
            #     if isValidNext(prev, state):
            #         resForThis += dp(i + 1, state)
            return resForThis % MOD

        return dp(0, 'aaa')

