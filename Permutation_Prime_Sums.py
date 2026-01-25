# import itertools

# def isPrime(v):
#     return v in {2, 3, 5, 7, 11, 13, 17, 19, 23}

# arr = [num for num in range(1, 7)]
# perms = list(itertools.permutations(arr))
# for k in range(len(perms)):
#     for k2 in range(k, len(perms)):
#         p = perms[k]
#         p2 = perms[k2]
#         fail = False
#         for i in range(len(p)):
#             if not isPrime(p[i] + p2[i]):
#                 fail = True
#                 break
#         if not fail:
#             print('=======')
#             print(p)
#             print(p2)

# # if 1+n is prime (meaning n is even) then we are free

# 1 2 3 4 5 6 7
# 1 5 4 3 2 7 6

# 1 2 3 4 5 6 7 8 9 10
# 2 1  10 9 8 7 6 5 4 3   
# # # 
# # If we have an odd N we have one more odd than even

# # So 1:1 now we have even amount of odds with evens

# # If we have an even N

# #   1 2 3 4
# # 1 2 3 4

# # Still pair any odd with even

# # a b c
# # b c a

# # a b c
# # b a c

# # 1   (2 3 4 5 6 7) (21)

# # 1 7 4 6 5
# # 1 4 7 5 6

n = int(input())
MX = 2 * n + 1 # +1 to hande n=1 lol
isPrime = [True] * (MX)
isPrime[0] = False
isPrime[1] = False
for div in range(MX):
    if not isPrime[div]:
        continue
    for mult in range(div * div, MX, div):
        isPrime[mult] = False

def findNextPrime(number):
    for number2 in range(number + 1, MX):
        if isPrime[number2]:
            return number2

pairs = []
curr = n
while curr > 0:
    nxt = findNextPrime(curr) # 7
    diff = nxt - curr # 2
    pairs.append((diff, curr))
    curr = diff - 1

# print(pairs)

res1 = []
res2 = []
for a, b in pairs:
    tot = a + b
    for number in range(a, b + 1):
        res1.append(number)
        res2.append(tot - number)

print(*res1)
print(*res2)

