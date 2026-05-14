# https://leetcode.com/problems/number-of-ways-to-build-house-of-cards/description/
# difficulty: medium
# tags: dynamic programming 2d

# problem
# You are given an integer n representing the number of playing cards you have. A house of cards meets the following conditions:

# A house of cards consists of one or more rows of triangles and horizontal cards.
# Triangles are created by leaning two cards against each other.
# One card must be placed horizontally between all adjacent triangles in a row.
# Any triangle on a row higher than the first must be placed on a horizontal card from the previous row.
# Each triangle is placed in the leftmost available spot in the row.
# Return the number of distinct house of cards you can build using all n cards. Two houses of cards are considered distinct if there exists a row where the two houses contain a different number of cards.

# Solution, O(n^3) time and O(n^2) space (but a fraction constant factor)
# We can make a subproblem of the width and the cards left, and it takes cards left time.
class Solution:
    def houseOfCards(self, n: int) -> int:
        @cache
        def dp(width, cardsLeft):
            # base case
            if cardsLeft == 0:
                return 1

            resForThis = 0

            maxTrianglesWeCanPlace = min(width, 1 + (cardsLeft - 2) // 3)
            for placedTriangles in range(1, maxTrianglesWeCanPlace + 1):
                nextWidth = placedTriangles - 1
                if placedTriangles == 1:
                    nextCards = cardsLeft - 2
                else:
                    nextCards = cardsLeft - 2 - ((placedTriangles - 1) * 3)
                resForThis += dp(nextWidth, nextCards)

            return resForThis

        return dp(float('inf'), n)


        #  170*170*170