# https://leetcode.com/problems/24-game/
# Difficulty: Hard
# Tags: backtracking

# Problem
# You are given an integer array cards of length 4. You have four cards, each containing a number in the range [1, 9]. You should arrange the numbers on these cards in a mathematical expression using the operators ['+', '-', '*', '/'] and the parentheses '(' and ')' to get the value 24.

# You are restricted with the following rules:

# The division operator '/' represents real division, not integer division.
# For example, 4 / (1 - 2 / 3) = 4 / (1 / 3) = 12.
# Every operation done is between two numbers. In particular, we cannot use '-' as a unary operator.
# For example, if cards = [1, 1, 1, 1], the expression "-1 - 1 - 1 - 1" is not allowed.
# You cannot concatenate numbers together
# For example, if cards = [1, 2, 1, 2], the expression "12 + 12" is not valid.
# Return true if you can get such expression that evaluates to 24, and false otherwise.

# Solution, O(1) time and space
# For any state, take two numbers and try all operations. Simplify the state. We use an epsilon to account for floating point errors. I copied arrays since n<=4 and it simplifies the code.

class Solution:
    def judgePoint24(self, currCards: List[int]) -> bool:
        # base case
        if len(currCards) == 1:
            return currCards[0] > 23.999 and currCards[0] < 24.001

        # iterate over all possible pairs of numbers, and all operations
        for i in range(len(currCards)):
            for j in range(len(currCards)):
                if i == j:
                    continue
                num1 = currCards[i]
                num2 = currCards[j]
                for operation in range(4):
                    if operation == 0:
                        newNum = num1 + num2
                    elif operation == 1:
                        newNum = num1 - num2
                    elif operation == 2:
                        newNum = num1 * num2
                    elif operation == 3:
                        if num2 == 0: continue # no divide by 0
                        newNum = num1 / num2

                    # create the new array of cards that is 1 length shorter
                    newArray = currCards.copy()
                    newArray.pop(max(i, j))
                    newArray.pop(min(i, j))
                    newArray.append(newNum)
                    if self.judgePoint24(newArray):
                        return True
        return False
