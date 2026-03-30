t = int(input())

def solve():
    n, k = list(map(int, input().split()))
    a = list(map(int, input().split()))
    b = list(map(int, input().split()))
    if k == n:
        frq1 = [0] * (n + 1)
        frq2 = [0] * (n + 1)
        for v in a:
            frq1[v] += 1
        for v in b:
            if v != -1:
                frq2[v] += 1
        for v in a:
            if frq2[v] > frq1[v]:
                print('NO')
                return
        for v in b:
            if v != -1:
                if frq2[v] > frq1[v]:
                    print('NO')
                    return
        print('YES')
        return
    
    right = k - 1
    left = n - k

    if right < left:
        # otherwise, every number in A must appear in B or be negative 1
        for i in range(n):
            if a[i] != -1:
                if b[i] not in [a[i], -1]:
                    print('NO')
                    return
        for i in range(n):
            if b[i] != -1:
                if a[i] != b[i]:
                    print('NO')
                    return
        print('YES')
        return
    
    # if right >= left we have some position that always overlaps

    # check prefix
    for i in range(left):
        if a[i] != -1:
            if b[i] not in [a[i], -1]:
                print('NO')
                return
    for i in range(left):
        if b[i] != -1:
            if a[i] != b[i]:
                print('NO')
                return
    
    # check suffix
    for i in range(right+1,n):
        if a[i] != -1:
            if b[i] not in [a[i], -1]:
                print('NO')
                return
    for i in range(right+1,n):
        if b[i] != -1:
            if a[i] != b[i]:
                print('NO')
                return
    
    a1 = a[left:right+1]
    s1 = set([str(x) for x in a1])
    a2 = b[left:right+1]
    from collections import Counter
    frq2 = Counter([str(x) for x in a2])
    for v in a2:
        if v == -1:
            continue
        if frq2[str(v)] > 1:
            print('NO')
            return
        if str(v) not in s1:
            print('NO')
            return
    
    print('YES')
        

for _ in range(t):
    solve()