class Solution:
    def mapWordWeights(self, words: List[str], weights: List[int]) -> str:
        res = []
        string = 'abcdefghijklmnopqrstuvwxyz'[::-1]
        for w in words:
            sz = 0
            for chr in w:
                order = ord(chr) - ord('a')
                sz += weights[order]
            sz %= 26
            res.append(string[sz])
        return ''.join(res)
            
                