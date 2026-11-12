# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/strings/multiPatternCounts.py

from random import getrandbits

# list of size len(patterns): res[k] = number of indices i where text[i...] matches patterns[k] (overlaps counted,
# Aho-Corasick) an empty pattern matches at every i in 0..len(text); duplicate patterns each get their own count text
# and patterns can be any mix of str / list / tuple holding hashable items (ints, chars, tuples, ...)
# multiPatternCounts("ababa", ["aba", "b", "ab", "zz"]) -> [2, 2, 2, 0]
# multiPatternCounts([-1, 2, -1, 2], [[-1, 2], [2]]) -> [2, 2]
# O(n + total pattern length) expected time and space
def multiPatternCounts(text, patterns):
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
    fail = [0] * len(children)
    order = [0]  # BFS order: parents before children
    for node in order:
        for c, child in children[node].items():
            if node:
                f = fail[node]
                while f and c not in children[f]:
                    f = fail[f]
                fail[child] = children[f].get(c, 0)
            order.append(child)
    # hits[node] = text positions whose longest trie-path suffix ends at node; then push each count up its fail chain
    hits = [0] * len(children)
    node = 0
    for c in text:
        while node and c not in children[node]:
            node = fail[node]
        node = children[node].get(c, 0)
        hits[node] += 1
    for node in reversed(order):
        if node:
            hits[fail[node]] += hits[node]
    return [hits[nodeOf[k]] if len(patterns[k]) else len(text) + 1 for k in range(len(patterns))]
