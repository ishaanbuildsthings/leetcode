t = int(input())
for _ in range(t):
    row, col = map(int, input().split())
    layer = max(row, col) + 1
    numsBeforeLayer = (layer - 1) ** 2
    direction = 'rightUp' if layer % 2 else 'downLeft'
    if direction == 'rightUp':
        horizGain = col
        vertGain = layer - row - 1
        print(numsBeforeLayer + horizGain + vertGain)
        continue
    else:

        vertGain = row