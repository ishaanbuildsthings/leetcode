from functools import cache
import math
def solve():
    a, n = list(map(int, input().split()))
    opts = list(map(int, input().split()))
    opts.sort()

    # print('===========')
    # print(f'{a=}')

    # find largest number <= a

    choice = {} # maps (i, tight) -> next digit
    nxt = {} # maps (i, tight) -> (nextI, nextTight)

    # tells us if this is doable
    @cache
    def dp(i, tight, strNum):
        if i == len(strNum):
            return True
        v = int(strNum[i])
        res = False
        for d in opts:
            if tight and d > v:
                continue
            ntight = tight and d == v
            nextDp = dp(i + 1, ntight, strNum)
            if nextDp:
                choice[(i, tight)] = d
                nxt[(i, tight)] = (i + 1, ntight)
                res = True
        return res
    
    dp(0, True, str(a))
    # print(choice)

    ans = math.inf

    # construct option 1
    if dp(0, True, str(a)):
        i = 0
        tight = True
        res = []
        while (i, tight) in choice:
            nxtI, ntight = nxt[(i, tight)]
            num = choice[(i, tight)]
            res.append(str(num))
            i = nxtI
            tight = ntight
        # print(f'{res=}')
        number = int(''.join(res))
        ans = abs(number - a)
    
    # print(f'init ans: {ans}')


    # ===============================================================
    # FIND SMALLEST >= a
    opts.sort(reverse=True)

    choice = {} # maps (i, tight) -> next digit
    nxt = {} # maps (i, tight) -> (nextI, nextTight)

    # tells us if this is doable
    @cache
    def dp2(i, tight, strNum):
        if i == len(strNum):
            return True
        v = int(strNum[i])
        res = False
        for d in opts:
            if tight and d < v:
                continue
            ntight = tight and d == v
            nextDp = dp2(i + 1, ntight, strNum)
            if nextDp:
                choice[(i, tight)] = d
                nxt[(i, tight)] = (i + 1, ntight)
                res = True
        return res
    
    dp2(0, True, str(a))
    # print(choice)


    # construct option 1
    if dp2(0, True, str(a)):
        i = 0
        tight = True
        res = []
        while (i, tight) in choice:
            nxtI, ntight = nxt[(i, tight)]
            num = choice[(i, tight)]
            res.append(str(num))
            i = nxtI
            tight = ntight
        # print(f'{res=}')
        number = int(''.join(res))
        ans = min(ans, abs(number - a))
    
    # print(f'final ans: {ans}')

    # now take the biggest number in shorter length
    mx = max(opts)
    if len(str(a)) > 1:
        newL = len(str(a)) - 1
        big = str(mx) * newL
        big = int(big)
        diff = abs(big - a)
        ans = min(ans, diff)

    # smallest with bigger length
    optsNoZero = [x for x in opts if x != 0]
    if optsNoZero:
        newL = len(str(a)) + 1
        begin = min(optsNoZero)
        remain = min(opts)
        smallNum = int(str(begin) + str(remain) * (newL - 1))
        diff = abs(smallNum - a)
        ans = min(ans, diff)

    print(ans)

        




t = int(input())
for _ in range(t):
    solve()