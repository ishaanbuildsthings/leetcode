import sys
input = sys.stdin.readline

t = int(input())
for _ in range(t):
    n = int(input())
    A = list(map(int, input().split()))

    # first one X can take X ops1, or less ops1 and a single ops2
    # in general we can convert some # of ops1 into ops2
    # establish the conversion ratio for everything holds when starting at 0

    num0 = A[0]
    num1 = A[1]
    denominator = n + 1

    # two systems of erquations
    # numOps1 =

    numOps1 = num1*n - num0 * (n - 1)
    numOps2 = 2*num0 - num1

    if numOps1 < 0 or numOps2 < 0 or numOps1 % denominator or numOps2 % denominator:
        print("NO")
        continue

    ops1 = numOps1 // denominator
    ops2 = numOps2 // denominator

    # check all equations

    didPrintBad = False
    for i, num in enumerate(A, start = 1):
        if i * ops1 + (n - i + 1) * ops2 != num:
            didPrintBad = True
            print('NO')
            break

    if didPrintBad:
        continue
    print('YES')


    #   1     2     3     4     5     6
    # 1  6  2  5  3  4  4  3   5  2  6  1



   # 1 or 4 ops
   # 2 or 3 ops
   # 2 ops only

   # 16   # here 1 op of 5 works to flip parity, or 3 ops, but 2 does not flip parity
   # 5 1