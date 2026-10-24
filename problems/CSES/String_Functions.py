s = input()
n = len(s)

# z func
def zFunction(s):
    n = len(s)
    z = [0] * n
    l, r = 0, 0
    for i in range(1, n):
        if i <= r:
            z[i] = min(r - i + 1, z[i - l])
        while i + z[i] < n and s[z[i]] == s[i + z[i]]:
            z[i] += 1
        if i + z[i] - 1 > r:
            l, r = i, i + z[i] - 1
    return z
print(*zFunction(s))

# kmp

properBorders = [0] * n
for i in range(1, n):
    v = s[i]
    prevSz = properBorders[i - 1]
    if s[prevSz] == v:
        properBorders[i] = prevSz + 1
        continue
    
    while prevSz:
        prevSz = properBorders[prevSz - 1]
        if s[prevSz] == v:
            properBorders[i] = prevSz + 1
            break
    
print(*properBorders)