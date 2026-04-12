from sortedcontainers import SortedList
class Solution:
    def countMajoritySubarrays(self, nums: List[int], target: int) -> int:
        # ideas
        # enumerate the actual indices of target only
        # if we considered all pairs, we would still need to have some function
        # given the left room and the right room how many sum up to <= X
        # I think this is O(1) doable I've done it before

        # some sort of prefix array system
        # if we have 20 0s and 5 1s in a prefix we could cut off some prefixes
        # but if we cut off a 1 on the left that becomes bad because it changes things

        # enumerate left edge
        # dont see a monotonic property though dont think we can bsearch for the right edge

        # sliding window across the target indices
        # doesnt seem to work

        # binary search for the # of subarrays
        # dont see how to write a validator

        surpluses = SortedList()
        surpluses.add(0)
        res = 0
        curr = 0
        for v in nums:
            curr += (1 if v == target else -1)
            maxWeCanRemove = curr - 1
            res += surpluses.bisect_right(maxWeCanRemove)
            surpluses.add(curr)
        return res
