from collections import Counter
s = input()
res = []
c = Counter(s)
def backtrack(curr):
    if len(curr) == len(s):
        res.append(curr)
        return
    for k, v in c.items():
        if not v:
            continue
        c[k] -= 1
        backtrack(curr + k)
        c[k] += 1
backtrack('')
print(len(res))
res.sort()
for v in res:
    print(v)
    