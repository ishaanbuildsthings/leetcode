class Solution:
    def closestFair(self, n: int) -> int:
        s = str(n)

        
        odds = 0
        for v in s:
            if int(v) % 2:
                odds += 1
        evens = len(s) - odds
        print(odds)
        print(evens)
        if odds == evens:
            return n

        for i in range(len(s) - 1, -1, -1):
            v = int(s[i])
            evensBefore = 0
            oddsBefore = 0
            for j in range(i):
                if int(s[j]) % 2:
                    oddsBefore += 1
                else:
                    evensBefore += 1
            for d in range(v + 1, 10):
                evenSurplus = evensBefore - oddsBefore
                if d % 2 == 0:
                    evenSurplus += 1
                else:
                    evenSurplus -= 1
                
                suffSize = len(s) - i - 1
                # E + O = suffSize
                # E - O = eSurplus
                # E = eSurplus + O
                # 2 * O + eSurplus = suffSize
                # O = (suffSize - eSurplus) / 2
                O = (suffSize - evenSurplus)
                if O % 2:
                    continue
                O //= 2
                E = suffSize - O
                if min(O, E) < 0:
                    continue
                E, O = O, E # actually for suffix
                prefix = s[:i] + str(d) + ('0' * E) + ('1' * O)
                return int(prefix)


        sz = len(s) + 1
        if sz % 2:
            sz += 1
        answer = '1' + ('0' * (sz // 2)) + ('1' * ((sz // 2) - 1))
        return int(answer)

                

        
# # digit dp
# class Solution:
#     def closestFair(self, n: int) -> int:
        
#         s = str(n)

#         choice = {}
#         nextState = {}

#         @cache
#         def dp(i, evenSurplus, ltight):
#             if i == len(s):
#                 return True if evenSurplus == 0 else False
#             v = int(s[i]) if ltight else 0
#             for d in range(v, 10):
#                 nltight = ltight and d == v
#                 isEven = d % 2 == 0
#                 nEven = evenSurplus + (1 if isEven else -1)
#                 result = dp(i + 1, nEven, nltight)
#                 if result:
#                     choice[i, evenSurplus, ltight] = d
#                     nextState[i, evenSurplus, ltight] = i + 1, nEven, nltight
#                     return True
#             return False
        
#         dp(0, 0, True)
        
#         res = []
#         i = 0
#         evenSurplus = 0
#         ltight = True

#         while (i, evenSurplus, ltight) in nextState:
#             res.append(choice[i, evenSurplus, ltight])
#             i, evenSurplus, ltight = nextState[i, evenSurplus, ltight]
        
#         if res:
#             return int(''.join(map(str, res)))
        
#         if not res:
#             sz = len(s) + 1
#             if sz % 2:
#                 sz += 1
#             answer = '1' + ('0' * (sz // 2)) + ('1' * ((sz // 2) - 1))
#             return int(answer)