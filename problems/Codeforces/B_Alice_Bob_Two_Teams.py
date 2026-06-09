n = int(input())
A = list(map(int, input().split()))
s = input()

curr = 0
pf = []
for v in A:
    curr += v
    pf.append(curr)

def query(l, r):
    if l > r:
        return 0
    if l >= n:
        return 0
    return pf[r] - (pf[l - 1] if l else 0)

bob = sum(A[i] if s[i] == 'B' else 0 for i in range(n))

aliceScore = 0
pfAlice = []
for i in range(n):
    if s[i] == 'A':
        aliceScore += A[i]
    pfAlice.append(aliceScore)

def queryAlice(l, r):
    if l > r:
        return 0
    if l >= n:
        return 0
    return pfAlice[r] - (pfAlice[l - 1] if l else 0)

def queryBob(l, r):
    if l > r:
        return 0
    if l >= n:
        return 0
    tot = query(l, r)
    return tot - queryAlice(l, r)

for i in range(n):
    bobScoreSuff = queryBob(i + 1, n - 1)
    bobScorePref = queryAlice(0, i)
    bob = max(bob, bobScorePref + bobScoreSuff)
    # print(f'bob now: {bob}')

for i in range(n - 1, -1, -1):
    # print(f'{i=}')
    bobScorePref = queryBob(0, i - 1)
    bobScoreSuff = queryAlice(i, n - 1)
    # print(f'{bobScorePref=} {bobScoreSuff=}')
    bob = max(bob, bobScorePref + bobScoreSuff)
    # print(f'bob suff now: {bob}')

print(bob)

