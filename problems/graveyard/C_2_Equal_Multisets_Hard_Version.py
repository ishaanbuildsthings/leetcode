t = int(input())

# TEMPLATE BY LEETGOAT.IO
# unions by depth
# ITERATIVE FAST VERSION
class DSU:
    __slots__ = ['parent', 'rank']
    def __init__(self, n):
        self.parent = list(range(n))
        self.rank = [0] * n
    def find(self, x):
        while self.parent[x] != x:
            self.parent[x] = self.parent[self.parent[x]]
            x = self.parent[x]
        return x
    def union(self, a, b):
        a, b = self.find(a), self.find(b)
        if a == b:
            return
        if self.rank[a] < self.rank[b]:
            a, b = b, a
        self.parent[b] = a
        if self.rank[a] == self.rank[b]:
            self.rank[a] += 1





def solve():
    # print('-------------')
    n, k = list(map(int, input().split()))
    A = list(map(int, input().split()))
    B = list(map(int, input().split()))
    # print(f'{n=} {k=}')
    # print(f'{A=}')
    # print(f'{B=}')

    uf = DSU(n)

    # first just make sure every non -1 number in B appears <= times in A

    # frqA = [0] * (n + 1)
    # frqB = [0] * (n + 1)
    # for v in A:
    #     frqA[v] += 1
    # for v in B:
    #     if v != -1:
    #         frqB[v] += 1
    
    # for number in range(1, n + 1):
    #     if frqB[number] > frqA[number]:
    #         print('NO')
    #         return
    
    # now B is a subset of A

    # check all K sized windows are a subset also
    frqA = [0] * (n + 1)
    frqB = [0] * (n + 1)
    for i in range(k):
        frqA[A[i]] += 1
        if B[i] != -1:
            frqB[B[i]] += 1
    for number in range(1, n + 1):
        if frqB[number] > frqA[number]:
            print('NO')
            return
    for r in range(k, n):
        gainA = A[r]
        gainB = B[r]
        lostA = A[r - k]
        lostB = B[r - k]
        frqA[gainA] += 1
        frqA[lostA] -= 1
        if gainB != -1:
            frqB[gainB] += 1
        if lostB != -1:
            frqB[lostB] -= 1
        
        if gainB != -1:
            if frqB[gainB] > frqA[gainB]:
                print('NO')
                return
        if frqB[lostA] > frqA[lostA]:
            print('NO')
            return
    
    for l in range(n):
        r = l + k
        if r >= n:
            break
        
        if A[l] == A[r]:
            uf.union(l, r)
            if B[l] != -1 and B[r] != -1:
                if B[l] != B[r]:
                    print('NO')
                    return
            if B[l] == B[r] == -1:
                continue
            mx = max(B[l], B[r])
            B[l] = B[r] = mx
            continue
        
        if B[l] == -1:
            B[l] = A[l]
        
        if B[r] == -1:
            B[r] = A[r]
        
        if (B[l] != A[l]) or (B[r] != A[r]):
            print("NO")
            return

    vals = {}
    for i in range(n):
        if B[i] == -1:
            continue
        root = uf.find(i)
        if root in vals:
            if vals[root] != B[i]:
                print('NO')
                return
        else:
            vals[root] = B[i]

    frqA = [0] * (n + 1)
    frqB = [0] * (n + 1)
    for i in range(k):
        frqA[A[i]] += 1
        if B[i] != -1:
            frqB[B[i]] += 1
        else:
            root = uf.find(i)
            if root in vals:
                frqB[vals[root]] += 1
    for number in range(1, n + 1):
        if frqB[number] > frqA[number]:
            print('NO')
            return
    print("YES")


for _ in range(t):
    solve()