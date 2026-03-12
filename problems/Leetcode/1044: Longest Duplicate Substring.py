class Solution:
    def longestDupSubstring(self, s: str) -> str:
        MOD = 10**9 + 7
        mods = [] # mods[i] tells us 10^i % MOD
        curr = 1 # starts at 10^0
        # the biggest length s can be is 3*10^4 (question constraint), so the biggest window size is 3*10^4
        # this means the biggest power we might need in the rolling hash is 3*10^4, so that's the max we calculate
        for i in range(3 * 10**4):
            mods.append(curr)
            curr *= 26 # for instance we go from 10^3 to 10^4, by multiplying by 10
            curr %= MOD # but we cap it to our max size to prevent it from becoming big

        length = len(s)
        lo, hi = 1, length-1
        ans = ""
        BASE = 26

        def getVal(c):
            return ord(c)-ord('a')+1

        def returnDup(size):
            start, end = 0, size-1
            hashVal = 0
            hashValToCoords = defaultdict(list)
            for i in range(size):
                hashVal = (hashVal * BASE + getVal(s[i])) % MOD
            while end < length+1:
                if hashVal in hashValToCoords: 
                    # print(f'hash val: {hashVal} was in hashVal to coords. current string: {s[start:end+1]}. coords: {hashValToCoords[hashVal]}')
                    # return s[start:end+1]
                    currStr = s[start:end+1]
                    for (prevStart, prevEnd) in hashValToCoords[hashVal]:
                        if s[prevStart:prevEnd] == currStr: return currStr
                hashValToCoords[hashVal].append((start, end+1))
                if end+1 == length: break
                hashVal -= getVal(s[start]) * (mods[size - 1])
                hashVal *= BASE
                hashVal += getVal(s[end+1])
                hashVal %= MOD
                start += 1
                end += 1
            return ""

        while lo <= hi:
            size = lo + ((hi-lo)//2)
            dup = returnDup(size)
            if dup != "":
                ans = dup
                lo = size+1
            else: hi = size-1
        return ans