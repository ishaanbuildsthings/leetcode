class Solution:
    def subarraysWithKDistinct(self, nums: List[int], k: int) -> int:
        n = len(nums)
        
        def countLteX(x):
            l = r = res = 0
            frq = Counter()
            while r < n:
                gain = nums[r]
                frq[gain] += 1
                while len(frq) > x:
                    lost = nums[l]
                    frq[lost] -= 1
                    if not frq[lost]: del frq[lost]
                    l += 1
                res += r - l + 1
                r += 1

            return res
        
        return countLteX(k) - countLteX(k-1)
            