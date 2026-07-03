class Solution:
    def sumImbalanceNumbers(self, nums: List[int]) -> int:
        res = 0
        n = len(nums)
        for l in range(n):
            imbalance = 0
            sl = SortedList()
            for r in range(l, n):
                v = nums[r]
                idx = sl.bisect_left(v)
                largestNumLtV = sl[idx - 1] if idx > 0 else None
                smallestNumGteV = sl[idx] if idx < len(sl) else None

                if largestNumLtV is not None and v > largestNumLtV + 1:
                    imbalance += 1
                if smallestNumGteV is not None:
                    if largestNumLtV is not None and smallestNumGteV > largestNumLtV + 1:
                        imbalance -= 1
                    if smallestNumGteV > v + 1:
                        imbalance += 1

                sl.add(v)
                res += imbalance

        return res