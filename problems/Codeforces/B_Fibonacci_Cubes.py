import sys

# boxes are 1 2 3 5 8 13 21 34 55 89

def solve(n, m, boxes):
    # print(f'solving for n={n} m={m} boxes={boxes}')
    # boxes is w, l, h
    # n is number of cubes
    # m is number of boxes

    resArr = []

    for box in boxes:

      cubes = [1, 2, 3, 5, 8, 13, 21, 34, 55, 89][:n]
      # print(f'solving for box={box} cubes={cubes}')
      totArea = sum(c ** 3 for c in cubes)
      boxArea = box[0] * box[1] * box[2]
      # print(f'totArea={totArea} boxArea={boxArea}')

      # if any two ever add up and cant fit into the biggest dimension we fail
      bigTwoSideLengths = cubes[-1] + cubes[-2]
      if bigTwoSideLengths > max(box):
        # print('bigTwoSideLengths > max(box), adding a 0')
        resArr.append('0')
        continue

      if totArea > boxArea:
        # print('totArea < boxArea, adding a 0')
        resArr.append('0')
        continue

      tightDimension = min(box)
      # if we definitely cannot fit
      if tightDimension < max(cubes):
          resArr.append('0')
          continue
      else:
          resArr.append('1')
          continue

    return ''.join(resArr)

input = sys.stdin.readline

t = int(input())
for _ in range(t):
    n, m = map(int, input().split())
    boxes = []
    for _ in range(m):
        w, l, h = map(int, input().split())
        boxes.append((w, l, h))

    result = solve(n, m, boxes)
    print(result)