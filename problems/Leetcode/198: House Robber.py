class Solution:
    def rob(self, nums: List[int]) -> int:
        didntRobLast = 0
        didRobLast = 0
        for num in nums:
            ifRobHere = num + didntRobLast
            ifDontRobHere = max(didntRobLast, didRobLast)
            didntRobLast = ifDontRobHere
            didRobLast = ifRobHere
        return max(didntRobLast, didRobLast)

        