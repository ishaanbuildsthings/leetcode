class Solution:
    def isPrefixString(self, s: str, words: List[str]) -> bool:
        i = 0
        for j in range(len(words)):
            if i == len(s):
                return True
            for c in words[j]:
                if i == len(s):
                    return False
                if s[i] == c:
                    i += 1
                else:
                    return False
        return i == len(s)
            