# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/strings/DoubleEndedEertree.py

from random import getrandbits

# Palindromic tree (eertree) that grows at both ends. A palindrome's longest palindromic suffix is also its longest
# palindromic prefix, so one set of links serves both sides; it tracks the longest palindromic suffix and prefix of the
# whole sequence. Only whole-sequence queries: prepending changes the answers at existing positions.
# works on a str, list or tuple holding any hashable items (ints, chars, tuples, ...)
# et = DoubleEndedEertree("aba")
# et = DoubleEndedEertree([-1, 2, -1])
# et = DoubleEndedEertree()   # empty, then append / appendLeft
class DoubleEndedEertree:
    # O(n) expected time, O(n) space
    def __init__(self, arrOrString=()):
        self._salt = getrandbits(62)
        self.front = []  # the items before the original start, nearest last: seq = front[::-1] + back
        self.back = []
        self.palLen = [-1, 0]  # node 0 = the imaginary length -1 root, node 1 = the empty palindrome
        self.palLink = [0, 0]  # longest proper palindromic suffix (= longest proper palindromic prefix)
        self.nxt = [{}, {}]  # nxt[node][x] = the palindrome x + node + x
        self.sufNode = 1  # longest palindromic suffix of the whole sequence
        self.preNode = 1  # longest palindromic prefix of the whole sequence
        # @if numPalsTotal numPalsEndingAtCurrentR numPalsStartingAtCurrentL
        self.depth = [0, 0]  # depth[node] = how many palindromes are suffixes of node (itself included)
        # @endif
        # @if numPalsTotal
        self.totalPals = 0
        # @endif
        # @if longestPal
        self.longest = 0
        # @endif
        for x in arrOrString:
            self._append(x)

    def _key(self, x):  # ints (also inside tuples) get a random salt so crafted inputs can't make the dicts collide
        if type(x) is int:
            return x ^ self._salt
        if type(x) is tuple:
            return tuple(map(self._key, x))
        return x  # str hashing is already randomized per run

    def _get(self, i):
        front = self.front
        return front[len(front) - 1 - i] if i < len(front) else self.back[i - len(front)]

    # the node x + cur + x, made if new (x salted); fits(t) says whether x + t + x fits on this side (for the new node's
    # link)
    def _child(self, cur, x, fits):
        palLen, palLink, nxt = self.palLen, self.palLink, self.nxt
        node = nxt[cur].get(x)
        if node is None:
            node = len(palLen)
            palLen.append(palLen[cur] + 2)
            if palLen[node] == 1:
                link = 1
            else:
                t = palLink[cur]
                while not fits(t):
                    t = palLink[t]
                link = nxt[t][x]
            palLink.append(link)
            nxt.append({})
            nxt[cur][x] = node
            # @if numPalsTotal numPalsEndingAtCurrentR numPalsStartingAtCurrentL
            self.depth.append(self.depth[link] + 1)
            # @endif
            # @if longestPal
            self.longest = max(self.longest, palLen[node])
            # @endif
        return node

    def _append(self, x):
        self.back.append(x)
        n = len(self.front) + len(self.back)
        i = n - 1
        palLen, get = self.palLen, self._get

        def fits(t):  # x + t + x as a suffix: the item before suffix t is x
            j = i - palLen[t] - 1
            return j >= 0 and get(j) == x

        cur = self.sufNode
        while not fits(cur):
            cur = self.palLink[cur]
        node = self.sufNode = self._child(cur, self._key(x), fits)
        if palLen[node] == n:  # the whole sequence is a palindrome
            self.preNode = node
        # @if numPalsTotal
        self.totalPals += self.depth[node]  # every palindrome ending at the new item
        # @endif

    # @if append
    # O(1) amortized expected -- adds x to the end
    def append(self, x):
        self._append(x)

    # @endif
    # @if appendLeft
    # O(1) amortized expected -- adds x to the front
    def appendLeft(self, x):
        self.front.append(x)
        n = len(self.front) + len(self.back)
        palLen, get = self.palLen, self._get

        def fits(t):  # x + t + x as a prefix: the item after prefix t is x
            j = palLen[t] + 1
            return j < n and get(j) == x

        cur = self.preNode
        while not fits(cur):
            cur = self.palLink[cur]
        node = self.preNode = self._child(cur, self._key(x), fits)
        if palLen[node] == n:
            self.sufNode = node
        # @if numPalsTotal
        self.totalPals += self.depth[node]  # every palindrome starting at the new item
        # @endif

    # @endif
    # @if longestPalEndingAtCurrentR
    # O(1) -- length of the longest palindrome ending at the current right end (0 if empty)
    def longestPalEndingAtCurrentR(self):
        return self.palLen[self.sufNode]

    # @endif
    # @if longestPalStartingAtCurrentL
    # O(1) -- length of the longest palindrome starting at the current left end (0 if empty)
    def longestPalStartingAtCurrentL(self):
        return self.palLen[self.preNode]

    # @endif
    # @if numDistinctPals
    # O(1) -- how many distinct palindromic substrings the sequence has, at most n
    def numDistinctPals(self):
        return len(self.palLen) - 2

    # @endif
    # @if numPalsTotal
    # O(1) -- total palindromic substrings counted with multiplicity ("aa" has 3: a, a, aa)
    def numPalsTotal(self):
        return self.totalPals

    # @endif
    # @if longestPal
    # O(1) -- length of the longest palindromic substring (0 if empty)
    def longestPal(self):
        return self.longest

    # @endif

    # @if numPalsEndingAtCurrentR
    # O(1) -- how many palindromic substrings end at the current right end
    def numPalsEndingAtCurrentR(self):
        return self.depth[self.sufNode]

    # @endif
    # @if numPalsStartingAtCurrentL
    # O(1) -- how many palindromic substrings start at the current left end
    def numPalsStartingAtCurrentL(self):
        return self.depth[self.preNode]

    # @endif
