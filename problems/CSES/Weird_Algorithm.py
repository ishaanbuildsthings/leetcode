n = int(input())
res = []
curr = n

while curr != 1:
    res.append(curr)
    if curr % 2:
        curr *= 3
        curr += 1
    else:
        curr //= 2
res.append(curr)
print(*res)
