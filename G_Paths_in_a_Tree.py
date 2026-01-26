
import sys
def ask(a, b):
    print(f'? {a+1} {b+1}')
    sys.stdout.flush()

# 0 is bad, 1 is good
def receive():
    answer = int(input())
    if answer == -1:
        exit()
    return answer

def finish(v):
    print(f'! {v+1}')
    sys.stdout.flush()

# CODEFORCES THIS BOOTSTRAP TEMPLATE IVE USED EVERYWHERE YOU CAN SEE MY SUBMISSIONS!!! - leetgoat
from types import GeneratorType
def bootstrap(f):
    stack = []
    def wrappedfunc(*args, **kwargs):
        if stack:
            return f(*args, **kwargs)
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
    n = int(input())
    g = [[] for _ in range(n)]
    edges = []
    for _ in range(n - 1):
        a, b = map(int, input().split())
        a -= 1
        b -= 1
        g[a].append(b)
        g[b].append(a)

    if n == 3:
        ask(0, 0)
        if receive():
            finish(0)
            return
        else:
            ask(1, 1)
            if receive():
                finish(1)
                return
            else:
                finish(2)
                return
    
    
    children = [[] for _ in range(n)]

    @bootstrap
    def dfs(node, parent):
        for adjN in g[node]:
            if adjN == parent:
                continue
            children[node].append(adjN)
            yield dfs(adjN, node)
        yield 0
    dfs(0, -1)
    
    # print(f'children:')
    # print(children)

    postorder = []

    @bootstrap
    def dfs2(node):
        if not children[node]:
            postorder.append(node)
            yield 0
            return
        for child in children[node]:
            yield dfs2(child)
        postorder.append(node)
        yield 0
    dfs2(0)

    processed = [False] * n

    # print(f'{postorder=}')

    for node in postorder:
        if node == 0:
            lc = [c for c in children[0] if not processed[c]]
            if len(lc) <= 2:
                if len(lc) == 0:
                    return finish(0)
                else:
                    if len(lc) == 1:
                        ask(lc[0], lc[0])
                        if receive() == 1:
                            return finish(lc[0])
                        else:
                            return finish(0)
                    else:
                        ask(0, 0)
                        if receive():
                            return finish(0)
                        else:
                            ask(lc[0], lc[0])
                            if receive():
                                return finish(lc[0])
                            else:
                                return finish(lc[1])

        # print(f'trying node: {node} now')
        lc = [c for c in children[node] if not processed[c]]
        if len(lc) == 0:
            # print(f'no lc for this node, continuing')
            continue

        # if we have even children
        # pair first 2 children, if hit we do two singleton checks
        if len(lc) % 2 == 0:
            first = lc[0]
            second = lc[1]
            ask(first, second)
            if receive() == 1:
                ask(first, first)
                if receive() == 1:
                    finish(first)
                    return
                ask(second, second)
                if receive() == 1:
                    finish(second)
                    return
                else:
                    finish(node)
                    return
            # we missed two children, iterate as normal
            for i in range(2, len(lc), 2):
                left = lc[i]
                right = lc[i + 1]
                ask(left, right)
                if receive() == 0:
                    continue
                ask(left, left)
                if receive() == 1:
                    finish(left)
                    return
                else:
                    finish(right)
                    return

        # if we have odd children, pair one with root, then pair adjacents
        else:
            first = lc[0]
            # root <> first child
            ask(first, node)
            if receive() == 1:
                ask(first, first)
                if receive() == 1:
                    finish(first)
                    return
                finish(node)
                return
            
            for i in range(1, len(lc), 2):
                left = lc[i]
                right = lc[i + 1]
                ask(left, right)
                if receive() == 0:
                    continue
                # found the pair
                ask(left, left)
                if receive() == 0:
                    finish(right)
                    return
                else:
                    finish(left)
                    return
                
            
        
        processed[node] = True
    

    lc = [c for c in children[0] if not processed[c]]
    if len(lc) == 0:
        return finish(0)
    else:
        if len(lc) == 1:
            ask(lc[0], lc[0])
            if receive() == 1:
                return finish(lc[0])
            else:
                return finish(0)
        else:
            ask(0, 0)
            if receive():
                return finish(0)
            else:
                ask(lc[0], lc[0])
                if receive():
                    return finish(lc[0])
                else:
                    return finish(lc[1])
    return

t = int(input())
for _ in range(t):
    # print(f'number of tests is: {t}')
    solve()