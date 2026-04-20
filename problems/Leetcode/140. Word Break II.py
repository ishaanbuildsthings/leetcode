class Solution:
    def wordBreak(self, s: str, wordDict: List[str]) -> List[str]:

        wordSet = set(wordDict)
        
        @cache
        def dp(l):
            # base case
            if l == len(s):
                return [""]
            resThis = []
            for allLeft in range(l, len(s)):
                left = s[l:allLeft + 1]
                if not left in wordSet:
                    continue
                splits = dp(allLeft + 1)
                for split in splits:
                    newStr = left + (' ' if split else "") + split
                    resThis.append(newStr)
            return resThis
        
        return dp(0)