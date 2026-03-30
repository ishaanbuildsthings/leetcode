from math import gcd, lcm
def solve():
    n = int(input())
    A = list(map(int,input().split()))
    B = list(map(int,input().split()))
    res = 0
    for i in range(n):
        # print('-----')
        v = A[i]
        # print(f'{res=}')
        # print(f'{i=}')
        if i > 0 and i < n - 1:
            # print(f'mid')
            left = A[i-1]
            right = A[i+1]
            g1 = gcd(left,v)
            g2 = gcd(right,v)
            if g1 == v or g2 == v:
                continue
            if g1 == g2:
                res += 1
                continue
            nv = lcm(g1,g2)
            if nv < v:
                res += 1
                continue
        elif i == 0:
            # print('start')
            right = A[i+1]
            g1 = gcd(v,right)
            if g1 != v:
                res += 1
                continue
        else:
            # print('end')
            left = A[i-1]
            g1 = gcd(v,left)
            if g1 != v:
                res += 1
                continue
    print(res)

            
            
    
    # 2 10 15

    #  2  5

t = int(input())
for _ in range(t):
    solve()