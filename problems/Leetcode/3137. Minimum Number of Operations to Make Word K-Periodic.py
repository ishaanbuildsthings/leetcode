class Solution:
    def minimumOperationsToMakeKPeriodic(self, word: str, k: int) -> int:
        c = Counter()
        for i in range(0, len(word), k):
            c[word[i:i+k]] += 1
        return (len(word) // k) - max(c.values())