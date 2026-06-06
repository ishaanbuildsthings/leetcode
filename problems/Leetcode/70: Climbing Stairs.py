class Solution:
    def climbStairs(self, n: int) -> int:
        if n == 1: return 1

        first = 1 # one way to reach the first step
        second = 2 # two ways to reach the second step
        steps = 2 # solved up to steps = 2
        ways = 2 # current # of ways to reach the current steps
        while steps < n:
            ways = first + second
            steps += 1
            first = second
            second = ways
        
        return ways


