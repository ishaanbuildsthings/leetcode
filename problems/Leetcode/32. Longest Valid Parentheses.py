class Solution:
    def longestValidParentheses(self, s: str) -> int:

        # longest valid starting at i
        # @cache
        # def dp(i):
        #     if i >= len(s) - 1:
        #         return 0
        #     if s[i] == ')':
        #         return 0
        #     if s[i + 1] == ')':
        #         return 2 + dp(i + 2)
            
        #     # ( ( case
        #     longestRight = dp(i + 1)
        #     L = i + 1
        #     R = L + longestRight - 1

        #     if R + 1 < len(s) and s[R + 1] == ')':
        #         ans = 2 + longestRight + dp(R + 2)
        #         return ans
            
        #     return 0
        
        # res = 0
        # for i in range(len(s)):
        #     res = max(res, dp(i))
        
        # return res



        # stack solution
        stack = []
        for i, v in enumerate(s):
            if v == ')' and stack and s[stack[-1]] == '(':
                stack.pop()
                continue
            elif v == ')':
                stack.append(i)
                continue
            stack.append(i)
        stack.append(len(s))
        res = 0
        for i, v in enumerate(stack):
            prev = -1 if not i else stack[i - 1]
            width = v - prev - 1
            res = max(res, width)
        return res