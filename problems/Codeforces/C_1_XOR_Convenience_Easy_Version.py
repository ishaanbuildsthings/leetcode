tests = int(input())
for _ in range(tests):
    n = int(input())
    # I know this looks written by AI I promise it is not lol
    # We can always put 1 at the end
    res = [None] * n
    res[-1] = 1

    # Tracking which numbers we have placed, so I know the missing number to place at i=0
    taken = [False] * (n + 1)
    taken[1] = True

    # For every number from index 1...n-2 (0-indexed), we can XOR it with a 1
    for i in range(1, n - 1):
        permI = i + 1
        res[i] = permI ^ 1
        # print(f'placing: {permI ^ 1}')
        taken[permI ^ 1] = True
    

    # Place the very first number
    for number in range(1, n + 1):
        if not taken[number]:
            res[0] = number

    print(*res)