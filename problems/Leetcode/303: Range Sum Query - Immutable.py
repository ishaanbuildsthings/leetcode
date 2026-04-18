class NumArray:

    def __init__(self, nums: List[int]):
        pf = []
        curr = 0
        for v in nums:
            curr += v
            pf.append(curr)
        self.pf = pf

    def sumRange(self, left: int, right: int) -> int:
        return self.pf[right] - (self.pf[left - 1] if left else 0)
        


# Your NumArray object will be instantiated and called as such:
# obj = NumArray(nums)
# param_1 = obj.sumRange(left,right)