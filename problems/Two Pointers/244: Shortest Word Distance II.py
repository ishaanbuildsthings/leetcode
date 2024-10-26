# https://leetcode.com/problems/shortest-word-distance-ii/description/
# difficulty: medium
# tags: two pointers

# Solution, O(n*k) init time, O(words + chars) space, query is O(n*k) time

class WordDistance:

    def __init__(self, wordsDict: List[str]):
        self.positions = defaultdict(list)
        for i, word in enumerate(wordsDict):
            self.positions[word].append(i)

    def shortest(self, word1: str, word2: str) -> int:
        i = j = 0
        res = float('inf')
        while i < len(self.positions[word1]) and j < len(self.positions[word2]):
            dist = abs(self.positions[word1][i] - self.positions[word2][j])
            res = min(res, dist)
            if self.positions[word1][i] <= self.positions[word2][j]:
                i += 1
            else:
                j += 1
        return res


# Your WordDistance object will be instantiated and called as such:
# obj = WordDistance(wordsDict)
# param_1 = obj.shortest(word1,word2)