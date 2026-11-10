# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/strings/DequeEertree.py

# Palindromic tree (eertree) over a deque: append, appendLeft, pop, popLeft.
# Works on a str, or a list / tuple of hashable items (ints incl. negatives, tuples, strings, ...).
# et = DequeEertree("abaab")
# et = DequeEertree([-1, 2, -1])
# et = DequeEertree()
#
# n = current length. Pops follow Wang, Yang, Zhu "Double-Ended Palindromic Trees" (surface recording).
# A surface is a palindrome occurrence that isn't a prefix or suffix of a longer palindrome occurrence.
# A palindrome occurs iff it's a surface or a link-tree ancestor of one, so a node is alive while
# (its surface count) + (its alive link children) > 0. The longest palindrome at either end is always
# a surface, and a position has at most one surface starting / ending there, kept in preSurf / sufSurf.
# Popping the right end kills its surface t; the copy of link(t) at the front of t becomes a surface
# unless some surface already ends where that copy ends. Pushing is the mirror. So every op changes O(1)
# surfaces and creates or deletes at most one node. Positions are global indices into a ring buffer, so nothing shifts
# on appendLeft. A push has to find the longest palindrome at that end that the new item extends, without amortization
# (pops would break it):
# @if quickLinks
# quick links skip a whole run of equal-difference palindromic suffixes per jump, so O(log n) jumps worst case.
# @endif
# @if itemLinks
# every palindrome keeps a link per item (alphabet = number of distinct items), so it's one lookup, but making a
# palindrome copies its suffix link's links: O(alphabet) time and memory per palindrome.
# @endif
# @if persistentLinks
# every palindrome's per-item links are a persistent array (a binary trie over item ids) that shares all but one path
# with its suffix link's, so O(log alphabet) per push; trie nodes nothing points to any more are reused, so memory
# stays O(size * log alphabet).
# @endif

import random


class DequeEertree:
    def __init__(self, arrOrString=()):
        self._salt = random.getrandbits(62)
        # node 0: imaginary root (len -1), node 1: empty root (len 0); 0 in preSurf / sufSurf means "no surface"
        self._lens = [-1, 0]
        self._link = [0, 0]
        # @if quickLinks
        self._quick = [0, 0]
        # @endif
        # @if itemLinks
        # itemLink[node][x] = longest proper palindromic suffix of node with x right before it
        self._itemLink = [{}, {}]
        # @endif
        # @if persistentLinks
        self._idOf = {}
        self._trieLeft, self._trieRight, self._trieVal, self._trieRefs = [0], [0], [0], [0]  # trie node 0 = empty
        self._trieFree = []
        self._linkRoot, self._linkDepth = [0, 0], [0, 0]
        # @endif
        self._diff = [None, None]  # node[len(link)], the item right after the copy of link at the front of node
        self._cnt = [0, 0]  # surfaces of this palindrome
        self._kids = [0, 0]  # alive nodes whose link is this one
        self._par = [0, 0]  # node = edge + par + edge
        self._edge = [None, None]  # salted
        # @if numPalsTotal numPalsEndingAtCurrentR numPalsStartingAtCurrentL
        self._depth = [0, 0]  # palindromic suffixes of node, itself included
        # @endif
        # @if numPalsTotal
        self._total = 0
        # @endif
        # @if numDistinctPals
        self._distinct = 0
        # @endif
        # @if longestPal
        # live palindromes per length, and the longest live even / odd length. A palindrome only dies while its inner
        # palindrome (2 shorter) is still around, so when the longest length runs out, the next longest is 2 shorter
        self._lenCount = [0]
        self._longestOfParity = [0, -1]
        # @endif
        self._free = []
        self._to = {}
        self._mask = 7
        self._data = [None] * 8
        self._preSurf = [0] * 8
        self._sufSurf = [0] * 8
        self._l = 0
        self._r = 0
        for x in arrOrString:
            self.append(x)

    def __len__(self):
        return self._r - self._l

    def _salted(self, x):
        if isinstance(x, int):
            return x ^ self._salt
        if isinstance(x, tuple):
            return tuple(self._salted(y) for y in x)
        return x

    def _grow(self):
        oldMask = self._mask
        newMask = oldMask * 2 + 1
        data = [None] * (newMask + 1)
        preSurf = [0] * (newMask + 1)
        sufSurf = [0] * (newMask + 1)
        for pos in range(self._l, self._r):
            data[pos & newMask] = self._data[pos & oldMask]
            preSurf[pos & newMask] = self._preSurf[pos & oldMask]
            sufSurf[pos & newMask] = self._sufSurf[pos & oldMask]
        self._data, self._preSurf, self._sufSurf, self._mask = data, preSurf, sufSurf, newMask

    # longest palindromic suffix (step = -1) or prefix (step = 1) of the current string that is
    # preceded / followed by x, where x is already written at pos; lo..hi is the valid range
    def _walk(self, cur, x, key, pos, step, lo, hi):
        lens, data, m = self._lens, self._data, self._mask
        # @if quickLinks
        while True:
            ln = lens[cur]
            if ln == -1:
                return cur
            j = pos + step * (ln + 1)
            if lo <= j <= hi and data[j & m] == x:
                return cur
            if ln == 0:
                return 0
            if self._diff[cur] == x:
                return self._link[cur]
            cur = self._quick[cur]
        # @endif
        # @if itemLinks persistentLinks
        ln = lens[cur]
        if ln == -1:
            return cur
        j = pos + step * (ln + 1)
        if lo <= j <= hi and data[j & m] == x:
            return cur
        # @endif
        # @if itemLinks
        return self._itemLink[cur].get(key, 0)  # 0 = the imaginary root, which fits any x
        # @endif
        # @if persistentLinks
        item = self._idOf.get(key)
        return 0 if item is None else self._trieGet(self._linkRoot[cur], self._linkDepth[cur], item)
        # @endif

    # @if persistentLinks
    def _trieGet(self, root, depth, item):
        if item >> depth:
            return 0
        left, right = self._trieLeft, self._trieRight
        for bit in range(depth - 1, -1, -1):
            root = right[root] if item >> bit & 1 else left[root]
            if not root:
                return 0
        return self._trieVal[root]

    def _trieNode(self, left, right, val):  # a trie node holding a reference to each child
        refs = self._trieRefs
        if left:
            refs[left] += 1
        if right:
            refs[right] += 1
        if self._trieFree:
            t = self._trieFree.pop()
            self._trieLeft[t], self._trieRight[t], self._trieVal[t], refs[t] = left, right, val, 0
            return t
        self._trieLeft.append(left)
        self._trieRight.append(right)
        self._trieVal.append(val)
        refs.append(0)
        return len(refs) - 1

    def _trieRelease(self, t):  # drop one reference to t, freeing whatever nothing points to any more
        refs, stack = self._trieRefs, [t]
        while stack:
            t = stack.pop()
            if t:
                refs[t] -= 1
                if not refs[t]:
                    stack.append(self._trieLeft[t])
                    stack.append(self._trieRight[t])
                    self._trieFree.append(t)

    # a new version with [item] = val, sharing everything off the one path it copies: O(log alphabet). The caller owns
    # one reference to the returned root
    def _trieSet(self, root, depth, item, val):
        left, right, vals, refs = self._trieLeft, self._trieRight, self._trieVal, self._trieRefs
        top = root
        while item >> depth:  # too few bits for this item: the old trie becomes the left half of a taller one
            if root:
                root = self._trieNode(root, 0, 0)
            depth += 1
        newRoot = cur = self._trieNode(left[root], right[root], vals[root])
        for bit in range(depth - 1, -1, -1):
            goRight = item >> bit & 1
            child = right[cur] if goRight else left[cur]
            copy = self._trieNode(left[child], right[child], vals[child])
            if goRight:
                right[cur] = copy
            else:
                left[cur] = copy
            refs[copy] += 1
            if child:
                self._trieRelease(child)
            cur = copy
        vals[cur] = val
        refs[newRoot] += 1
        if root != top:  # the taller wrappers were only scaffolding
            refs[root] += 1
            self._trieRelease(root)
        return newRoot, depth

    # @endif

    # node for x + str(cur) + x, created if missing; start = first index of its occurrence
    def _child(self, cur, x, key, pos, step, lo, hi):
        node = self._to.get((cur, key))
        if node is not None:
            return node
        lens, link = self._lens, self._link
        ln = lens[cur] + 2
        if ln == 1:
            lk = 1
        else:
            lk = self._to[(self._walk(link[cur], x, key, pos, step, lo, hi), key)]
        start = pos if step == 1 else pos - ln + 1
        diff = self._data[(start + lens[lk]) & self._mask]
        # @if quickLinks
        if lens[lk] <= 0:
            quick = 0
        elif self._diff[lk] == diff:
            quick = self._quick[lk]
        else:
            quick = link[lk]
        # @endif
        # @if itemLinks
        links = dict(self._itemLink[lk])  # node's proper suffixes are lk and lk's proper suffixes
        links[self._salted(diff)] = lk  # diff is the item right before lk inside node
        # @endif
        # @if persistentLinks
        root, depth = self._trieSet(self._linkRoot[lk], self._linkDepth[lk], self._idOf[self._salted(diff)], lk)
        # @endif
        if self._free:
            node = self._free.pop()
            lens[node] = ln
            link[node] = lk
            # @if quickLinks
            self._quick[node] = quick
            # @endif
            # @if itemLinks
            self._itemLink[node] = links
            # @endif
            # @if persistentLinks
            self._linkRoot[node], self._linkDepth[node] = root, depth
            # @endif
            self._diff[node] = diff
            self._cnt[node] = 0
            self._kids[node] = 0
            self._par[node] = cur
            self._edge[node] = key
            # @if numPalsTotal numPalsEndingAtCurrentR numPalsStartingAtCurrentL
            self._depth[node] = self._depth[lk] + 1
            # @endif
        else:
            node = len(lens)
            lens.append(ln)
            link.append(lk)
            # @if quickLinks
            self._quick.append(quick)
            # @endif
            # @if itemLinks
            self._itemLink.append(links)
            # @endif
            # @if persistentLinks
            self._linkRoot.append(root)
            self._linkDepth.append(depth)
            # @endif
            self._diff.append(diff)
            self._cnt.append(0)
            self._kids.append(0)
            self._par.append(cur)
            self._edge.append(key)
            # @if numPalsTotal numPalsEndingAtCurrentR numPalsStartingAtCurrentL
            self._depth.append(self._depth[lk] + 1)
            # @endif
        self._kids[lk] += 1
        # @if longestPal
        while len(self._lenCount) <= ln:
            self._lenCount.append(0)
        self._lenCount[ln] += 1
        if ln > self._longestOfParity[ln & 1]:
            self._longestOfParity[ln & 1] = ln
        # @endif
        self._to[(cur, key)] = node
        # @if numDistinctPals
        self._distinct += 1
        # @endif
        return node

    # @if pop popLeft
    def _maybeDelete(self, node):
        if self._cnt[node] or self._kids[node]:
            return
        del self._to[(self._par[node], self._edge[node])]
        self._kids[self._link[node]] -= 1
        self._free.append(node)
        # @if itemLinks
        self._itemLink[node] = None
        # @endif
        # @if persistentLinks
        self._trieRelease(self._linkRoot[node])
        self._linkRoot[node] = 0
        # @endif
        # @if numDistinctPals
        self._distinct -= 1
        # @endif
        # @if longestPal
        ln = self._lens[node]
        self._lenCount[ln] -= 1
        if not self._lenCount[ln] and self._longestOfParity[ln & 1] == ln:
            self._longestOfParity[ln & 1] = ln - 2
        # @endif

    # @endif
    # @if quickLinks
    # O(log n) worst case + expected amortized O(1) (hashing, buffer growth). Returns None.
    # @endif
    # @if itemLinks
    # O(alphabet) expected + amortized O(1) buffer growth. Returns None.
    # @endif
    # @if persistentLinks
    # O(log alphabet) expected + amortized O(1) buffer growth. Returns None.
    # @endif
    def append(self, x):
        if self._r - self._l > self._mask:
            self._grow()
        m = self._mask
        pos = self._r
        self._data[pos & m] = x
        self._preSurf[pos & m] = 0
        self._sufSurf[pos & m] = 0
        lo = self._l
        cur = self._sufSurf[(pos - 1) & m] if pos > lo else 1
        key = self._salted(x)
        # @if persistentLinks
        if key not in self._idOf:
            self._idOf[key] = len(self._idOf)
        # @endif
        cur = self._walk(cur, x, key, pos, -1, lo, pos)
        node = self._child(cur, x, key, pos, -1, lo, pos)
        # the surface that started where node starts is now a prefix of node
        start = pos - self._lens[node] + 1
        old = self._preSurf[start & m]
        if old:
            self._cnt[old] -= 1
            self._sufSurf[(start + self._lens[old] - 1) & m] = 0
        self._preSurf[start & m] = node
        self._sufSurf[pos & m] = node
        self._cnt[node] += 1
        self._r = pos + 1
        # @if numPalsTotal
        self._total += self._depth[node]
        # @endif

    # @if appendLeft
    # @if quickLinks
    # O(log n) worst case + expected amortized O(1) (hashing, buffer growth). Returns None.
    # @endif
    # @if itemLinks
    # O(alphabet) expected + amortized O(1) buffer growth. Returns None.
    # @endif
    # @if persistentLinks
    # O(log alphabet) expected + amortized O(1) buffer growth. Returns None.
    # @endif
    def appendLeft(self, x):
        if self._r - self._l > self._mask:
            self._grow()
        m = self._mask
        pos = self._l - 1
        self._data[pos & m] = x
        self._preSurf[pos & m] = 0
        self._sufSurf[pos & m] = 0
        hi = self._r - 1
        cur = self._preSurf[(pos + 1) & m] if pos < hi else 1
        key = self._salted(x)
        # @if persistentLinks
        if key not in self._idOf:
            self._idOf[key] = len(self._idOf)
        # @endif
        cur = self._walk(cur, x, key, pos, 1, pos, hi)
        node = self._child(cur, x, key, pos, 1, pos, hi)
        end = pos + self._lens[node] - 1
        old = self._sufSurf[end & m]
        if old:
            self._cnt[old] -= 1
            self._preSurf[(end - self._lens[old] + 1) & m] = 0
        self._sufSurf[end & m] = node
        self._preSurf[pos & m] = node
        self._cnt[node] += 1
        self._l = pos
        # @if numPalsTotal
        self._total += self._depth[node]
        # @endif

    # @endif
    # @if pop
    # @if quickLinks
    # expected O(1). Removes and returns the last item.
    # @endif
    # @if itemLinks
    # O(alphabet) expected (a deleted palindrome's links are freed). Removes and returns the last item.
    # @endif
    # @if persistentLinks
    # O(log alphabet) expected (a deleted palindrome's trie path is freed). Removes and returns the last item.
    # @endif
    def pop(self):
        if self._r == self._l:
            raise IndexError("pop from an empty DequeEertree")
        m = self._mask
        pos = self._r - 1
        node = self._sufSurf[pos & m]
        start = pos - self._lens[node] + 1
        self._cnt[node] -= 1
        self._preSurf[start & m] = 0
        self._sufSurf[pos & m] = 0
        if self._lens[node] > 1:
            # the copy of link(node) at the front of node is a surface now, unless a surface already ends there
            link = self._link[node]
            end = start + self._lens[link] - 1
            if not self._sufSurf[end & m]:
                self._cnt[link] += 1
                self._preSurf[start & m] = link
                self._sufSurf[end & m] = link
        # @if numPalsTotal
        self._total -= self._depth[node]
        # @endif
        self._maybeDelete(node)
        self._r = pos
        x = self._data[pos & m]
        self._data[pos & m] = None
        return x

    # @endif
    # @if popLeft
    # @if quickLinks
    # expected O(1). Removes and returns the first item.
    # @endif
    # @if itemLinks
    # O(alphabet) expected (a deleted palindrome's links are freed). Removes and returns the first item.
    # @endif
    # @if persistentLinks
    # O(log alphabet) expected (a deleted palindrome's trie path is freed). Removes and returns the first item.
    # @endif
    def popLeft(self):
        if self._r == self._l:
            raise IndexError("pop from an empty DequeEertree")
        m = self._mask
        pos = self._l
        node = self._preSurf[pos & m]
        end = pos + self._lens[node] - 1
        self._cnt[node] -= 1
        self._preSurf[pos & m] = 0
        self._sufSurf[end & m] = 0
        if self._lens[node] > 1:
            link = self._link[node]
            start = end - self._lens[link] + 1
            if not self._preSurf[start & m]:
                self._cnt[link] += 1
                self._preSurf[start & m] = link
                self._sufSurf[end & m] = link
        # @if numPalsTotal
        self._total -= self._depth[node]
        # @endif
        self._maybeDelete(node)
        self._l = pos + 1
        x = self._data[pos & m]
        self._data[pos & m] = None
        return x

    # @endif
    # @if numDistinctPals
    # O(1). Number of distinct non-empty palindromic substrings.
    def numDistinctPals(self):
        return self._distinct

    # @endif
    # @if numPalsTotal
    # O(1). Number of palindromic substrings counted with multiplicity (by position).
    def numPalsTotal(self):
        return self._total

    # @endif
    # @if longestPalEndingAtCurrentR
    # O(1). Length of the longest palindrome ending at the last item, 0 if empty.
    def longestPalEndingAtCurrentR(self):
        if self._r == self._l:
            return 0
        return self._lens[self._sufSurf[(self._r - 1) & self._mask]]

    # @endif
    # @if longestPalStartingAtCurrentL
    # O(1). Length of the longest palindrome starting at the first item, 0 if empty.
    def longestPalStartingAtCurrentL(self):
        if self._r == self._l:
            return 0
        return self._lens[self._preSurf[self._l & self._mask]]
    # @endif

    # @if longestPal
    # O(1). Length of the longest palindromic substring, 0 if empty.
    def longestPal(self):
        return max(self._longestOfParity)

    # @endif

    # @if numPalsEndingAtCurrentR
    # O(1). How many palindromic substrings end at the current right end, 0 if empty.
    def numPalsEndingAtCurrentR(self):
        return self._depth[self._sufSurf[(self._r - 1) & self._mask]] if self._r > self._l else 0

    # @endif
    # @if numPalsStartingAtCurrentL
    # O(1). How many palindromic substrings start at the current left end, 0 if empty.
    def numPalsStartingAtCurrentL(self):
        return self._depth[self._preSurf[self._l & self._mask]] if self._r > self._l else 0

    # @endif
