class Solution:
    def detectCapitalUse(self, word: str) -> bool:
        return all(
            c.islower() for c in word
        ) or all(
            c.isupper() for c in word
        ) or word[0].isupper() and not any(
            word[i].isupper() for i in range(1, len(word))
        )