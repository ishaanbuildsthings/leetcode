s = input()
res = 1
curr = 1
for i in range(1, len(s)):
    if s[i] == s[i-1]:
        curr += 1
        res = max(res, curr)
    else:
        curr = 1
print(res)