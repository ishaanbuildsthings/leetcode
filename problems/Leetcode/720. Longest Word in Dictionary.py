class Solution:
    def longestWord(self, words: List[str]) -> str:
        # can insert all words into a trie and denote endings then navigate that trie for all words but im lazy

        seen = set(words)
        res = None
        for w in words:
            if res and len(w) < len(res):
                continue
            if res and len(w) == len(res) and w > res:
                continue
            hasFailed = False
            for size in range(1, len(w) + 1):
                substring = w[:size]
                if not substring in seen:
                    hasFailed = True
                    break
            if not hasFailed:
                res = w
        return res or ""