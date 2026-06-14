class Solution:
    def reachNumber(self, target: int) -> int:
        runningSum = 0
        i = 0
        target = abs(target)
        while runningSum < target:
            runningSum += (i + 1)
            i += 1

        if runningSum == target:
            return i
        if (runningSum - target) % 2 == 0:
            return i
        # if we overshot by an odd amount, and the next step we make is even, we cannot fix the parity
        if i % 2 == 0:
            return i + 1
        return i + 2

        # 0->1
        # 1->3
        # 3->6
        # 6->10
        # 10->15