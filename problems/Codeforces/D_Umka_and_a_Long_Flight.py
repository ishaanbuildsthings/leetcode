fib = [1, 1]
for fibn in range(2, 50):
    fib.append(fib[fibn-1] + fib[fibn-2])

def solve():
    n, x, y = map(int, input().split())
    def doable(smallHeight, largeWidth, r, c):
        if smallHeight == 1:
            return True
        # if the column is in bounds either way we cannot place this single cell
        if c < smallHeight and largeWidth - smallHeight <= c:
            return False
        
        prev = largeWidth - smallHeight

        # move the r,c to have the c be on the left
        if c >= largeWidth // 2:
            nc = largeWidth - c - 1
            nr = smallHeight - r - 1
        else:
            nc = c
            nr = r
        distFromTop = nr
        finalC = distFromTop
        truncatedWidth = largeWidth - smallHeight
        distFromRight = truncatedWidth - nc - 1
        finalR = distFromRight
        return doable(prev, smallHeight, finalR, finalC)

    height = fib[n]
    width = fib[n + 1]

    answer = doable(height, width, x - 1, y - 1)
    if answer:
        print("YES")
    else:
        print("NO")

t = int(input())
for _ in range(t):
    solve()