def solve():
    n = int(input())
    two = [[1, 1],[2,1]]
    three = [[1, 1], [1, 2], [3, 2]]
    four = [[1, 1], [1, 2], [4, 2], [4, 4]]

    if n <= 4:
        used = two if n == 2 else three if n == 3 else four
        for r, c in used:
            print(f'{r} {c}')
        return
    for dimension in range(5, n + 1):
        four.append((dimension, dimension))
    for r, c in four:
        print(f'{r} {c}')
t = int(input())
for _ in range(t):
    solve()
    print()