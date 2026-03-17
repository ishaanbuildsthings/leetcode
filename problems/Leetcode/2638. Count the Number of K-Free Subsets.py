@cache
def dp(numsLeft):
    if numsLeft <= 0:
        return 1
    ifPickHere = dp(numsLeft - 2)
    ifSkip = dp(numsLeft - 1)
    return ifPickHere + ifSkip

class Solution:
    def countTheNumOfKFreeSubsets(self, nums: List[int], k: int) -> int:
        nums.sort()
        nSet = set(nums)
        groups = []
        for num in nums:
            if not num in nSet:
                continue
            curr = num
            group = []
            while True:
                group.append(curr)
                nSet.remove(curr)
                curr += k
                if not curr in nSet:
                    break
            groups.append(group)
        
        res = 1
        for g in groups:
            opts = dp(len(g))
            res *= opts
        return res

        # 0 [  7 10 12 15 20 25 30]
