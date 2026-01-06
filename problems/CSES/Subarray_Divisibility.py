n = int(input())
A = list(map(int, input().split()))
mp = { '0': 1 } # mp[remainder when modded by n] -> count of how many times that prefix has occured
# string protects against hashmap blowups ;)
res = 0
remainderPf = 0
for v in A:
    remainderPf = (remainderPf + v) % n
    res += mp.get(str(remainderPf), 0)
    mp[str(remainderPf)] = mp.get(str(remainderPf), 0) + 1

print(res)
