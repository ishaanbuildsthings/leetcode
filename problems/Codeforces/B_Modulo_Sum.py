n, reqDivis = map(int, input().split())
arr = list(map(int, input().split()))

doableRemainders = 0 # bitset, seeing if remainder 0 after dividing by reqDivis is doable. We will track doable remainders from [0...reqDivis - 1].
# We don't consider the remainder of 0 initially doable because it is an empty subsequence
clearanceMask = (1 << (reqDivis + 1)) - 1 # prevent bitset from growing too big

for v in arr:
    v %= reqDivis # don't shift something by >=reqDivis since it would overflow and we don't need to consider those
    newRemainders = doableRemainders | (doableRemainders << v) | (1 << v)
    # we need to account for exceeding reqDivis, so if reqDivis is 5 and we have a remainder 2 and take a 7, we can make a remainder of 9 which we need to capture
    aboveMDoable = newRemainders >> reqDivis
    finalMask = (newRemainders | aboveMDoable) & clearanceMask
    doableRemainders = finalMask

print('YES' if bool(doableRemainders & 1) else 'NO')