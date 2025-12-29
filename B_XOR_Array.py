from random import randint

T = int(input())
for _ in range(T):
    n, L, R = map(int, input().split())
    L -= 1
    R -= 1
    # print(f'{n=} {L=} {R=}')
    resArr = [-1] * n

    # print(f'{resArr=}')
    
    pfXors = [0] # xors from 0...i-1
    pfXorSet = set()
    pfXorSet.add(str(0))

    for i in range(n):
        if i == R:
            currXor = 0
            for j in range(L, R):
                currXor ^= resArr[j]
            resArr[i] = currXor
            newXor = pfXors[-1] ^ resArr[i]
            pfXors.append(newXor)
            pfXorSet.add(str(newXor))
        else:
            # generate a random number, but if it forms a prefix xor that exists, we cannot use it
            while True:
                r = randint(1, 10**8)
                newPfXor = pfXors[-1] ^ r
                if str(newPfXor) in pfXorSet:
                    continue
                pfXorSet.add(str(newPfXor))
                pfXors.append(newPfXor)
                resArr[i] = r
                break
    
    print(*resArr)