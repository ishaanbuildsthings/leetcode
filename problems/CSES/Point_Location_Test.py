t = int(input())
for _ in range(t):
    x1, y1, x2, y2, x3, y3 = map(int, input().split())
    x2 -= x1
    y2 -= y1
    x3 -= x1
    y3 -= y1
    v = x3*y2 - x2*y3
    if v == 0:
        print("TOUCH")
    elif v < 0:
        print("LEFT")
    else:
        print("RIGHT")