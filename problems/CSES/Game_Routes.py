
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
MOD = 10**9 + 7
N, M = map(int, input().split())
es = []
g = [[] for _ in range(N)]
for _ in range(M):
    a, b = map(int, input().split())
    g[a-1].append(b-1)

cache = [-1] * N
@bootstrap
def dp(node):
    if node == N - 1:
        yield 1
        return
    if cache[node] != -1:
        yield cache[node]
        return
    res = 0
    for adj in g[node]:
        res += (yield dp(adj))
    res %= MOD
    cache[node] = res
    yield res

print(dp(0))
