class Solution:
    def singleNumber(self, nums: List[int]) -> int:
        once = twice = 0
        for v in nums:
            oldOnceThatDidntAdvance = (once & ~v) # an existing with paired with a current 0, is prev1 AND inverted(0)
            oldOnceThatAdvanced = once & v

            oldTwiceThatDidntAdvance = (twice & ~v)
            oldTwiceThatAdvanced = twice & v

            oldZero = ~once & ~twice
            oldZeroThatAdvanced = oldZero & v

            newOnce = oldOnceThatDidntAdvance | oldZeroThatAdvanced
            newTwice =  oldTwiceThatDidntAdvance | oldOnceThatAdvanced

            once = newOnce
            twice = newTwice
        
        return once