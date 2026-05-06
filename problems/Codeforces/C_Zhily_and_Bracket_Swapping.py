def solve():
    n = int(input())
    A = list(input())
    B = list(input())
    # print(f'{A=} {B=}')
    aSurplus = 0
    bSurplus = 0
    for i in range(n):
        a = A[i]
        b = B[i]
        if a == b:
            if a == '(':
                aSurplus += 1
                bSurplus += 1
            else:
                aSurplus -= 1
                bSurplus -= 1
            if min(aSurplus, bSurplus) < 0:
                return False
            continue
        if aSurplus <= bSurplus:
            aSurplus += 1
            bSurplus -= 1
        else:
            bSurplus += 1
            aSurplus -= 1
        if min(aSurplus, bSurplus) < 0:
            return False
    return aSurplus == bSurplus == 0

t = int(input())
for _ in range(t):
   ans = solve()
   print('YES' if ans else 'NO')