class Solution:
    def fixedRatio(self, s: str, num1: int, num2: int) -> int:
        # 0s are going to gain num2
        # 1s will minus num1

        pf = defaultdict(int)
        pf[0] = 1
        res = 0
        curr = 0
        for r, v in enumerate(s):
            if v == '0':
                curr += num2
            else:
                curr -= num1
            res += pf[curr]
            pf[curr] += 1
        return res