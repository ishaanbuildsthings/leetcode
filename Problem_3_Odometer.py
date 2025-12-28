import functools

readFile = True

if readFile:
    with open('odometer.in', 'r') as f:
        L, R = map(int, f.readline().split())
else:
    L, R = map(int, input().split())

strL = str(L)
strR = str(R)
diff = len(strR) - len(strL)
strL = '0' * diff + strL
n = len(strR)

res = 0

# count valid results, but will double count ties, for instance 2244 would add 1 when isAtLeastHalfNumber is 2 and isAtLeastHalfNumber is 4
# need to think about this a bit more, not sure if it double counts ties or exponentially double counts ties
for isAtLeastHalfNumber in range(10):
    @functools.lru_cache(maxsize=None)
    def dp1(i, th, tl, seqLength, digitCount):
        # base case
        if i == n:
            if digitCount >= seqLength / 2:
                return 1
            return 0

        ub = 9 if not th else int(strR[i])
        lb = 0 if not tl else int(strL[i])
        resHere = 0
        for d in range(lb, ub + 1):
            nth = int(th and d == ub)
            ntl = int(tl and d == lb)
            newSeqLength = seqLength + 1 if seqLength else 1 if d else 0
            newDigitCount = digitCount + ((d == isAtLeastHalfNumber) if newSeqLength else 0)
            resHere += dp1(i + 1, nth, ntl, newSeqLength, newDigitCount)
        return resHere
    res += dp1(0, 1, 1, 0, 0)

# print(f'res: {res}')

# count ties
for tie1 in range(10):
    # need to start at tie1 + 1 otherwise we would double count ties again
    for tie2 in range(tie1 + 1, 10):
        @functools.lru_cache(maxsize=None)
        def dp2(i, th, tl, seqLength, digitCount, digitCount2):
            # base case
            if i == n:
                return 1 if digitCount == digitCount2 == seqLength / 2 else 0

            ub = 9 if not th else int(strR[i])
            lb = 0 if not tl else int(strL[i])
            resHere = 0
            for d in range(lb, ub + 1):
                nth = int(th and d == ub)
                ntl = int(tl and d == lb)
                newSeqLength = seqLength + 1 if seqLength else 1 if d else 0
                newDigitCount = digitCount + ((d == tie1) if newSeqLength else 0)
                newDigitCount2 = digitCount2 + ((d == tie2) if newSeqLength else 0)
                resHere += dp2(i + 1, nth, ntl, newSeqLength, newDigitCount, newDigitCount2)
            return resHere
        res -= dp2(0, 1, 1, 0, 0, 0)

if readFile:
    with open('odometer.out', 'w') as f:
        f.write(str(res) + '\n')
else:
    print(res)

    


# Bug, strict majority gets counted once for each antiTieType, so 11115 would add 9 to result for antiTieType 0 2 3 4 ... 9
# @functools.lru_cache(maxsize=None)
# def dp(i, tightHigh, tightLow, digitType, antiTieType, digitCount, antiTieCount, seqLength):
#     if i == n:
#         isMajority = digitCount > (seqLength / 2)
#         if isMajority:
#             return 1
#         # We cannot double count ties
#         if digitCount == (seqLength / 2) and antiTieCount == (seqLength / 2):
#             return 1 if digitType < antiTieType else 0 # hashing system
#         return 0

#     ub = 9 if not tightHigh else int(strR[i])
#     lb = 0 if not tightLow else int(strL[i])
#     resHere = 0
#     for d in range(lb, ub + 1):
#         nth = int(tightHigh and d == ub)
#         ntl = int(tightLow and d == lb)
#         newSeqLength = seqLength + 1 if seqLength else 1 if d != 0 else 0
#         if newSeqLength:
#             newCount = digitCount + (d == digitType)
#             newAntiTieCount = antiTieCount + (d == antiTieType)
#         else:
#             newCount = digitCount
#             newAntiTieCount = antiTieCount
#         resHere += dp(i + 1, nth, ntl, digitType, antiTieType, newCount, newAntiTieCount, newSeqLength)
#     return resHere

# result = 0
# for digitType in range(10):
#     for antiTieType in range(10):
#         if antiTieType == digitType:
#             continue
#         result += dp(0, 1, 1, digitType, antiTieType, 0, 0, 0)

# if readFile:
#     with open('odometer.out', 'w') as f:
#         f.write(str(result) + '\n')
# else:
#     print(result)

