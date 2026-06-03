class Solution:
    def wordSubsets(self, words1: List[str], words2: List[str]) -> List[str]:
        maxCounts = Counter()
        for word in words2:
            wordCounts = Counter(word)
            for char in wordCounts:
                maxCounts[char] = max(maxCounts[char], wordCounts[char])

        res = []
        for word in words1:
            wordCounts = Counter(word)
            if all(
                wordCounts[char] >= maxCounts[char] for char in maxCounts
            ):
                res.append(word)
        return res
    