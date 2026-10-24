n = int(input())
pattern = input()
m = len(pattern)
MOD = 10**9 + 7
import functools
import sys
sys.setrecursionlimit(1500)
abc = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'

properBorders = [0] * m
for i in range(1, m):
    v = pattern[i]
    prevSize = properBorders[i - 1]
    if v == pattern[prevSize]:
        properBorders[i] = prevSize + 1
        continue
    while prevSize:
        prevSize = properBorders[prevSize - 1]
        if v == pattern[prevSize]:
            properBorders[i] = prevSize + 1
            break

@functools.cache
def dp(currentMatch, nextLetter):
    if nextLetter == pattern[currentMatch]:
        return 1 + currentMatch
    if not currentMatch:
        return 0
    smallerSize = properBorders[currentMatch - 1]
    return dp(smallerSize, nextLetter)

pow26 = [1]
for i in range(1, n + 1):
    pow26.append((pow26[-1] * 26) % MOD)

cache2 = [[-1 for _ in range(m)] for _ in range(n)]

def dp2(i, currentMatch):
    if i == n:
        return 0
    if cache2[i][currentMatch] != -1:
        return cache2[i][currentMatch]

    res = 0
    for nxtLetterI in range(26):
        letter = abc[nxtLetterI]
        nmatch = dp(currentMatch, letter)
        if nmatch == m:
            remainLetters = n - i - 1
            res += pow26[remainLetters]
        else:
            res += dp2(i + 1, nmatch)

    cache2[i][currentMatch] = res % MOD
    return cache2[i][currentMatch]

ans = dp2(0, 0)
print(ans)