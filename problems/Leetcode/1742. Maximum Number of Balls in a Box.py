class Solution:
    def countBalls(self, lowLimit: int, highLimit: int) -> int:
        # biggest box is 9+9+9+9+9 = 45
        # can check how many are in each box with digitDp
        # dp state (i, isTight, currSum, targetSum) logN * 2 * 45 * 45, * 10 for recurrence relation, this is 120*45*45 = 243000 lol
        c = Counter()
        for num in range(lowLimit, highLimit + 1):
            tot = sum(int(x) for x in str(num))
            c[tot] += 1
        return max(c.values())