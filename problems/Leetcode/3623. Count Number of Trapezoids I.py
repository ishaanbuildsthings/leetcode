class Solution:
    def countTrapezoids(self, points: List[List[int]]) -> int:
        yToSegCount = defaultdict(int)
        MOD = 10**9 + 7
        totalSeg = 0
        ys = []
        res = 0
        for x, y in points:
            ys.append(y)
        ys = sorted(set(ys))
        yToPointCount = defaultdict(int)
        for x, y in points:
            yToPointCount[y] += 1
        for y in ys:
            pointCount = yToPointCount[y]
            segsHere = (pointCount) * (pointCount - 1) // 2
            totalSeg += segsHere

        print(f'{totalSeg=}')

        for y in ys:
            pointCount = yToPointCount[y]
            segsHere = (pointCount) * (pointCount - 1) // 2
            otherSeg = totalSeg - segsHere
            res += otherSeg * segsHere
        res %= MOD
        modInv2 = pow(2, MOD-2, MOD)
        res *= modInv2
        return res % MOD
        # return (res // 2
            