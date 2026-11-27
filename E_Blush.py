t = int(input())
import math

def solve():
    a, x, k = map(int, input().split())

    ans = a

    jumps = [1]
    for power in range(50):
        jumps.append(jumps[-1] * 2)
    
    small = math.ceil(k / 2)
    big = k - small

    # for each small size, whats the fewest # of small stuns we can use, where the rest can be big stuns, and we stay ahead

    # print(f'{small=} {big=}')

    for i in range(len(jumps) - 1):
        smallJump = jumps[i]
        bigJump = jumps[i+1]

        smallCycle = i + 1
        bigCycle = i + 2

        smallConsec = (2 * smallJump) - 1
        bigConsec = (2 * bigJump) - 1

        l = 0
        r = k
        resFewest = None
        aubreyEnd = None
        sunnyEnd = None
        while l <= r:
            m = (l + r) // 2

            # m = 2

            smallStuns = m
            bigStuns = k - smallStuns

            smallGain = smallConsec * smallStuns
            bigGain = bigConsec * bigStuns
            totalGain = smallGain + bigGain + 1
            aubrey = totalGain

            steps = (smallCycle * smallStuns) + (bigCycle * bigStuns) + 1
            sunny = a + (x * steps)

            if sunny > aubrey:
                resFewest = smallStuns
                aubreyEnd = aubrey
                sunnyEnd = sunny
                r = m - 1
            else:
                l = m + 1
            
            # break
        
        if resFewest is None:
            continue

        
        
        nxtJump = 2
        while sunnyEnd > aubreyEnd:
            ans = max(ans, sunnyEnd)
            aubreyEnd += nxtJump
            nxtJump *= 2
            sunnyEnd += x
        


    
    print(ans)






for _ in range(t):
    solve()