import sys
input = sys.stdin.readline

t = int(input())
for _ in range(t):
    n, x = map(int, input().split())
    skills = list(map(int, input().split()))
    # print(f'{skills=}, {x=}')

    skills.sort(reverse=True)
    i = 0
    res = 0
    while i < len(skills):
        j = i
        while j < len(skills):
            currSize = j - i + 1
            currMin = skills[j]
            currScore = currSize * currMin
            if currScore >= x:
                res += 1
                break
            j += 1
        i = j + 1
    print(res)