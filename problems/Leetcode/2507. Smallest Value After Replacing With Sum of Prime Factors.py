spf = [0] * (10**5 + 1)
factors = [[] for _ in range(10**5 + 1)]

for i in range(2, 10**5 + 1):
    if spf[i] == 0:
        for j in range(i, 10**5 + 1, i):
            if spf[j] == 0:
                spf[j] = i
class Solution:
    def smallestValue(self, n: int) -> int:
        minN = n
        seen = {n}
        curr = n
        while True:
            tot = 0
            while curr > 1:
                tot += spf[curr]
                curr //= spf[curr]
            minN = min(minN, tot)
            curr = tot
            if curr in seen:
                break
            seen.add(curr)
        return minN

        