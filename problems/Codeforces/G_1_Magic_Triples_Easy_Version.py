def nc3(n):
    return n * (n - 1) * (n - 2) // 6
import collections
BIG = 1000000

# proper divisors
# divs = [[] for _ in range(BIG + 1)]
# for number in range(2, BIG + 1):
#     for mult in range(2 * number, BIG + 1, number):
#         divs[mult].append(number)

spf = [0] * (BIG + 1) # spf[1] = 0, spf[prime] = prime
for number in range(2, BIG + 1):
    if spf[number]: continue
    spf[number] = number
    for mult in range(number * number, BIG + 1, number):
        if spf[mult] == 0: spf[mult] = number

def fastFactorize(number):
    facs = [1]
    curr = number
    while curr > 1:
        p = spf[curr]
        length = len(facs)
        currToPow = 1
        while curr % p == 0:
            currToPow *= p
            curr //= p
            for j in range(length):
                facs.append(facs[j] * currToPow)
    return sorted(facs)


def solve():
    n = int(input())
    A = list(map(int, input().split()))
    # print('=========')
    
    mx = max(A)
    frq = collections.Counter([str(x) for x in A])

    res = 0
    for k, v in frq.items():
        triples = nc3(int(v))
        orders = 6 * triples
        res += orders
    
    prevAdded = 0
    A.sort()
    # print(f'{A=}')
    frqLeft = collections.Counter()
    for i, v in enumerate(A):
        if i and A[i] == A[i - 1]:
            res += prevAdded
            frqLeft[str(v)] += 1
            continue
        prevAdded = 0
        for div in fastFactorize(v):
            if div == 1:
                continue
            # print(f'v is: {v} div is: {div}')
        # print(f'{v=}')
        # for div in divs[v]:
            # print(f'{div=}')
            leftOpts = frqLeft[str(v // div)]
            # print(f'left opts: {leftOpts}')
            reqRight = div * v
            # print(f'req right: {reqRight}')
            if reqRight > mx:
                break
            frqRight = frq[str(reqRight)] - frqLeft[str(reqRight)]
            # print(f'frq right: {frqRight}')
            res += leftOpts * frqRight
            prevAdded += leftOpts * frqRight
        # print(f'prev added now: {prevAdded}')
        frqLeft[str(v)] += 1
    
    print(res)



t = int(input())
for _ in range(t):
    solve()