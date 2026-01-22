t = int(input())
for _ in range(t):
    n = int(input())
    A = input()
    B = input()

    # group 1 is even A indices and odd B indices
    g1 = 0
    g2 = 0
    for i in range(0, n, 2):
        if A[i] == "0":
            g1 += 1
    for i in range(1, n, 2):
        if B[i] == "0":
            g1 += 1
    
    # group 2 is odd A and even B
    for i in range(1, n, 2):
        if A[i] == "0":
            g2 += 1
    for i in range(0, n, 2):
        if B[i] == "0":
            g2 += 1
        
    evens = (n + 1) // 2
    odds = n - evens
    answer = g1 >= evens and g2 >= odds
    print("YES" if answer else "NO")
