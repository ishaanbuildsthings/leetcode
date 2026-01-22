from math import gcd
T = int(input())

def normSlope(p1, p2):
    rise = p2[1] - p1[1]
    run = p2[0] - p1[0]
    if run == 0:
        return (1, 0) # sentinel
    
    g = gcd(abs(rise), abs(run))
    rise //= g
    run //= g
    if rise < 0:
        rise = -rise
        run = -run
    
    return (rise, run)

for _ in range(T):
    x1, y1, x2, y2, x3, y3, x4, y4 = map(int, input().split())
    p1 = (x1, y1)
    p2 = (x2, y2)
    p3 = (x3, y3)
    p4 = (x4, y4)
    s1 = normSlope(p1, p2)
    s2 = normSlope(p3, p4)
    print(f'{s1=} {s2=}')
    if s1 != s2:
        print("YES")
        continue
    
    # same slope could still intersect if the same line
    s3 = normSlope(p2, p3)
    if s3 == s1:
        print("YES")
    else:
        print("NO")