class Solution:
    def canMakeEqual(self, nums: List[int], k: int) -> bool:
        # all 1
        opsEven = 0
        ones = nums[:]
        for i in range(len(ones) - 1):
            if ones[i] == -1:
                opsEven += 1
                ones[i + 1] *= -1

        # make all neg
        twos = nums[:]
        opsnegs = 0
        for i in range(len(twos) - 1):
            if twos[i] == 1:
                opsnegs += 1
                twos[i + 1] *= - 1
        if opsEven <= k and ones[-1] == 1:
            return True
        if opsnegs <= k and twos[-1] == -1:
            return True
        return False
        print(opsEven, opsnegs)
        return min(opsEven, opsnegs) <= k