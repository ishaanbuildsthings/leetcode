class Solution:
    def maxNumOfSubstrings(self, s: str) -> List[str]:
        n = len(s)
        rightmost = {}
        leftmost = {}
        for i in range(n - 1, -1, -1):
            v = s[i]
            if v not in rightmost:
                rightmost[v] = i
            leftmost[v] = i
        
        ABC = sorted(set([x for x in s]))
        pfSums = {}
        for letter in ABC:
            curr = 0
            pf = []
            for v in s:
                curr += v == letter
                pf.append(curr)
            pfSums[letter] = pf
        
        def query(l, r, letter):
            pf = pfSums[letter]
            return pf[r] - (pf[l - 1] if l else 0)

        ranges = []
        
        for letter in ABC:
            L = leftmost[letter]
            R = rightmost[letter]
            while True:
                l = inf
                r = -inf
                for letter in ABC:
                    amt = query(L, R, letter)
                    if amt:
                        l = min(l, leftmost[letter])
                        r = max(r, rightmost[letter])
                if l == L and r == R:
                    break
                L = l
                R = r
            ranges.append((L, R))
        
        ranges.sort(key = lambda x : x[1])

        res = []
        prevStart = ranges[0][0]
        prevEnd = ranges[0][1]
        for l, r in ranges[1:]:
            if l <= prevEnd:
                continue
            res.append((prevStart, prevEnd))
            prevStart = l
            prevEnd = r
        res.append((prevStart, prevEnd))
        
        resArr = []
        for l, r in res:
            resArr.append(s[l:r+1])
        
        return resArr