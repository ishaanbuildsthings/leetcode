class Solution:
    def waysToMakeFair(self, nums: List[int]) -> int:
        pfOdds = [] # sum of the first i+1 odd numbers
        pfEvens = []
        currOddSum = 0
        currEvenSum = 0
        for i, val in enumerate(nums):
            if i % 2 == 0:
                currEvenSum += val
            else:
                currOddSum += val
            pfEvens.append(currEvenSum)
            pfOdds.append(currOddSum)

        def query(l, r, isOdd):
            if l > r: return 0
            if r < 0: return 0
            if isOdd:
                return pfOdds[r] - (pfOdds[l - 1] if l else 0)
            return pfEvens[r] - (pfEvens[l - 1] if l else 0)

        res = 0

        for i in range(len(nums)):
            beforeOdd = query(0, i - 1, True)
            beforeEven = query(0, i - 1, False)
            afterOdd = query(i + 1, len(nums) - 1, False) if i < len(nums) - 1 else 0
            afterEven = query(i + 1, len(nums) - 1, True) if i < len(nums) - 1 else 0
            res += (beforeOdd + afterOdd) == (beforeEven + afterEven)
        
        return res
