T = int(input())
for _ in range(T):
    s = input()
    c = sum(x == 'Y' for x in s)
    print('YES' if c <= 1 else 'NO')