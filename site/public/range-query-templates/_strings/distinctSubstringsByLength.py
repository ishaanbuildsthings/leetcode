# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/strings/distinctSubstringsByLength.py

from random import getrandbits

# list of size n + 1: res[L] = number of distinct contiguous substrings of length L (res[0] = 0, the empty one isn't
# counted)
# works on a str, list or tuple holding any hashable items (ints, chars, tuples, ...)
# distinctSubstringsByLength("abab") -> [0, 2, 2, 2, 1]   # {a, b}, {ab, ba}, {aba, bab}, {abab}
# distinctSubstringsByLength([-1, 2, -1]) -> [0, 2, 2, 1]
# O(n) expected time and space
def distinctSubstringsByLength(arrOrString):
    salt = getrandbits(62)

    def key(x):  # ints (also inside tuples) get a random salt so crafted inputs can't make the dicts collide
        if type(x) is int:
            return x ^ salt
        if type(x) is tuple:
            return tuple(map(key, x))
        return x  # str hashing is already randomized per run

    arrOrString = list(map(key, arrOrString))
    n = len(arrOrString)
    # suffix automaton: each state is a group of substrings sharing their end positions, with lengths in (length[link],
    # length]
    nxt = [{}]
    link = [-1]
    length = [0]
    last = 0
    for c in arrOrString:
        cur = len(nxt)
        nxt.append({})
        length.append(length[last] + 1)
        link.append(0)
        p = last
        while p != -1 and c not in nxt[p]:
            nxt[p][c] = cur
            p = link[p]
        if p != -1:
            q = nxt[p][c]
            if length[p] + 1 == length[q]:
                link[cur] = q
            else:
                clone = len(nxt)
                nxt.append(dict(nxt[q]))
                length.append(length[p] + 1)
                link.append(link[q])
                while p != -1 and nxt[p].get(c) == q:
                    nxt[p][c] = clone
                    p = link[p]
                link[q] = clone
                link[cur] = clone
        last = cur
    # each state adds one distinct substring of every length in (length[link], length]: difference array
    diff = [0] * (n + 2)
    for state in range(1, len(nxt)):
        diff[length[link[state]] + 1] += 1
        diff[length[state] + 1] -= 1
    res = [0] * (n + 1)
    running = 0
    for L in range(1, n + 1):
        running += diff[L]
        res[L] = running
    return res
