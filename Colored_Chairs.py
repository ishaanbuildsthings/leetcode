import sys

def ask(i):
    print(f"? {i}", flush=True)
    return sys.stdin.readline().strip()

def answer(i):
    print(f"! {i}", flush=True)
    sys.exit(0)

n = int(input())

c1 = ask(1)
c2 = ask(n)
if c1 == c2:
    answer(n)

def recurse(l, r, leftColor, rightColor):
    if l + 1 == r:
        answer(l)
    
    m = (l + r) // 2
    midColor = ask(m)
    edgesEqual = leftColor == rightColor
    leftEqual = leftColor == midColor
    rightEqual = midColor == rightColor
    leftWidth = m - l + 1
    rightWidth = r - m + 1

    # answer is in evenWidth same color or oddWidth different color
    if (leftWidth % 2 == 0 and leftEqual) or (leftWidth % 2 == 1 and not leftEqual):
        recurse(l, m, leftColor, midColor)
    else:
        recurse(m, r, midColor, rightColor)



recurse(1, n, c1, c2)

