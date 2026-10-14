n = int(input())
MOD = 10**9 + 7

D = [1, 0, 1]
for d in range(3, n + 1):
    resHere = 0
    # clean swap
    others = d - 1
    resHere += others * D[d - 2]
    
    resHere += others * D[d - 1]
    
    resHere %= MOD
    D.append(resHere)

print(D[n])


