# # _(_)_(_)

# # (()) (())

# _)_)_)_)

# ()()()()
def solve():
    n = int(input())
    s = input()
    # print('-------')
    # print(f'{s=}')

    safe = [False] * n
    closeSurplus = 0
    for i in range(n - 1, -1, -1):
        if s[i] == ')':
            closeSurplus += 1
        else:
            closeSurplus -= 1
        if closeSurplus <= 0:
            safe[i] = True
    
    # print(f'{safe=}')


    # we want to close as long as it is safe to close, e.g. future closes can never exceed opens, and we can put a ) here
    res = list(s)
    openSurplus = 0
    for i in range(n):
        if s[i] == '(':
            openSurplus += 1
            continue
        if s[i] == ')':
            openSurplus -= 1
            continue
        # no opens, we must open here
        if openSurplus == 0:
            res[i] = '('
            openSurplus += 1
            continue
        
        # we can close here, based on the prefix
        # but can we on the suffix?
        if i < n - 1 or safe[i+1]:
            res[i] = ')'
            openSurplus -= 1
        elif i == n - 1:
            res[i] = ')'
            openSurplus -= 1
        else:
            res[i] = '('
            openSurplus += 1
    
    string = ''.join(res)

    def score(result):
        scoreHere = 0
        stack = [0] # holds indices
        for i in range(1, len(result)):
            v = result[i]
            if v == '(':
                stack.append(i)
                continue
            poppedI = stack.pop()
            diff = i - poppedI
            scoreHere += diff
        return scoreHere
    
    print(score(string))



            

t = int(input())
for _ in range(t):
    solve()