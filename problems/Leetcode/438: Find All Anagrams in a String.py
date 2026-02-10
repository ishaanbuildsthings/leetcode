class Solution:
    def findAnagrams(self, s: str, p: str) -> List[int]:
        if len(s) < len(p):
            return []

        pCounts = Counter(p)
        windowCounts = Counter(s[i] for i in range(len(p)))

        have = sum(1 if windowCounts[char] >= pCounts[char] and pCounts[char] else 0 for char in windowCounts)
        need = len(pCounts)

        l = 0
        r = len(p) - 1

        res = [0] if have == need else []
        while r < len(s) - 1:
            
            lostChar = s[l]
            windowCounts[lostChar] -= 1
            if windowCounts[lostChar] == pCounts[lostChar] - 1:
                have -= 1

            gainedChar = s[r + 1]
            windowCounts[gainedChar] += 1
            if windowCounts[gainedChar] == pCounts[gainedChar]:
                have += 1
            
            l += 1
            r += 1

            if have == need:
                res.append(l)
        
        return res