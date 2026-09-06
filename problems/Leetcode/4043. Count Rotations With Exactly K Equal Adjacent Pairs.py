class Solution:
    def countRotations(self, s: str, k: int) -> int:
        res = 0
        for rot in range(len(s)):
            print(s)

            score = 0
            for i in range(len(s) - 1):
                if s[i] == s[i+1]:
                    score += 1
            if score == k:
                res += 1
                


            s = s[1:] + s[0]

        return res