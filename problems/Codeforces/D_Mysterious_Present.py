n, w, h = map(int, input().split())
cards = []
for i in range(n):
    wi, hi = map(int, input().split())
    if w < wi and h < hi:
        cards.append((wi, hi, i + 1))
if not cards:
    print(0)
    exit()

cards.sort(key=lambda x: (x[0], -x[1]))
lis = [0] * len(cards)
prevI = [-1] * len(cards)
for r in range(len(cards)):
    lsHere = 1
    for j in range(r):
        if cards[j][1] < cards[r][1]:
            if lis[j] + 1 > lsHere:
                lsHere = lis[j] + 1
                prevI[r] = j
    lis[r] = lsHere

print(max(lis))
currI = lis.index(max(lis))
chain = []
while currI != -1:
    currCard = cards[currI][2]
    chain.append(currCard)
    currI = prevI[currI]
print(*chain[::-1])

