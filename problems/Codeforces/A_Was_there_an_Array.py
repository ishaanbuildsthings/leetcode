t = int(input())
for _ in range(t):
    n = int(input())
    B = list(map(int, input().split()))
    broken = False
    for i in range(len(B) - 2):
        if B[i] == 1 and B[i + 1] == 0 and B[i + 2] == 1:
            print('NO')
            broken = True
            break
    
    if not broken:
        print('YES')
    
