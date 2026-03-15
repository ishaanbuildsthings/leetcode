class Solution:
    def countWords(self, words1: List[str], words2: List[str]) -> int:
        c1 = Counter(words1)
        c2 = Counter(words2)
        # can be way more optimal lol
        return sum(
            c1[word] == 1 == c2[word] for word in list(set(list(set(words1)) + list(set(words2)))) 
        )