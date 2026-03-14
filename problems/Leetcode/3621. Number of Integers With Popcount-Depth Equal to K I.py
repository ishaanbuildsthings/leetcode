class Solution:
    def popcountDepth(self, n: int, k: int) -> int:
        if k == 0:
            return 1
            
        @cache
        def depth(number):
            if number == 1:
                return 0
            return 1 + depth(number.bit_count())

        strNum = str(bin(n)[2:])

        @cache
        def dp(i, isTight, sb):
            if i == len(strNum):
                # if we only have 1 set bit, our answer is 1, except for edge case if number=1 then its 0 which we dedupe later
                if sb == 1:
                    return 1 if 1 == k else 0
                # if we have no set bits I guess there is no answer
                if sb == 0:
                    return 0
                dep = 1 + depth(sb)
                return 1 if dep == k else 0
            v = strNum[i]
            res = 0
            upper = 1 if not isTight else int(v)
            for d in range(upper + 1):
                newT = isTight and upper == d
                newSb = sb + d
                res += dp(i + 1, newT, newSb)
            return res

        ans = dp(0, True, 0)
        if k == 1:
            ans -= 1

        return ans
                