class Solution:
    def isBalanced(self, num: str) -> bool:
        evens = 0
        odds = 0
        for i in range(len(num)):
            if i % 2 == 0:
                evens += int(num[i])
            else:
                odds += int(num[i])
        return evens == odds