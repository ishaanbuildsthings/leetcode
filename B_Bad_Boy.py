t = int(input())
for _ in range(t):
    height, width, row, col = map(int,input().split())
    # print('==================')
    # print(f'{height=} {width=}')
    # print(f'{row=} {col=}')

    def dist(p1, p2):
        xd = abs(p1[0] - p2[0])
        yd = abs(p1[1] - p2[1])
        return xd + yd

    corners = [[1,1],[height,1],[1,width],[height,width]]
    res = -1
    resPairs = []
    for i in range(4):
        for j in range(4):
            c1 = corners[i]
            c2 = corners[j]
            # throw to corners[i] first, then corners[j]
            d1 = dist((row,col), c1)
            d2 = dist(c1, c2)
            d3 = dist(c2, (row,col))
            distSum = d1 + d2 + d3
            if distSum > res:
                res = distSum
                resPairs = [c1, c2]
    # print(f'{resPairs=}')
    v = [resPairs[0][0], resPairs[0][1], resPairs[1][0], resPairs[1][1]]
    print(*v)



# x A x x
# x x x x
# x x x x
# x x x x