class Solution:
    def minSwaps(self, nums: List[int]) -> int:
        # either 01010... or 101010...
        def arrange(zeroFirst):
            zeroes = [i for i in range(len(nums)) if nums[i] % 2 == 0]
            ones = [i for i in range(len(nums)) if nums[i] % 2]
            res = zI = oI = 0

            try:
                sl = SortedList(range(len(nums)))
                # try 0 first
                for i in range(len(nums)):
                    req = i % 2
                    if not zeroFirst:
                        req ^= 1
                    early = zeroes[zI] if req == 0 else ones[oI]
                    realPos = sl.index(early)
                    res += realPos
                    sl.pop(realPos)
                    if req % 2:
                        oI += 1
                    else:
                        zI += 1
                return res
            except:
                return inf
        
        ans = min(arrange(True), arrange(False))
        return ans if ans != inf else -1
                