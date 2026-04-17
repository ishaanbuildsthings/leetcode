# class Solution:
#     def wordBreak(self, s: str, wordDict: List[str]) -> bool:
#         words = set(wordDict)

#         @cache
#         def dp(l):
#             if l == len(s):
#                 return True

#             for i in range(l, len(s)):
#                 curWord = s[l:i + 1]
#                 if curWord in words:
#                     if dp(i + 1):
#                         return True
            
#             return False
        
#         return dp(0)

class Solution:
    def wordBreak(self, s: str, wordDict: List[str]) -> bool:
        wordSet = set(wordDict)

        @cache
        def dp(i):
            # base case
            if i == len(s):
                return True

            resThis = False
            
            for rightEdge in range(i, len(s)):
                substring = s[i:rightEdge + 1]
                if substring in wordSet:
                    resThis = resThis or dp(rightEdge + 1)
            
            return resThis
        
        return dp(0)