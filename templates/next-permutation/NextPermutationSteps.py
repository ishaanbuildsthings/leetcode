# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/next-permutation/NextPermutationSteps.py

# Can pass in a list of any comparable values (ints, longs, negatives, chars) or a string, and a # of steps which can be very large
# Returns a new permutation in the same format, that many steps forward, with looping behavior
def nextPermutation(arr, steps):
    n = len(arr)
    if steps == 0:
        return arr[:]  # (a string is returned as is)

    vals, rk = [], [0] * n
    for i in sorted(range(n), key=lambda i: arr[i]):
        if not vals or vals[-1] < arr[i]:
            vals.append(arr[i])
        rk[i] = len(vals) - 1
    d = len(vals)

    cap = (steps + 1) * (n + 1)
    cnt = [0] * d
    fen = [0] * (d + 1)
    arrangements, after, afterNext = 1, 0, 0
    s = n
    while after < steps:
        if s == 0:  # fewer than steps arrangements come after arr: loop around to the smallest and count on from there
            r = (steps - after - 1) % arrangements  # arrangements: how many there are in all (or more than steps)
            first = sorted(arr)
            return nextPermutation("".join(first) if isinstance(arr, str) else first, r)
        s -= 1
        v, length = rk[s], n - s
        cnt[v] += 1
        i = v + 1
        while i <= d:
            fen[i] += 1
            i += i & -i
        atMost, i = 0, v + 1
        while i > 0:
            atMost += fen[i]
            i -= i & -i
        arrangements = min(cap, arrangements * length // cnt[v])
        afterNext = after
        after = min(cap, after + arrangements * (length - atMost) // length)

    v, length = rk[s], n - s
    r = steps - afterNext - 1
    w = v + 1
    while True:
        if cnt[w]:
            c = arrangements * cnt[w] // length
            if r < c:
                break
            r -= c
        w += 1

    rest = sorted(rk[s:])
    rest.remove(w)
    m = t = len(rest)
    tc = [0] * d
    tailCount = 1
    while tailCount <= r:
        t -= 1
        tc[rest[t]] += 1
        tailCount = tailCount * (m - t) // tc[rest[t]]
    lo = rest[t] if t < m else 0
    for pos in range(t, m):
        x = lo
        while True:
            if tc[x]:
                c = tailCount * tc[x] // (m - pos)
                if r < c:
                    rest[pos] = x
                    tc[x] -= 1
                    tailCount = c
                    break
                r -= c
            x += 1

    out = list(arr[:s]) + [vals[w]] + [vals[k] for k in rest]
    return "".join(out) if isinstance(arr, str) else out
