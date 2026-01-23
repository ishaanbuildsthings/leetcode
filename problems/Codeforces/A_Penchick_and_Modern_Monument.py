import collections
t = int(input())
for _ in range(t):
    n = int(input())
    A = list(map(int, input().split()))

    # Want
    #     /
    # / --


    # Have
    # \__
    #    \

    # pick some index, everything less than that value and everything more must chance
    INF = 1000000000
    res = INF

    c = collections.Counter(A)
    for k, v in c.items():
        others = n - v
        res = min(res, others)
    
    print(res)
