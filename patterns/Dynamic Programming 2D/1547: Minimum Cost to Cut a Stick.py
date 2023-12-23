# https://leetcode.com/problems/minimum-cost-to-cut-a-stick/description/
# difficulty: hard
# tags: dynamic programming 2d

# Problem
# Given a wooden stick of length n units. The stick is labelled from 0 to n. For example, a stick of length 6 is labelled as follows:


# Given an integer array cuts where cuts[i] denotes a position you should perform a cut at.

# You should perform the cuts in order, you can change the order of the cuts as you wish.

# The cost of one cut is the length of the stick to be cut, the total cost is the sum of costs of all cuts. When you cut a stick, it will be split into two smaller sticks (i.e. the sum of their lengths is the length of the stick before the cut). Please refer to the first example for a better explanation.

# Return the minimum total cost of the cuts.

# Solution, O(cuts^3) time, O(cuts^2) space
# There's cuts^2 possible sticks we could create. Those are the subproblems. The base case is when there's nothing to cut.

class Solution:
    def minCost(self, n: int, cuts: List[int]) -> int:
        cuts.sort() # helps with pruning when we search for cuts, technically we don't need to sort this but we would need to change our early break when iterating over cuts

        @cache
        def dp(l, r):
            # base case, no cuts to be made
            cutFound = False
            for cut in cuts:
                if cut > l and cut < r:
                    cutFound = True
                    break
            if not cutFound:
                return 0

            resForThis = float('inf')
            for cut in cuts:
                if cut <= l:
                    continue
                if cut >= r:
                    break
                ifCutHere = r - l + dp(l, cut) + dp(cut, r)
                resForThis = min(resForThis, ifCutHere)
            return resForThis
        return dp(0, n)
