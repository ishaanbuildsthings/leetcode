# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/strings/longestCommonSubstring.py

from random import getrandbits

# longest contiguous run appearing in both a and b, as (length, startInA, startInB): a[startInA : startInA + length] == b[startInB : startInB + length]
# ties go to the earliest start in b, then the earliest start in a; no common item -> (0, 0, 0)
# a and b can be any mix of str / list / tuple holding hashable items (ints, chars, tuples, ...)
# longestCommonSubstring("xabcdy", "zzbcdq") -> (3, 2, 2)   # "bcd"
# longestCommonSubstring([5, -1, 2, 7], [-1, 2, 9]) -> (2, 1, 0)   # [-1, 2]
# O(n + m) expected time, O(n) space (n = len(a), m = len(b))
def longestCommonSubstring(a, b):
    salt = getrandbits(62)

    def key(x):  # ints (also inside tuples) get a random salt so crafted inputs can't make the dicts collide
        if type(x) is int:
            return x ^ salt
        if type(x) is tuple:
            return tuple(map(key, x))
        return x  # str hashing is already randomized per run

    a = list(map(key, a))
    b = list(map(key, b))
    # suffix automaton of a; firstEnd[state] = earliest index in a where that state's substrings end
    nxt = [{}]
    link = [-1]
    length = [0]
    firstEnd = [-1]
    last = 0
    for i, c in enumerate(a):
        cur = len(nxt)
        nxt.append({})
        length.append(length[last] + 1)
        link.append(0)
        firstEnd.append(i)
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
                firstEnd.append(firstEnd[q])
                while p != -1 and nxt[p].get(c) == q:
                    nxt[p][c] = clone
                    p = link[p]
                link[q] = clone
                link[cur] = clone
        last = cur
    # walk b through it, keeping the longest suffix of b[..j] that appears in a
    state = 0
    matched = 0
    best = bestState = bestEndB = 0
    for j, c in enumerate(b):
        while state and c not in nxt[state]:
            state = link[state]
            matched = length[state]
        if c in nxt[state]:
            state = nxt[state][c]
            matched += 1
        if matched > best:
            best, bestState, bestEndB = matched, state, j
    if best == 0:
        return (0, 0, 0)
    return (best, firstEnd[bestState] - best + 1, bestEndB - best + 1)
