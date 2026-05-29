class Solution:
    def findRepeatedDnaSequences(self, s: str) -> List[str]:
        res = []
        counter = Counter()
        for l in range(len(s) - 9):
            window = s[l:l+10]
            counter[window] += 1
            if counter[window] == 2:
                res.append(window)
        return res