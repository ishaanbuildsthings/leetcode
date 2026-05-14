# https://leetcode.com/problems/minimum-levels-to-gain-more-points/description/
# difficulty: medium
# tags: prefix/postfix, range query

# Solution, O(n) time O(n) space

class Solution:
    def minimumLevels(self, possible: List[int]) -> int:
        pf = []
        tot = 0
        for i in range(len(possible)):
            tot += possible[i]
            pf.append(tot)

        def query(l, r):
            if l == 0:
                return pf[r]
            return pf[r] - pf[l - 1]

        for aliceLevels in range(1, len(possible)):
            # can probably simplify these
            aliceWin = query(0, aliceLevels - 1)
            aliceLose = aliceLevels - aliceWin
            aliceScore = aliceWin - aliceLose

            bobWin = query(aliceLevels, len(possible) - 1)
            bobLose = (len(possible) - aliceLevels) - bobWin
            bobScore = bobWin - bobLose

            if aliceScore > bobScore:
                return aliceLevels

        return -1