s = 'Z' + input()
n = len(s)

# A C G T -> 0 1 2 3
# nxt[i][letterI] will tell us the first j where j>i with that letter, or infinity if it doesn't exist
# Imagine we have ACGTACGT, we first pick T, and then T again (technically doesn't matter), but we need to do j>i not j>=i to allow jumping to the same letter
nxt = [
    [
        float('inf') for _ in range(4)
    ] for _ in range(n)
]
mp = {'A' : 0, 'C' : 1, 'G' : 2, 'T' : 3}
idxToV = {0 : 'A', 1 : 'C', 2 : 'G', 3 : 'T'}
currRight = [float('inf')] * 4
for i in range(n - 1, -1, -1):
    for updateI in range(4):
        nxt[i][updateI] = currRight[updateI]
    if i == 0:
        break
    v = s[i]
    updateI = mp[v]
    currRight[updateI] = i

res = []
i = 0
while i < n:
    biggest = max(nxt[i])
    idx = nxt[i].index(biggest)
    res.append(idxToV[idx])
    i = biggest
print(''.join(res))


