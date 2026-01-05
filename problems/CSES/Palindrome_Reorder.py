s = input()

import collections

c = collections.Counter(s)

odd = None # odd letter
for k, v in c.items():
    if v % 2:
        if odd:
            print('NO SOLUTION')
            exit()
        odd = k


if (odd and len(s) % 2 == 0) or (not odd and len(s) % 2 == 1):
    print('NO SOLUTION')
    exit()
res = [None] * len(s)
if odd:
    mid = len(s) // 2
    res[mid] = odd
    c[odd] -= 1

i = 0
for k, v in c.items():
    for j in range(i, i + (v // 2)):
        res[j] = k
        res[len(s) - 1 - j] = k
    i += v // 2

print(''.join(res))