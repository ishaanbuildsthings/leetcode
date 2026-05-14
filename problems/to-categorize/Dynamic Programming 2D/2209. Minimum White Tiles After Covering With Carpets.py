# https://leetcode.com/problems/minimum-white-tiles-after-covering-with-carpets/description/
# difficulty: hard
# tags: dynamic programming 2d

# Problem
# You are given a 0-indexed binary string floor, which represents the colors of tiles on a floor:

# floor[i] = '0' denotes that the ith tile of the floor is colored black.
# On the other hand, floor[i] = '1' denotes that the ith tile of the floor is colored white.
# You are also given numCarpets and carpetLen. You have numCarpets black carpets, each of length carpetLen tiles. Cover the tiles with the given carpets such that the number of white tiles still visible is minimum. Carpets may overlap one another.

# Return the minimum number of white tiles still visible.

# Solution, O(n*c) time and space, I could have inverted the dp to not use a pf query, wrote this on my phone in a line at trader joe's lol

class Solution:
    def minimumWhiteTiles(self, floor: str, numCarpets: int, carpetLen: int) -> int:

        pf=[]
        curr=0
        for char in floor:
            curr+=char=='1'
            pf.append(curr)
        def query(l,r):
            biggest = min(r, len(floor) - 1)
            if l==0:
                return pf[biggest]
            return pf[biggest]-pf[l-1]

        @cache
        def dp(i, c):
            #base
            if i >= len(floor) or c == 0: return 0
            return max(dp(i+1,c), query(i,i+carpetLen-1) + dp(i+carpetLen,c-1))

        return pf[-1] - dp(0,numCarpets)