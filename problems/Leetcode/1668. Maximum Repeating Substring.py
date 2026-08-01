class Solution:
    def maxRepeating(self, sequence: str, word: str) -> int:
        # can use binary search + rolling hash for n log n, though seems like some people did kmp for n? would need to look into this
        for repeats in range(len(sequence) // len(word), -1, -1):
            if word * repeats in sequence:
                return repeats
