class Solution:
    def getLength(self, nums: List[int]) -> int:
        res = 1

        for l in range(len(nums)):
            numToFrq = defaultdict(int)
            frqToNums = defaultdict(int)
            mxFrq = 0
            for r in range(l, len(nums)):
                # print(f'{l=} {r=}')
                v = nums[r]
                prev = numToFrq[v]
                numToFrq[v] += 1
                frqToNums[prev] -= 1
                frqToNums[prev + 1] += 1
                mxFrq = max(mxFrq, numToFrq[v])
                if r == l:
                    continue
                frq = numToFrq[v]
                if mxFrq % 2:
                    continue
                # print(f'{l=} {r=}')
                half = mxFrq // 2
                # print(f'half frq is: {half}')
                countFull = frqToNums[mxFrq]
                uniqueNums = len(numToFrq)
                req = uniqueNums - countFull
                # print(f'{req=}')
                # print(f'{countFull=}')

                # ????
                if countFull > 1 and countFull * mxFrq == r - l + 1:
                    # print(f'forced to skip due to weird condition')
                    continue
                if frqToNums[half] == req:
                    res = max(res, r - l + 1)
                    # print(f'res now: {res} at {l=} {r=}')

        return res


# nums =
# [1,1,1,3,4]
# Use Testcase
# Output
# 2
# Expected
# 4



# Wrong Answer
# 911 / 916 testcases passed
# Input
# nums =
# [1,2,1,1,2]
# Use Testcase
# Output
# 4
# Expected
# 3


# nums =
# [1,1,8,5,3,9,9,5,4,5]
# Use Testcase
# Output
# 8
# Expected
# 9