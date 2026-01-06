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

n = int(input())
bosses = list(map(lambda x: int(x) - 1, input().split()))
print(f'{bosses=}')
g = [[] for _ in range(n)]
for node in range(n):
    boss = bosses[node]
    node += 1
    print(f'node={node} boss={boss}')
    g[node].append(boss)
    g[boss].append(node)

print(f'g now: {g}')
sz = [1] * n

@bootstrap
def dfs(node, p):
    if len(g[node]) == 1:
        yield None
        return
    szHere = 1
    for adj in g[node]:
        if adj == p:
            continue
        dfs(adj, node)
        szHere += sz[adj]
    sz[node] = szHere
    yield None

dfs(0, -1)

print(*[x - 1 for x in sz])