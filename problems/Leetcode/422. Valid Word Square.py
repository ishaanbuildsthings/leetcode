class Solution:
    def validWordSquare(self, words: List[str]) -> bool:
        height = len(words)
        width = max(len(w) for w in words)
        if height != width:
            return False
        for r in range(height):
            w1 = words[r]
            w2 = []
            for r2 in range(len(w1)):
                if r >= len(words[r2]):
                    return False
                v = words[r2][r]
                w2.append(v)
            if ''.join(w2) != w1:
                return False
        return True 