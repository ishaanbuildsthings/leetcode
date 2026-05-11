X = 10**5
numToFacs = [[] for _ in range(X + 5)]
for fac in range(1, X + 1):
    mult = 1
    while fac * mult <= X:
        big = fac * mult
        numToFacs[big].append(fac)
        mult += 1
        
class Solution:
    def minArraySum(self, nums: list[int]) -> int:
        nums.sort()
        res = 0

        # print(numToFacs)

        # every divisor is going to knock down its multiples

        numToScore = {}
        numSet = set(nums)
        for num in nums:
            if num in numToScore:
                res += numToScore[num]
                continue
            for fac in numToFacs[num]:
                if fac in numSet:
                    numToScore[num] = fac
                    res += fac
                    break

        return res