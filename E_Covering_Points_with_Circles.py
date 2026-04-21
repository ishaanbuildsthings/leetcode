import math
n, r = list(map(int, input().split()))

def overlap(cx, cy, px, py):
    dist = (px - cx)**2 + (py-cy)**2
    return dist <= r*r

points = []
for _ in range(n):
    x, y = list(map(int, input().split()))
    points.append((x, y))

diff = math.ceil(r * math.sqrt(3)) # actual vertical offset between points

used = set() # holds (str(x), str(y))

for x, y in points:
    row1 = y // diff
    # row1 centered at y=0
    # row2 centered at y=h
    rows = [row1 - 2, row1 - 1, row1, row1 + 1, row1 + 2]
    for row in rows:
        col = (x - r * row) // (2*r)
        cols = [col - 2, col - 1, col, col + 1, col + 2]
        for column in cols:
            cx = (2 * r * column) + (r * row)
            if overlap(cx, diff * row, x, y):
                used.add((str(cx), str(diff * row)))
                break
        else:
            continue
        break

print(len(used))
for x, y in used:
    print(f'{x} {y}')



