def solve():
    s = input()
    if len(s) <= 1:
        print(s)
        return
    # ending characters is the sum of some previous digit set, that digit set is a number itself
    # 75 | 12 | 3
    # 3 is the sum of 12 digits, 12 is the sum of 75 digits
    counts = [0] * 10
    for v in s:
        v = int(v)
        counts[v] += 1
    
    for xsum in range(1,1000000000000):
        counts2 = [0] * 10 # count of all subsequence digits used
        term = xsum
        while term > 9:
            nsum = sum(int(x) for x in str(term))
            for d in str(term):
                d = int(d)
                counts2[d] += 1
            term = nsum
        counts2[term] += 1

        if any(counts2[i] > counts[i] for i in range(10)):
            continue
        
        remainDigits = [counts[i] - counts2[i] for i in range(10)]
        firstSum = 0
        for i in range(10):
            cnt = remainDigits[i]
            firstSum += i * cnt
        if firstSum != xsum:
            continue
        if not firstSum:
            continue
        # print(f'xsum is a valid digit sum: {xsum}')
        # print(f'remain digits: {remainDigits}')

        # res = []
        term1 = []
        for i in range(9, -1, -1):
            term1.append(remainDigits[i] * str(i))
        term1 = [str(x) for x in term1]
        if not term1:
            continue
        term1 = ''.join(term1)
        # print(f'{term1=}')

        # res.append(term1)
        res = [term1]
        term = sum(int(x) for x in term1)
        while term > 9:
            res.append(str(term))
            dsum = sum(int(x) for x in str(term))
            term = dsum
        res.append(str(term))
        print(''.join(res))
        return
                

t = int(input())
for _ in range(t):
    solve()