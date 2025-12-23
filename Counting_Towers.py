MOD = 10**9 + 7

MAX_N = 10**6

# If previous is combined, we can either start 2 individual blocks, start a double block, or extend the previous double
# If previous is separate, we can either start 2 individual blocks, extend 1 restart 1, extend 1 restart the other, extend both, or start a new double
prevCombined = 1 # we can start with a double block
prevSeparate = 1 # we can start with 2 single blocks

answers = [0] * (MAX_N + 1)
answers[1] = 2

for height in range(2, MAX_N + 1):
    newCombined = 2 * prevCombined + prevSeparate
    newSeparate = prevCombined + 4 * prevSeparate
    prevCombined = newCombined % MOD
    prevSeparate = newSeparate % MOD
    answers[height] = (prevCombined + prevSeparate) % MOD

t = int(input())
for _ in range(t):
    height = int(input())
    print(answers[height])

