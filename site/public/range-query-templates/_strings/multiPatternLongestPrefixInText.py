# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/strings/multiPatternLongestPrefixInText.py

from random import getrandbits

# list of size len(patterns): res[i] = longest L such that patterns[i][:L] appears somewhere in text (0 if none)
# text and patterns can be any mix of str / list / tuple holding hashable items (ints, chars, tuples, ...)
# multiPatternLongestPrefixInText("xabcaby", ["abd", "cab", "zz"]) -> [2, 3, 0]
# multiPatternLongestPrefixInText([-1, 2, -1, 5], [[2, -1, 2], [5, 9]]) -> [2, 1]
# O(n + m) expected time, O(n) space (n = len(text), m = total pattern length)
def multiPatternLongestPrefixInText(text, patterns):
    salt = getrandbits(62)

    def key(x):  # ints (also inside tuples) get a random salt so crafted inputs can't make the dicts collide
        if type(x) is int:
            return x ^ salt
        if type(x) is tuple:
            return tuple(map(key, x))
        return x  # str hashing is already randomized per run

    text = list(map(key, text))
    patterns = [list(map(key, pattern)) for pattern in patterns]
    # suffix automaton of text: each state is a group of substrings sharing their end positions, with lengths in (length[link], length]
    nxt = [{}]
    link = [-1]
    length = [0]
    last = 0
    for c in text:
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
    # walk each pattern in from the start: it stays inside the automaton exactly while its prefix appears in text
    res = []
    for pattern in patterns:
        state = 0
        matched = 0
        for c in pattern:
            nextState = nxt[state].get(c)
            if nextState is None:
                break
            state = nextState
            matched += 1
        res.append(matched)
    return res
