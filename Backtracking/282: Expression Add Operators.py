# https://leetcode.com/problems/expression-add-operators/description/
# difficulty: hard
# tags: backtracking

# Problem
# Given a string num that contains only digits and an integer target, return all possibilities to insert the binary operators '+', '-', and/or '*' between the digits of num so that the resultant expression evaluates to the target value.

# Note that operands in the returned expressions should not contain leading zeros.

# Solution
# I built a function to evaluate a statement in O(n) time. Then I did 4^n backtracking. Other people seemed to evaluate on the fly, I need to think about how to do that because it seems tricky when factoring in PEMDAS.

OPS = '+-*'
class Solution:
    def addOperators(self, num: str, target: int) -> List[str]:
        def evalExpression(arr):
            stack = []
            for i, val in enumerate(arr):
                if not stack:
                    stack.append(val)
                    continue
                if val in OPS:
                    stack.append(val)
                    continue

                curr = int(val) # multiplied value

                while stack and stack[-1] == '*':
                    stack.pop() # clear the multiplication
                    prev = stack.pop() # previous number
                    curr *= int(prev)

                stack.append(curr)

            res = int(stack[0])
            for i in range(2, len(stack), 2):
                if stack[i - 1] == '+':
                    res += int(stack[i])
                else:
                    res -= int(stack[i])
            return res

        ans = []
        def backtrack(acc, i):
            # base
            if i == len(num):
                if evalExpression(acc) == target:
                    ans.append(''.join(acc[:]))
                return

            prevNum = acc[-1] if acc else ''
            newStrNum = prevNum + num[i]

            # try appending number rather than an operation, but don't lead with a 0
            if prevNum != '0':
                if not acc:
                    acc.append(newStrNum)
                else:
                    acc[-1] = newStrNum
                backtrack(acc, i + 1)
                # undo
                if prevNum == '':
                    acc.pop()
                else:
                    acc[-1] = prevNum

            if acc:
                for op in OPS:
                    acc.append(op)
                    acc.append(num[i])
                    backtrack(acc, i + 1)
                    acc.pop()
                    acc.pop()

        backtrack([], 0)
        return ans
