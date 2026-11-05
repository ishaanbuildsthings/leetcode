# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/next-permutation/NextPermutationSteps.py

# The arrangement of sequence steps later (steps = 1: the next one; a new list, or a string for a string), or None if
# fewer than steps arrangements come after it
# sequence: a list or a string of values that compare with each other: negatives, floats, chars, tuples ok
def nextPermutation(sequence, steps):
    n = len(sequence)
    if steps == 0:
        return "".join(sequence) if isinstance(sequence, str) else list(sequence)

    vals, rk = [], [0] * n
    for i in sorted(range(n), key=lambda i: sequence[i]):
        if not vals or vals[-1] < sequence[i]:
            vals.append(sequence[i])
        rk[i] = len(vals) - 1
    d = len(vals)

    cap = (steps + 1) * (n + 1)
    cnt = [0] * d
    fen = [0] * (d + 1)
    arrangements, after, afterNext = 1, 0, 0
    s = n
    while after < steps:
        if s == 0:
            return None
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

    out = list(sequence[:s]) + [vals[w]] + [vals[k] for k in rest]
    return "".join(out) if isinstance(sequence, str) else out
