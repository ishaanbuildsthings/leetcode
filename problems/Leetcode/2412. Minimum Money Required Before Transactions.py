from functools import cmp_to_key
class Solution:
    def minimumMoney(self, transactions: List[List[int]]) -> int:
        def cmp(t1, t2):
            oneFirst = max(t1[0], t2[0] + (t1[0] - t1[1]))
            twoFirst = max(t2[0], t1[0] + (t2[0] - t2[1]))
            if oneFirst < twoFirst:
                return 1
            elif oneFirst > twoFirst:
                return -1
            # if there is a tie in starting money, whatever leaves less money after the first one is bad (so we put it first)
            if (t1[0] - t1[1]) > (t2[0] - t2[1]):
                return -1
            return 1
        # 5,0  4,2   2,1 -> 9
        # 5,0  2,1   4,2 -> 10
        
        transactions.sort(key=cmp_to_key(cmp))

        def canDo(startMoney):
            curr = startMoney
            for cost, cashback in transactions:
                if curr < cost:
                    return False
                curr -= cost
                curr += cashback
            return True

        l = 0
        r = 10**18
        res = inf
        while l <= r:
            m = (r + l) // 2
            if canDo(m):
                res = m
                r = m - 1
            else:
                l = m + 1
        
        return res
        