class Solution:
    def splitLoopedString(self, strs: List[str]) -> str:
        maxs = [max(x, x[::-1]) for x in strs]
        res = ''
        for i in range(len(strs)):
            w = strs[i]
            # try max here at all break points
            for j in range(len(w)):
                wordPref = w[j:]
                after = ''.join(maxs[i + 1:])
                before = ''.join(maxs[:i])
                ending = w[:j]
                finalWord = wordPref + after + before + ending
                wordInv = w[::-1]
                wordPref2 = wordInv[j:]
                ending2 = wordInv[:j]
                finalWord2 = wordPref2 + after + before + ending2
                res = max(res, finalWord, finalWord2)
        return res
        