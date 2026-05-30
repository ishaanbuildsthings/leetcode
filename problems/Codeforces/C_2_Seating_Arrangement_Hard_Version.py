def solve():
    n, tables, seats = map(int, input().split())
    s = input()

    placedAmbivertsAsExtroverts = 0

    empty = tables
    full = 0
    partials = []
    for i, v in enumerate(s):
        if v == 'A':
            if partials:
                placedAmbivertsAsExtroverts += 1
                partials[-1] += 1
                if partials[-1] == seats:
                    partials.pop()
                    full += 1
            else:
                if empty:
                    partials.append(1)
                    if partials[-1] == seats:
                        partials.pop()
                        full += 1
                    empty -= 1
        elif v == 'E':
            if partials:
                partials[-1] += 1
                if partials[-1] == seats:
                    partials.pop()
                    full += 1
            else:
                if placedAmbivertsAsExtroverts and empty:
                    empty -= 1
                    placedAmbivertsAsExtroverts -= 1
                    partials.append(1)
                    if partials[-1] == seats:
                        partials.pop()
                        full += 1
        elif v == 'I':
            if empty:
                empty -= 1
                partials.append(1)
                if partials[-1] == seats:
                    partials.pop()
                    full += 1
    
    res = full * seats
    res += sum(partials)
    print(res)





t = int(input())
for _ in range(t):
    solve()