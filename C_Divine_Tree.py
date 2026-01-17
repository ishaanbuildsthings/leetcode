from collections import deque
def deque_insert(d: deque, i: int, x):
    n = len(d)
    if i < 0:
        i += n
    i = max(0, min(i, n))   # clamp like list insert behavior
    d.rotate(-i)
    d.appendleft(x)
    d.rotate(i)


# we have N nodes from 1 to N
# We can make any tree with a sum of M <= 1e12 by taking path minimums

# Smallest we can do is when the root is 1 we can form a total sum of N
# It will always be N

# If we use the root of 2
# We can place our 1 above or below certain nodes

# So we get 2 + (n-2) we can pick to contribute 1 or 2, + 1

# If we picked like 2->1234567 we would get N+1 score
# If we picked 2->65431 we would get  11 score

# So root 1 -> exactly N
# root 2 -> N+1 to 2N - 1

# root 3 we could have 3->5421 which gives 3*(N-1) + 1
# 3->1245 gives 3 + (N - 1)

# root 3-> N + 2 up to 3N - 2

# root X -> (N + X - 1) up to (X*N - (X-1))


# 1 2 3 4 5 6 7
# default state, we form sum N

# to increase by 1 we can swap the first 2:

# 2 1 3 4 5 6 7

# to increase by 1 again, we swap the second 2

# 2 3 1 4 5 6 7


# 2 3 4 5 6 7 1

# to increase by 1 again, we swap the first 2
# 3 2 4 5 6 7 1

# but we can only go to:
# 3 4 5 6 7 | 2 1


def solve(n, totalDivine):
    maxGainable = n * (n + 1) / 2
    if totalDivine > maxGainable:
        return -1
    if totalDivine < n:
        return -1
    
    arr = [x for x in range(1, n + 1)]
    curr = n # current score

    remain = totalDivine - curr # need to gain this much more score
    q = deque(arr)
    # print(f'{q=}')

    movedToBack = 0

    for numberToMove in range(1, n):
        gainable = n - numberToMove # moving the 1 could gain us at most 6 points when n=7
        if gainable >= remain:
            popped = q.popleft()
            deque_insert(q, remain, popped)
            break
        
        remain -= gainable
        movedToBack = numberToMove
        q.popleft()
        # place that number as far back as we can
    
    # print(f'q is: {q}')
    # print(f'{movedToBack=}')

    for number in range(movedToBack, 0, -1):
        q.append(number)
    
    # print(f'final q: {q}')

    return q


t = int(input())
for _ in range(t):
    n, totalDivine = map(int, input().split())
    # print('======')
    ans = solve(n, totalDivine)
    if ans == -1:
        print(-1)
        continue
    print(ans[0])
    for i in range(len(ans) - 1):
        print(f'{ans[i]} {ans[i + 1]}')