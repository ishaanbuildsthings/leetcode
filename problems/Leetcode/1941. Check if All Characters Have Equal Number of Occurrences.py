class Solution:
    def areOccurrencesEqual(self, s: str) -> bool:
        abc = list(set(s)) # could avoid this pass, or just check counter values
        c = Counter(s)
        return all(c[char] == c[abc[0]] for char in abc)