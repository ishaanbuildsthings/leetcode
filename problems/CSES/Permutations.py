n = int(input())
if n in [2, 3]:
    print('NO SOLUTION')
    exit()

res = []

curr = n - 1
while curr >= 1:
    res.append(curr)
    curr -= 2

curr = n
while curr >= 1:
    res.append(curr)
    curr -= 2

print(*res)