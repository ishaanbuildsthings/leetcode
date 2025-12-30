from collections import Counter
T = int(input())
for _ in range(T):
    # print(F'============')
    t = input()
    s = input()
    # print(f'{s=}')
    # print(f'{t=}')

    sArr = sorted([x for x in s])
    # print(f'{sArr=}')

    cBig = Counter(sArr)
    cSmall = Counter(t)

    if not all(cSmall[key] <= cBig[key] for key in cSmall):
        print('Impossible')
        continue
    cBudget = cBig - cSmall
    # print(f'{cBudget=}')

    budget = []
    for k, v in cBudget.items():
        budget.extend([k] * v)
    budget.sort()

    # print(f'{budget=}')
    # print(f'{t=}')


    resArr = []
    i = j = 0
    while i < len(t) and j < len(budget):
        if t[i] <= budget[j]:
            resArr.append(t[i])
            i += 1
        elif t[i] > budget[j]:
            resArr.append(budget[j])
            j += 1
    while i < len(t):
        resArr.append(t[i])
        i += 1
    while j < len(budget):
        resArr.append(budget[j])
        j += 1
    print(''.join(resArr))

    # a b c 
    # other budget: e f