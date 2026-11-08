# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/strings/multiPatternMatches.py

from random import getrandbits

# list of size len(patterns): res[k] = every index i where text[i...] matches patterns[k], ascending (overlaps included, Aho-Corasick)
# an empty pattern matches at every i in 0..len(text); duplicate patterns each get their own list
# text and patterns can be any mix of str / list / tuple holding hashable items (ints, chars, tuples, ...)
# multiPatternMatches("ababa", ["aba", "b", "ab", "zz"]) -> [[0, 2], [1, 3], [0, 2], []]
# multiPatternMatches([-1, 2, -1, 2], [[-1, 2], [2]]) -> [[0, 2], [1, 3]]
# O(n + m + n * sqrt(m)) expected time (m = total pattern length), worst case when the output is huge: patterns of the same length are
# different, so together they match at most n indices, and total length m allows at most about sqrt(2m) different lengths,
# so there are at most n * sqrt(2m) matches (duplicate patterns each get their own copy); use multiPatternCounts for just counts
def multiPatternMatches(text, patterns):
    salt = getrandbits(62)

    def key(x):  # ints (also inside tuples) get a random salt so crafted inputs can't make the dicts collide
        if type(x) is int:
            return x ^ salt
        if type(x) is tuple:
            return tuple(map(key, x))
        return x  # str hashing is already randomized per run

    text = list(map(key, text))
    patterns = [list(map(key, pattern)) for pattern in patterns]
    # trie of the patterns; fail[node] = node of the longest proper suffix of node's path that is also a trie path
    children = [{}]
    nodeOf = []
    for pattern in patterns:
        node = 0
        for c in pattern:
            child = children[node].get(c)
            if child is None:
                child = len(children)
                children[node][c] = child
                children.append({})
            node = child
        nodeOf.append(node)
    isEnd = [False] * len(children)
    for k in range(len(patterns)):
        if nodeOf[k]:
            isEnd[nodeOf[k]] = True
    fail = [0] * len(children)
    endLink = [0] * len(children)  # nearest node down the fail chain where some pattern ends (0 = none)
    order = [0]
    for node in order:
        for c, child in children[node].items():
            if node:
                f = fail[node]
                while f and c not in children[f]:
                    f = fail[f]
                fail[child] = children[f].get(c, 0)
            endLink[child] = fail[child] if isEnd[fail[child]] else endLink[fail[child]]
            order.append(child)
    # ends[node] = every text index where the pattern ending at node ends
    ends = [[] for _ in range(len(children))]
    node = 0
    for i, c in enumerate(text):
        while node and c not in children[node]:
            node = fail[node]
        node = children[node].get(c, 0)
        out = node if isEnd[node] else endLink[node]
        while out:
            ends[out].append(i)
            out = endLink[out]
    res = []
    for k, pattern in enumerate(patterns):
        m = len(pattern)
        res.append([e - m + 1 for e in ends[nodeOf[k]]] if m else list(range(len(text) + 1)))
    return res
