t = int(input())
for _ in range(t):
    n = int(input())
    A = list(map(int, input().split()))
    xor = 0
    for v in A:
        xor ^= v
    if xor == 0:
        print('second')
    else:
        print('first')

# Base case, xor of 0 (no piles) is losing
# XOR not 0 (an existing pile) wins
# As we make turns the # of sticks goes down and therefore piles, eventually we reach one of these states on our turn

# Will a losing state of 0 always lead to a winning non-0 state?
# Yes because we remove something we change the XOR

# Can a winning state of non-0 always lead to a losing state of 0 for our opponent?
# Say the XOR of all numbers is 1001010, X

# 1000000
# 1000
# 10
# XOR of all of these is 1001010
# We need to set this XOR to 0

# Note that if we subtract some amount S from a pile P
# We obtain the new XOR via X ^ P ^ (P - S) 

# So X' = X ^ P ^ P'
# We want X' = 0
# 0 = X ^ P ^ P'
# P' = X ^ P

# X has some highest set bit, so at least one pile (we will call it P) does too
# Obviously there is some P' = P ^ X but we need P' < P to hold

# Since P has the highest set bit, all bits above it are 0, same with P' since P' cannot have a higher set bit, so all bits above msb are matched
# If P and X share the same highest bit then P' does not have it, so P' is smaller