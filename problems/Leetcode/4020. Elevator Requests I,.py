class Solution:
    def elevatorRequests(self, n: int, requests: list[int]) -> int:
        res = 0
        for i, v in enumerate(requests):
            res += abs(v - (0 if not i else requests[i - 1]))
        return res