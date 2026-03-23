class Solution:
    def maxPalindromesAfterOperations(self, words: List[str]) -> int:
        c = Counter(letter for w in words for letter in w)
        sizes = sorted(len(w) for w in words)
        pairs = sum(v // 2 for v in c.values())
        res = 0
        for sz in sizes:
            need = sz // 2
            if pairs >= need:
                pairs -= need
                res += 1
            else:
                break
        return res