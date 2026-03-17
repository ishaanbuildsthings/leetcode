class Solution:
    def queryString(self, s: str, n: int) -> bool:
        seen = set()
        for size in range(1, 33):
            if size > len(s):
                break
            init = 0
            for i in range(size):
                init *= 2
                init += s[i] == '1'
            seen.add(init)
            for r in range(size, len(s)):
                lostChar = s[r - size]
                if lostChar == '1':
                    init -= (2**(size-1))
                init *= 2
                if s[r] == '1':
                    init += 1
                seen.add(init)
        seen.discard(0)
        return all(
            x in seen for x in range(1, n + 1)
        )