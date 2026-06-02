class Solution:
    def mostCommonWord(self, paragraph: str, banned: List[str]) -> str:
        bSet = set(banned)
        p = ''.join(c if c not in "!?';,." else ' ' for c in paragraph)
        split = [word for word in p.split(' ') if word != ' ' and word != '']
        c = Counter(w.lower() for w in split)
        big = 0
        res = None
        for key in c:
            if key in bSet:
                continue
            if c[key] > big:
                res = key
                big = c[key]
        return res
            