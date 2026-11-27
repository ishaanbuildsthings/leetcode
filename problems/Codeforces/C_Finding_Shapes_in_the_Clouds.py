from collections import Counter
t = int(input())

def solve():
    n = int(input())
    s = input()
    if n % 2:
        print('NO')
        return
    
    # c = Counter(s)

    alts = 0
    for i in range(n - 1):
        if s[i] != s[i+1]:
            alts += 1
        
    if alts == n - 1:
        print('NO')
    else:
        print('YES')
   
    
    # even amount of 1s and 0s

    # 0  101

for _ in range(t):
    solve()