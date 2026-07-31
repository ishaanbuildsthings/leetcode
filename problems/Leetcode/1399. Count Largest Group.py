class Solution:
    def countLargestGroup(self, n: int) -> int:
        totToCount = defaultdict(int)
        for num in range(1, n + 1):
            tot = sum(int(c) for c in str(num))
            totToCount[tot] += 1
        maxSize = max(totToCount.values())
        return sum(
            totToCount[key] == maxSize for key in totToCount
        )