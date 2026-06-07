class Solution:
    def minWindow(self, s: str, t: str) -> str:
        goalCounts = Counter(t)
        currCounts = Counter()

        def haveEnoughCounts():
            return all(
                currCounts[char] >= goalCounts[char]
                for char in goalCounts
            )

        resL = None
        resR = None
        res = float('inf')

        l = r = 0
        while r < len(s):
            newChar = s[r]
            if goalCounts[newChar]:
                currCounts[newChar] += 1
                while haveEnoughCounts():
                    if r - l + 1 < res:
                        res = r - l + 1
                        resL = l
                        resR = r
                    lostChar = s[l]
                    if currCounts[lostChar]:
                        currCounts[lostChar] -= 1
                    l += 1
                    
            r += 1
        
        return s[resL:resR + 1] if res != float('inf') else ''

            
            