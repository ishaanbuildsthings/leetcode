class Solution:
    def minRotations(self, n: int, s: str) -> int:
        def step(a, b):
            diff1 = abs(a - b)
            diff2 = 10 - diff1
            return min(diff1, diff2)
 
        pf = []
        curr = 0 # number of steps
        for i, v in enumerate(s):
            prev = 0 if i == 0 else int(s[i - 1])
            current = int(s[i])
            dist = step(prev, current)
            curr += dist
            pf.append(curr)

        res = pf[-1] # if no reversal

        suff = [None] * len(s)
        # suff[i] is the # of steps to solve n-1...i with no prior step, we start at this point

        curr = 0
        for i in range(n - 1, -1, -1):
            current = int(s[i])
            
            if i != n - 1:
                nxt = int(s[i + 1])
                distance = step(current, nxt)
                curr += distance

            suff[i] = curr

        # print(suff)

        reverseAll = suff[0]
        reverseAll += step(0, int(s[-1]))

        res = min(res, reverseAll)

        for i in range(n - 1):
            # normal 0...i, reverse the suffix
            normalSteps = pf[i]
            suffSteps = suff[i + 1]
            lst = int(s[i])
            chain = int(s[-1])
            total = normalSteps + suffSteps + step(lst, chain)
            res = min(res, total)

        return res