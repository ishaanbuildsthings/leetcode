import math
def solve():
    n = int(input())
    arr = list(map(int, input().split()))

    res = 0
    B = math.ceil(math.sqrt(n))
    for j, v in enumerate(arr):
        # x * v = j - i
        # so j-i is a multiple of v
        # if v is big we can enumerate all multiples
        if v >= B:
            # look backwards
            mult = 1
            while j - (mult * v) >= 0:
                i = j - (mult * v)
                # print(f'i: {i}')
                res += (v * arr[i] == (j - i))
                mult += 1
            # look forwards
            mult = 1
            while (j + (mult * v)) < n:
                k = j + (mult * v)
                res += (v * arr[k] == (k - j)) and (v != arr[k]) # on the forward pass don't allow things like B * B because we double count then
                mult += 1
            
        # if v is small, it could be multiplied by a number < B
        # but not >= B because we handle that above
        else:
            for smaller in range(1, B):
                vv = v * smaller
                i = j - vv
                if i >= 0 and (j - i) == vv and arr[i] == smaller:
                    res += 1
            
    print(res)


t = int(input())
for _ in range(t):
    solve()