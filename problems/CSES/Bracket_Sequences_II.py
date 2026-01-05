MOD = 10**9 + 7
n = int(input())
pf = input()

if n % 2:
    print(0)
    exit()

opens = 0
closed = 0
surplusOpen = 0
for v in pf:
    if v == '(':
        surplusOpen += 1
        opens += 1
    else:
        surplusOpen -= 1
        closed += 1
    if surplusOpen < 0:
        print(0)
        exit()

remain = n - len(pf)
opensToBePlaced = n//2 - opens
closedToBePlaced = n//2 - closed


# We have to place O open brackets and C closed brackets such that the closed surplus never exceeds `surplusOpen`
# O = opens to be placed
# C = closed to be placed
# R = remain (total to be placed)
# H = height (surplus we start at, we cannot touch -1)
# C - O = H # we will always drop down to height 0 at the end, so this is true

# Normal ways to place without the exceeding exclusion is C(R, O)

# Attempt a completion, say H=3 R=7 O=2 C=5
# ) ) ) ) ( ( )
#       ^ violating index i=3
# At the bad prefix, there are H+1 more closed than open, since we dropped H+1 steps
# At the suffix, there is 1 less closed than open (this would result in H total more closed than open, which is what we need)

# If we flip the prefix, there are H+1 more open than closed in the prefix, making a total of H+2 more opened than closed
# Computing # of bad sequences:
# R spots to place into
# Our flip increased the open brackets by H+1
# O' = O + H + 1


# We can prove this is bijective in a similar manner to bracket sequences I
# Every input completion will map to a different output, otherwise we can find two inputs that somehow map to the same output, find a differing index, and discover a contradiction
# Every output is mapped by an input because we could un-reverse the prefix and get a valid setup

# So there are C(R, O') bad sequences

# Final answer is C(R, 0) - C(R, O')
# C(R, 0) - C(R, O + H + 1)

# This would work even for invalid sequences, see:
# ( ( ( N = 4
# O = -1
# C = 2
# R = 1
# H = 3
# C(1, -1) - C(1, 3) = 0 - 0
# Not airtight but combinatorics should just end up as 0


MAX_N = 10**6
MOD = 10**9 + 7
fact = [1] # 0! % MOD
for num in range(1, MAX_N + 1):
    nfac = (fact[-1] * num) % MOD
    fact.append(nfac)

invFact = [1] * (MAX_N + 1)
invFact[MAX_N] = pow(fact[MAX_N], MOD - 2, MOD)
for i in range(MAX_N, 0, -1):
    invFact[i - 1] = invFact[i] * i % MOD

def nCkMod(n, k):
    if k < 0 or k > n:
        return 0
    return fact[n] * invFact[k] % MOD * invFact[n - k] % MOD

ans = nCkMod(remain, opensToBePlaced) - nCkMod(remain, opensToBePlaced + surplusOpen + 1)
print(ans % MOD)