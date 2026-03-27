class Solution:
    def canWin(self, currentState: str) -> bool:
        
        streaks = []
        curr = 0
        for v in currentState:
            if v == '-':
                if curr:
                    streaks.append(curr)
                curr = 0
            else:
                curr += 1
        if curr:
            streaks.append(curr)
        
        streaks.sort()

        # tuple of streaks
        @cache
        def dp(t):
            t = list(t)
            if len(t) == 0:
                return False
            for i in range(len(t)):
                streak = t[i]
                for leftSize in range(streak - 1):
                    rightSize = streak - leftSize - 2
                    nt = t[:i] + t[i+1:]
                    if leftSize:
                        nt.append(leftSize)
                    if rightSize:
                        nt.append(rightSize)
                    nt.sort()
                    if not dp(tuple(nt)):
                        return True
            return False
        
        return dp(tuple(streaks))

                


