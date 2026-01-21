class Solution:
    def maxDistance(self, words: List[str]) -> int:
        res = 0
        for i in range(len(words) - 1, 0, -1):
            if words[i] != words[0]:
                res = i + 1
                break
            
        for i in range(len(words) - 1):
            if words[i] != words[-1]:
                res = max(res, len(words) - i)
        
        return res