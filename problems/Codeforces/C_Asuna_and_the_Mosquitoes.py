def solve(arr):
    arr.sort()
    if all(x % 2 == 0 for x in arr):
        return max(arr)
    if all(x % 2 == 1 for x in arr):
        return max(arr)
    
    # at least 1 even and 1 odd

    maxOdd = max(x for x in arr if x % 2 == 1)
    maxEven = max(x for x in arr if x % 2 == 0)
    sumOdd = sum(x for x in arr if x % 2 == 1)
    sumEven = sum(x for x in arr if x % 2 == 0)
    countOdd = sum(x % 2 for x in arr)
    countEven = len(arr) - countOdd

    # one option, take largest odd and all evens
    bigOddAllEvens = maxOdd + sumEven

    # theory, largest odd + all evens + all but 1 from each other odd
    otherOdds = countOdd - 1
    gainFromOdd = sumOdd - otherOdds

    return gainFromOdd + sumEven

    # If we want multiple odds

    # 2 3 (4) 5 (9)
    
    # 2 3 (3) 5 (10)

    # # We can take the largest even and pair it with an odd to get a single odd, then use that single odd to fully consume all evens



    # 2 3 4 5 9

    #   1 6 5 9


    return bigOddAllEvens

t = int(input())
for _ in range(t):
    n = int(input())
    A = list(map(int, input().split()))
    answer = solve(A)
    print(answer)

# # for A + B to be odd, we need exactly one odd and one even (non-0)

# If we have an odd and an even, say 5 and 4
# We can form 6 and 3
# 7 and 2
# 8 and 1
# 9 and 0

# # So odd + even can be fully drained

# What about 8 and 5

# 9 and 4
# 10 and 3

# Invariant: sum of 2 numbers stays the same

# If we have only evens: cannot do anything
# If we have only odds, cannot do anything
# Implies we have at least one even and one odd
# We can take the odd and fully drain the even, then repeat for all other evens

# So take the largest odd + all evens as an option

# Or the largest even + all odds