t = int(input())
for _ in range(t):
    n = int(input())
    A = list(map(int, input().split()))
    # for a number, find how many numbers share an MSB, the AND will always win if the MSB is shared
    # otherwise, XOR wins
    msb = [0] * 32
    res = 0
    def maxset(num):
        return num.bit_length() - 1

    for num in A:
        maxHere = maxset(num)
        res += msb[maxHere]
        msb[maxHere] += 1
    
    print(res)

