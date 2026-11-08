# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/strings/multiPatternLongestPrefixMatches.py

from random import getrandbits

# list of size len(text): res[idx] = longest L such that text[idx : idx + L] is a prefix of some pattern (0 if none)
# text and patterns can be any mix of str / list / tuple holding hashable items (ints, chars, tuples, ...)
# multiPatternLongestPrefixMatches("abcab", ["abd", "bca", "x"]) -> [2, 3, 0, 2, 1]
# multiPatternLongestPrefixMatches([-1, 2, -1, 5], [[-1, 2, -1, 2], [5, 9]]) -> [3, 0, 1, 1]
# O(n + m) expected time, O(m) space (n = len(text), m = total pattern length)
def multiPatternLongestPrefixMatches(text, patterns):
    salt = getrandbits(62)

    def key(x):  # ints (also inside tuples) get a random salt so crafted inputs can't make the dicts collide
        if type(x) is int:
            return x ^ salt
        if type(x) is tuple:
            return tuple(map(key, x))
        return x  # str hashing is already randomized per run

    text = list(map(key, text))
    patterns = [list(map(key, pattern)) for pattern in patterns]
    # reversed, "text[idx : idx + L] is a prefix of a pattern" becomes "the reversed text's run of length L ending at
    # mirrored idx is a suffix of a reversed pattern": suffix automaton over every reversed pattern
    nxt = [{}]
    link = [-1]
    length = [0]

    def extend(last, c):
        if c in nxt[last]:
            q = nxt[last][c]
            if length[last] + 1 == length[q]:
                return q
            clone = len(nxt)
            nxt.append(dict(nxt[q]))
            length.append(length[last] + 1)
            link.append(link[q])
            p = last
            while p != -1 and nxt[p].get(c) == q:
                nxt[p][c] = clone
                p = link[p]
            link[q] = clone
            return clone
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
        return cur

    ends = []
    for pattern in patterns:
        last = 0
        for c in reversed(pattern):
            last = extend(last, c)
        ends.append(last)
    # isSuffix[state]: its runs are suffixes of some reversed pattern (states on the link path up from a pattern's end)
    isSuffix = [False] * len(nxt)
    isSuffix[0] = True
    for state in ends:
        while not isSuffix[state]:
            isSuffix[state] = True
            state = link[state]
    # nearestSuffix[state] = closest state at or above it (by links) whose runs are suffixes
    byLength = [[] for _ in range(max(length) + 1)]  # counting sort: shorter states (closer to the root) first
    for state in range(len(nxt)):
        byLength[length[state]].append(state)
    order = [state for bucket in byLength for state in bucket]
    nearestSuffix = [0] * len(nxt)
    for state in order:
        nearestSuffix[state] = state if isSuffix[state] else nearestSuffix[link[state]]
    n = len(text)
    res = [0] * n
    state = matched = 0
    for pos in range(n - 1, -1, -1):  # walk the reversed text
        c = text[pos]
        while state and c not in nxt[state]:
            state = link[state]
            matched = length[state]
        if c in nxt[state]:
            state = nxt[state][c]
            matched += 1
        res[pos] = matched if isSuffix[state] else length[nearestSuffix[state]]
    return res
