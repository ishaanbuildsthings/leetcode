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

from collections import defaultdict
import functools

MOD = 998244353

T = int(input())
for _ in range(T):
    n, m = map(int, input().split())
    arr = list(map(int, input().split()))

    nodemaps = [defaultdict(list) for _ in range(n)]
    for _ in range(m):
        a, b = map(int, input().split())
        a -= 1
        b -= 1
        nodemaps[a][arr[b]].append(b)

    cache = [dict() for _ in range(n)]
    
    @bootstrap
    def dp(node, needVal):
        if needVal not in nodemaps[node]:
            yield 0
            return
        if needVal in cache[node]:
            yield cache[node][needVal]
            return
        
        nextNeed = arr[node] + needVal
        res = 0
        for nxt in nodemaps[node][needVal]:
            res += 1 + (yield dp(nxt, nextNeed))
            res %= MOD
        cache[node][needVal] = res
        yield res

    ans = 0
    for node in range(n):
        for needVal in nodemaps[node]:
            ans += dp(node, needVal)
            ans %= MOD

    print(ans)
