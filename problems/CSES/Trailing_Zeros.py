n = int(input())

# for any n! there are fewer factors of 5 than 2, so we count 5s
res = 0

curr = 5
while curr <= n:
    res += n // curr
    curr *= 5

print(res)