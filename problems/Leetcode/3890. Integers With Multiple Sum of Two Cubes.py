class Solution:
    def findGoodIntegers(self, n: int) -> list[int]:
        up = int(n ** (1/3)) + 50
        counts = Counter()
        for num1 in range(1, up):
            for num2 in range(num1, up):
                v = (num1**3) + (num2**3)
                if v <= n:
                    counts[v] += 1

        ans = []
        for k in counts:
            if counts[k] >= 2:
                ans.append(k)
        return sorted(ans)

        
        