class Solution:
    def slowestKey(self, releaseTimes: List[int], keysPressed: str) -> str:
        big = releaseTimes[0]
        res = keysPressed[0]
        for i in range(1, len(releaseTimes)):
            if releaseTimes[i] - releaseTimes[i - 1] > big:
                res = keysPressed[i]
                big = releaseTimes[i] - releaseTimes[i - 1]
            elif releaseTimes[i] - releaseTimes[i - 1] == big:
                res = max(res, keysPressed[i])
        return res
