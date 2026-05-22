class Solution:
    def smallestBeautifulString(self, s: str, k: int) -> str:
        # find the rightmost letter we can break
        # we need to be greater than original, not equal to the left or right, avoid palindromes of size 3

        # this is the shittiest code i have ever written
        n = len(s)
        ans = None
        ABC = 'abcdefghijklmnopqrstuvwxyz'
        maxAllowed = ABC[k-1]

        def smallestLetterNotInTheseTwo(setOf2):
            if 'a' not in setOf2:
                return 'a'
            if 'b' not in setOf2:
                return 'b'
            return 'c'
 
        for i in range(n - 1, -1, -1):
            v = s[i]
            if v == 'z':
                continue
            bigger = chr(ord(v) + 1)
            traps = set()
            for j in range(max(0, i - 2), i):
                traps.add(s[j])
            
            if bigger in traps:
                if bigger == 'z':
                    continue
                bigger = chr(ord(bigger) + 1)
            if bigger in traps:
                if bigger == 'z':
                    continue
                bigger = chr(ord(bigger) + 1)
            if bigger in traps:
                if bigger == 'z':
                    continue
                bigger = chr(ord(bigger) + 1)
            if bigger in traps:
                if bigger == 'z':
                    continue
                bigger = chr(ord(bigger) + 1)
            
            if bigger > maxAllowed:
                continue

            current = s[:i] + bigger

            if i == n - 1:
                ans = current
                break
            
            nxt = 'a'
            prev = s[i-1] if i else '?'
            if nxt == prev or nxt == bigger:
                nxt = 'b'
            if nxt == prev or nxt == bigger:
                nxt = 'c'
            
            current = current

            setOfTwo = set()
            setOfTwo.add(nxt)
            setOfTwo.add(bigger)
            tile = nxt
            tile = tile + smallestLetterNotInTheseTwo(setOfTwo)
            nset = {tile[0], tile[1]}
            tile = tile + smallestLetterNotInTheseTwo(nset)
            
            rightSpots = len(s) - (i + 1)
            tilesUsed = math.ceil(rightSpots / 3)
            right = ''.join([tile * tilesUsed])

            ans = current + right
            ans = ans[:len(s)]
            break
        
        if not ans:
            return ''
        ABC = 'abcdefghijklmnopqrstuvwxyz'
        for x in ans:
            maxAllowed = ABC[k-1]
        if any(x > ABC[k-1] for x in ans):
            return ''
        
        return ans

            