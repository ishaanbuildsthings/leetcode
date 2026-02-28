

# SMALLEST > A, not shared with B
def f2(a, b):
    x = a + 1
    while x & b:
        bad = x & b
        bit = bad & -bad
        x = (x + bit) & ~(bit - 1)
    return x

def score(x, y, xAns, yAns):
    if xAns is None or yAns is None:
        return float('inf')
    a1 = sorted([x, y])
    a2 = sorted([xAns, yAns])
    # print(f'scoring: {x=} {y=} {xAns=} {yAns=}')
    vv = abs(a1[0] - a2[0]) + abs(a1[1] - a2[1])
    # print(vv)
    return vv

# largest < x no shared bit with y
def prevNoShare(x, y):
    if x == 0:
        return None
    ub = x - 1

    limit = max(ub, y).bit_length()
    c = 0
    smaller = False

    for bit in range(limit - 1, -1, -1):
        ubBit = (ub >> bit) & 1
        yBit = (y >> bit) & 1

        if smaller:
            if yBit == 0:
                c |= 1 << bit
            continue

        if yBit == 1:
            if ubBit == 1:
                smaller = True
            continue

        if ubBit == 1:
            c |= 1 << bit

    return c

def idea3(x, y):
    if x > y:
        x, y = y, x
    if x & y == 0:
        return (x, y)
    # next biggest > X no shared bit with y
    opt1 = (f2(x, y), y)
    # next biggest > Y no shared bit with x
    opt2 = (x, f2(y, x))

    opt3 = (prevNoShare(x, y), y)

    opt4 = (x, prevNoShare(y, x))

    scores = [
        score(x, y, opt1[0], opt1[1]), 
        score(x, y, opt2[0], opt2[1]), 
        score(x, y, opt3[0], opt3[1]), 
        score(x, y, opt4[0], opt4[1]), 
    ]

    idx = scores.index(min(scores))
    if idx == 0:
        return opt1
    if idx == 1:
        return opt2
    if idx == 2:
        return opt3
    return opt4


# 38 -> 25
def invMask(x):
    if x == 0:
        return 0
    mask = (1 << x.bit_length()) - 1
    return mask ^ x

MX = 555
import random
def brute(x, y):
    smallest = float('inf')
    res = []
    for number1 in range(2 * MX + 1):
        for number2 in range(2 * MX + 1):
            if number1 & number2:
                continue
            v = abs(x - number1) + abs(y - number2)
            if v == smallest:
                res.append((number1, number2))
            elif v < smallest:
                res = [(number1, number2)]
                smallest = v
    return sorted(res)

def verify(tup, x, y):
    solutions = brute(x, y)
    # print(f'{solutions=}')
    # print(f'{solutions=}')
    return tup in solutions

# exclusive
def nextPow2E(x):
    return 1 << x.bit_length()

# gets 1<<shift
def msb(x):
    return 1 << (x.bit_length() - 1) if x > 0 else 0

#inclusive
def nextPow2(x):
    if x <= 1:
        return 1
    return 1 << ((x - 1).bit_length())

def isPow2(x):
    return x > 0 and (x & (x - 1)) == 0



def idea2(x, y):
    if not x & y:
        return (x, y)
    if x == y:
        if isPow2(x):
            return (x - 1, x)
        else:
            opt1 = (x, invMask(x))
            aScore = score(x, x, x, invMask(x))
            bScore = score(x, x, x, nextPow2E(x))
            if aScore <= bScore:
                return (x, invMask(x))
            else:
                return (x, nextPow2E(x))
    # set as many bits in Y as possible if not set in X
    res = 0
    # take all bits staying <= y
    for bit in range(64, -1, -1):
        # if 1 << bit == 256:
            # print(f'offset is: {1 << bit}')
        if (1 << bit) > y:
            continue
        if (1 << bit) & x:
            continue
        # print(f'can we take {1 << bit} ?')
        if (res | (1 << bit)) <= y:
            # print(f'yes')
            res |= (1 << bit)
        # else:
        #     print('no')
        
        # print(f'curr res: {res}')
    
    # take first > y
    # print(f'biggest <=y : {res}')

                
        # res |= (1 << bit)
    # if res > y:
    #     res = y
    s1 = score(x, y, x, res)
    # print(f'score 1: {s1}')
    nxtPow = nextPow2(y)
    # print(f'nxt pow is: {nxtPow}')
    # print(f'nxt pow is: {nxtPow}')
    # print(f'assessing solution: {x} {nxtPow}')
    s2 = score(x, y, x, nxtPow)
    # print(f'score 2 is: {s2}')
    result = None
    if (s1 <= s2):
        result = (x, res)
        # print(f'score 1 is lower, so result is: {result}')
    else:
        # print(f'score 2 is lower')
        result = (x, nxtPow)
    
    # print(f'current result: {result}')


    # set lower number to next exclusive power
    currScore = min(s1, s2)
    s3 = score(x, y, nextPow2E(x), y)
    if nextPow2E(x) & y == 0:
        # print(f'that worked: {nextPow2E(x)} and {y}')
        # print(f'that score was: {s3}')
        if s3 <= min(s1, s2):
            result = sorted((nextPow2E(x), y))
            currScore = s3

    
    # print('======')
    m = msb(y)
    for bit in range(64):
        if (1 << bit) >= m:
            continue
        alternative = (1 << bit) | m
        if alternative & x:
            continue
        # print(alternative)
        # print(f'considering: {(x, alternative)}')
        scoreHere = score(x, y, x, alternative)
        # print(f'score here: {scoreHere}')
        # print(f'curr score: {currScore}')
        if scoreHere <= currScore:
            currScore = scoreHere
            result = (x, alternative)

    # set x a bit bigger
    c2 = f2(x, y)
    thisScore = score(x, y, c2, y)
    if thisScore < currScore:
        currScore = thisScore
        result = (min(c2, y), max(c2, y))
    
    # set y a bit bigger
    c3 = f2(y, x)
    vvScore = score(x, y, c3, x)
    if vvScore < currScore:
        currScore = vvScore
        result = (min(c3, x), max(c3, x))
        

    # print(f'idea 2 yields: {result}')
    return result

# for _ in range(20):
#     a = random.randint(0, MX)
#     b = random.randint(0, MX)
#     if a > b:
#         a, b = b, a

#     # a = 29
#     # b = 37
#     # a = 30
#     # b = 762
#     # print(f'generated {a=} {b=}')
#     answer = idea3(a, b)
#     # print(F'my answer: {answer}')
#     if not verify(tuple(answer), a, b):
#         print("ERRROR")
#         print(f'{a=} {b=}')



# SINGLE TEST
# a = 47
# b = 98
# print(f'generated {a=} {b=}')
# answer = idea2(a, b)
# print(f'my answer is: {answer}')
# print(verify(tuple(answer), a, b))
# solutions = brute(a, b)
# print(f'{solutions=}')    


def solve():
    x, y = map(int, input().split())
    # if x > y:
    #     x, y = y, x

    if x == y == 0:
        print(f'{0} {0}')
        return
    if x == 0 or y == 0:
        print(f'{x} {y}')
        return
    # print('========')
    # print(f'{x=} {y=}')
    # x = 16
    # y = 16
    result = idea3(x, y)
    s1 = abs(x - result[0]) + abs(y - result[1])
    s2 = abs(x - result[1]) + abs(y - result[0])
    if s1 <= s2:
        print(*result)
    else:
        print(*result[::-1])

    # print(verify(result, x, y))
    # print(*result)
t = int(input())
for _ in range(t):
    solve()