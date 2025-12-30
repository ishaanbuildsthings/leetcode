if True:
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

MOD = 998244353
T = int(input())
for _ in range(T):
    N = int(input())
    # print('=============')
    # print(f'{N=}')
    parents = list(map(int,input().split()))
    parents = [-1] + [v-1 for v in parents]
    # print(f'{parents=}')

    children = [[] for _ in range(N)]
    for node in range(N):
        par = parents[node]
        if par != -1:
            children[par].append(node)

    # print(f'{children=}')

    nodesAtLayer = [[] for _ in range(N)]

    @bootstrap
    def dfs(node, layer):
        nodesAtLayer[layer].append(node)
        for c in children[node]:
            yield dfs(c, layer + 1)
        yield None
    dfs(0, 0)
    mxDepth = 0
    for i in range(len(nodesAtLayer)):
        if nodesAtLayer[i]:
            mxDepth = i

    cacheNode = [-1] * N
    @bootstrap
    def dpNode(node, depth):
        if depth == mxDepth:
            yield 1
            return
        if cacheNode[node] != -1:
            yield cacheNode[node]
            return
        if node == 0:
            res = 1 # end here
            for c in children[node]:
                res += (yield dpNode(c, depth + 1))
            yield res % MOD
            return

        belowLayer = (yield dpLayer(depth + 1))
        for c in children[node]:
            belowLayer -= (yield dpNode(c, depth + 1))
        belowLayer += 1 # sequence can end at this node
        belowLayer %= MOD
        cacheNode[node] = belowLayer
        yield belowLayer
    
    cacheLayer = [-1] * N
    @bootstrap
    def dpLayer(layer):
        if cacheLayer[layer] != -1:
            yield cacheLayer[layer]
            return
        res = 0
        for node in nodesAtLayer[layer]:
            res += (yield dpNode(node, layer))
        res %= MOD
        cacheLayer[layer] = res
        yield res
    
    print(dpNode(0, 0))


    

        
    
        



    