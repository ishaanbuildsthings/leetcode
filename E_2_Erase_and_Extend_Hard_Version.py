# the moment our prefix is smaller than our suffix, we should cull that suffix to use the prefix

import random
import random

class LexSubarrCmp:
    def __init__(self, a):
        self.a = a
        self.n = len(a)
        self.mod1 = 1000000007
        self.mod2 = 100000003
        self.base = random.randrange(911382323, 972663749)

        self.pw1 = [1] * (self.n + 1)
        self.pw2 = [1] * (self.n + 1)
        self.h1 = [0] * (self.n + 1)
        self.h2 = [0] * (self.n + 1)

        for i, v in enumerate(a):
            x = ord(v)
            self.pw1[i + 1] = (self.pw1[i] * self.base) % self.mod1
            self.pw2[i + 1] = (self.pw2[i] * self.base) % self.mod2
            self.h1[i + 1] = (self.h1[i] * self.base + x) % self.mod1
            self.h2[i + 1] = (self.h2[i] * self.base + x) % self.mod2

    def getHash(self, l, r):
        a1 = self.h1[r + 1] - (self.h1[l] * self.pw1[r - l + 1]) % self.mod1
        a2 = self.h2[r + 1] - (self.h2[l] * self.pw2[r - l + 1]) % self.mod2
        return (a1 % self.mod1, a2 % self.mod2)

    def lcp(self, l1, r1, l2, r2):
        lo = 0
        hi = min(r1 - l1 + 1, r2 - l2 + 1)
        while lo < hi:
            mid = (lo + hi + 1) // 2
            if self.getHash(l1, l1 + mid - 1) == self.getHash(l2, l2 + mid - 1):
                lo = mid
            else:
                hi = mid - 1
        return lo

    def isLess(self, l1, r1, l2, r2):
        k = self.lcp(l1, r1, l2, r2)
        len1 = r1 - l1 + 1
        len2 = r2 - l2 + 1
        if k == min(len1, len2):
            return len1 < len2
        return self.a[l1 + k] < self.a[l2 + k]


n, k = map(int, input().split())
s = input()
# print(f'{s=}')
# v = LexSubstrCmp(s)
# best = n - 1

ls = list(s)

# print(ls)

modder = LexSubarrCmp(ls[:])

pf = 0
while True:
    if pf >= len(ls):
        break
    # if 0...pf is smaller, we pop the suffix and reset pf to 0
    l1 = 0
    r1 = pf

    r2 = len(ls) - 1
    l2 = r2 - pf

    if l2 <= r1:
        break
    if modder.isLess(l1, r1, l2, r2):
        for _ in range(pf + 1):
            ls.pop()
        pf = 0
    else:
        pf += 1

# print(f'{pf=}')
# print(f'{ls=}')

pf -= 1

used = s[:pf + 1]

portion = ''.join(ls)
# print(f'portion: {portion}')

full = k // len(portion)
answer = portion * full
remain = k - len(answer)
answer += portion[:remain]
print(answer)
# full = k // len(used)
# answer = full * used
# remain = k - len(answer)
# answer += s[:remain]
# print(answer)
# # find largest prefix that is smaller than the suffix

# # if our prefix is smaller than that suffix, we lose the suffix and continue
# for pfLength in range(n + 1):
#     l1 = 0
#     r1 = l1 + pfLength - 1

#     r2 = n - 1
#     l2 = r2 - pfLength + 1

#     # print(f'{l1=} {r1=} {l2=} {r2=}')

#     if l2 <= r1:
#         continue
    
#     if v.isLess(l1, r1, l2, r2):
#         best = r1
#         break

# print(f'{best=}')

# cutFromEnd = best + 1

# answer = s[:-cutFromEnd]

# print(f'then answer is: {answer} with cut from end: {cutFromEnd}')

# length = best + 1

# fulls = k // length

# answer = fulls * s[:length]
# remain = k - len(answer)
# answer += s[:remain]

# print(answer)
    

    

