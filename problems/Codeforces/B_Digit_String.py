from functools import cache
from math import inf

from types import GeneratorType

def bootstrap(f, stack=[]):
    def wrappedfunc(*args, **kwargs):
        if stack:
            return f(*args, **kwargs)
        else:
            to = f(*args, **kwargs)
            while True:
                if type(to) is GeneratorType:
                    stack.append(to)
                    to = next(to)
                else:
                    stack.pop()
                    if not stack:
                        break
                    to = stack[-1].send(to)
            return to
    return wrappedfunc


def solve():
    s = input()
    arr = []
    for v in s:
        arr.append(int(v))
    arr = [x for x in arr if x != 4]
    ops = len(s) - len(arr)
    # print(f'{arr=}')
    # print(f'{ops=}')

    if 2 not in arr:
        print(ops)
        return


    # 22 is fine
    # 32 is bad
    # 12 is bad

    # # remove non2 digits before a 2
    # newOps = 0
    # seen2 = False
    # for j in range(len(arr) -1, -1, -1):
    #     if arr[j] == 2:
    #         seen2 = True
    #     if seen2 and arr[j] != 2:
    #         newOps += 1
    
    # removeNonTwos = ops + newOps

    # # remove 2s that come after a non2
    # non2Seen = False
    # twos = 0
    # for j in range(len(arr)):
    #     if arr[j] != 2:
    #         non2Seen = True
    #     if non2Seen and arr[j] == 2:
    #         twos += 1
    
    # option2 = ops + twos

    # # 1 2 1 3 2 2 1 3

    # ans = min(removeNonTwos, option2)

    cache = [[-1] * 2 for _ in range(len(arr))] # arr[i][hasNum]

    @bootstrap
    def dp(i, hasNum):
        if i == len(arr):
            yield 0
            return
        if cache[i][hasNum] != -1:
            yield cache[i][hasNum]
            return
        v = arr[i]
        res = inf
        if not hasNum:
            if v != 2:
                allowNum = (yield dp(i + 1, 1))
                skip = 1 + (yield dp(i + 1, 0))
                res = min(allowNum, skip)
            else:
                # if we have some prefix too we can just keep it
                res = yield dp(i + 1, 0)
        else:
            if v == 2:
                forcedSkip = 1 + (yield dp(i + 1, 1))
                res = forcedSkip
            else:
                freeTake = yield dp(i + 1, 1)
                res = freeTake
        cache[i][hasNum] = res
        yield res
        return
    
    answer = dp(0, 0)
        
    print(answer + ops)

t = int(input())
for _ in range(t):
    solve()