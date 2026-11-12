# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/strings/Eertree.py

from random import getrandbits

# Palindromic tree (eertree) over a sequence: every distinct palindromic substring is one node inside, but every method
# below talks in indices into the sequence. A sequence of length n has at most n distinct palindromic substrings.
# works on a str, list or tuple holding any hashable items (ints, chars, tuples, ...)
# et = Eertree("abaab")
# et = Eertree([-1, 2, -1])
# et = Eertree()   # empty, then append
class Eertree:
    # @if append+pop
    # @if quickLinks
    # O(n log n) expected time, O(n) space (append finds its palindrome through quick links, so it stays fast after
    # pops)
    # @endif
    # @if itemLinks
    # O(n * alphabet) expected time and space, alphabet = number of distinct items (every palindrome keeps a link per
    # item)
    # @endif
    # @if persistentLinks
    # O(n log alphabet) expected time and space, alphabet = number of distinct items (every palindrome's links are a
    # persistent array)
    # @endif
    # @else
    # O(n) expected time, O(n) space
    # @endif
    def __init__(self, arrOrString=()):
        self._salt = getrandbits(62)
        self.seq = []
        self.palLen = [-1, 0]  # node 0 = the imaginary length -1 root, node 1 = the empty palindrome
        self.palLink = [0, 0]  # longest proper palindromic suffix
        self.nxt = [{}, {}]  # nxt[node][x] = the palindrome x + node + x
        self.sufNode = []  # sufNode[r] = longest palindrome ending at r
        # @if numPalsEndingAtR numPalsTotal numPalsEndingAtEachR numPalsEndingAtCurrentR numPalsStartingAtCurrentL
        self.depth = [0, 0]  # depth[node] = how many palindromes are suffixes of node (itself included)
        # @endif
        # @if distinctPalsWithCounts
        self.firstEnd = [-1, -1]
        # @endif
        # @if minPalPartition
        self.diff = [0, 0]
        self.seriesLink = [0, 0]
        # @endif
        # @if append+pop+quickLinks
        self.quick = [0, 0]  # quick link: lets append skip runs of suffixes preceded by the same item
        # @endif
        # @if append+pop+itemLinks
        self.itemLink = [{}, {}]  # itemLink[node][x] = longest proper palindromic suffix of node with x right before it
        # @endif
        # @if append+pop+persistentLinks
        # the same links as a persistent array per palindrome: item -> id, then a binary trie over the id's bits where a
        # new palindrome copies only the O(log alphabet) trie nodes on one path of its suffix link's trie
        self.idOf = {}
        self.trieLeft, self.trieRight, self.trieVal = [0], [0], [0]  # trie node 0 = empty
        self.linkRoot, self.linkDepth = [0, 0], [0, 0]
        self.trieSizeBefore = [0, 0]  # trie size before each palindrome was made, to undo it on pop
        # @endif
        # @if pop
        self.parent = [0, 0]  # node = x + parent + x
        self.createdAt = []  # createdAt[r] = whether position r made a new node
        # @endif
        # @if numDistinctPalsInPrefixEndingAtR numDistinctPalsInPrefixEndingAtEachR
        self.distinctInPrefix = []
        # @endif
        # @if longestPalStartingAtCurrentL
        self.palPrefixLen = []  # palPrefixLen[r] = longest palindromic prefix of seq[0..r]
        # @endif
        # @if numPalsStartingAtCurrentL
        self.palPrefixNode = []  # palPrefixNode[r] = node of the longest palindromic prefix of seq[0..r]
        # @endif
        # @if longestPal
        self.longestUpTo = []  # longestUpTo[r] = length of the longest palindrome in seq[0..r]
        # @endif
        # @if numPalsTotal
        self.totalPals = 0
        # @endif
        # @if rightmostRForPalStartingAtL rightmostRForPalStartingAtEachL
        self._revLens = None
        # @endif
        for x in arrOrString:
            self._append(x)

    def _key(self, x):  # ints (also inside tuples) get a random salt so crafted inputs can't make the dicts collide
        if type(x) is int:
            return x ^ self._salt
        if type(x) is tuple:
            return tuple(map(self._key, x))
        return x  # str hashing is already randomized per run

    # @if append+pop
    # longest palindromic suffix of seq[0..i-1], at or below node, with x (salted: k) right before it
    def _findPrecededBy(self, node, i, x, k):
        seq, palLen = self.seq, self.palLen
        j = i - palLen[node] - 1
        if j >= 0 and seq[j] == x:
            return node
        # @if quickLinks
        palLink, quick = self.palLink, self.quick
        while True:
            link = palLink[node]
            if seq[i - palLen[link] - 1] == x:
                return link
            node = quick[node]  # every suffix between link and quick[node] has the same item before it as link does
            j = i - palLen[node] - 1
            if j >= 0 and seq[j] == x:
                return node
        # @endif
        # @if itemLinks
        return self.itemLink[node].get(k, 0)  # 0 = the imaginary root, which fits any x
        # @endif
        # @if persistentLinks
        item = self.idOf.get(k)
        return 0 if item is None else self._trieGet(self.linkRoot[node], self.linkDepth[node], item)
        # @endif

    # @endif
    # @if append+pop+persistentLinks
    def _trieGet(self, root, depth, item):
        if item >> depth:
            return 0
        left, right = self.trieLeft, self.trieRight
        for bit in range(depth - 1, -1, -1):
            root = right[root] if item >> bit & 1 else left[root]
            if not root:
                return 0
        return self.trieVal[root]

    # a new version of the trie with [item] = val, sharing everything off the one path it copies: O(log alphabet)
    def _trieSet(self, root, depth, item, val):
        left, right, vals = self.trieLeft, self.trieRight, self.trieVal
        while item >> depth:  # too few bits for this item: the old trie becomes the left half of a taller one
            if root:
                left.append(root)
                right.append(0)
                vals.append(0)
                root = len(left) - 1
            depth += 1
        newRoot = cur = len(left)
        left.append(left[root])
        right.append(right[root])
        vals.append(vals[root])
        for bit in range(depth - 1, -1, -1):
            goRight = item >> bit & 1
            child = right[cur] if goRight else left[cur]
            copy = len(left)
            left.append(left[child])
            right.append(right[child])
            vals.append(vals[child])
            if goRight:
                right[cur] = copy
            else:
                left[cur] = copy
            cur = copy
        vals[cur] = val
        return newRoot, depth

    # @endif
    def _append(self, x):
        seq, palLen, palLink, nxt = self.seq, self.palLen, self.palLink, self.nxt
        i = len(seq)
        seq.append(x)
        k = self._key(x)
        # @if append+pop+persistentLinks
        if k not in self.idOf:
            self.idOf[k] = len(self.idOf)
        # @endif
        # @if append+pop
        cur = self._findPrecededBy(self.sufNode[-1] if i else 1, i, x, k)
        # @else
        cur = self.sufNode[-1] if i else 1
        while True:
            j = i - palLen[cur] - 1
            if j >= 0 and seq[j] == x:
                break
            cur = palLink[cur]
        # @endif
        node = nxt[cur].get(k)
        # @if pop
        self.createdAt.append(node is None)
        # @endif
        if node is None:
            node = len(palLen)
            palLen.append(palLen[cur] + 2)
            if palLen[node] == 1:
                link = 1
            else:
                # @if append+pop
                link = nxt[self._findPrecededBy(palLink[cur], i, x, k)][k]
                # @else
                t = palLink[cur]
                while True:
                    j = i - palLen[t] - 1
                    if j >= 0 and seq[j] == x:
                        break
                    t = palLink[t]
                link = nxt[t][k]
                # @endif
            palLink.append(link)
            nxt.append({})
            nxt[cur][k] = node
            # @if numPalsEndingAtR numPalsTotal numPalsEndingAtEachR numPalsEndingAtCurrentR numPalsStartingAtCurrentL
            self.depth.append(self.depth[link] + 1)
            # @endif
            # @if distinctPalsWithCounts
            self.firstEnd.append(i)
            # @endif
            # @if minPalPartition
            d = palLen[node] - palLen[link]
            self.diff.append(d)
            self.seriesLink.append(link if d != self.diff[link] else self.seriesLink[link])
            # @endif
            # @if append+pop+quickLinks
            if palLen[link] <= 0:
                self.quick.append(0)
            elif seq[i - palLen[palLink[link]]] != seq[i - palLen[link]]:
                self.quick.append(palLink[link])
            else:
                self.quick.append(self.quick[link])
            # @endif
            # @if append+pop+itemLinks
            links = dict(self.itemLink[link])  # node's proper suffixes are link and link's proper suffixes
            links[self._key(seq[i - palLen[link]])] = link  # the item right before link inside node
            self.itemLink.append(links)
            # @endif
            # @if append+pop+persistentLinks
            self.trieSizeBefore.append(len(self.trieLeft))
            before = self.idOf[self._key(seq[i - palLen[link]])]
            root, depth = self._trieSet(self.linkRoot[link], self.linkDepth[link], before, link)
            self.linkRoot.append(root)
            self.linkDepth.append(depth)
            # @endif
            # @if pop
            self.parent.append(cur)
            # @endif
        self.sufNode.append(node)
        # @if numDistinctPalsInPrefixEndingAtR numDistinctPalsInPrefixEndingAtEachR
        self.distinctInPrefix.append(len(palLen) - 2)
        # @endif
        # @if longestPalStartingAtCurrentL
        self.palPrefixLen.append(i + 1 if palLen[node] == i + 1 else (self.palPrefixLen[-1] if i else 0))
        # @endif
        # @if numPalsStartingAtCurrentL
        self.palPrefixNode.append(node if palLen[node] == i + 1 else self.palPrefixNode[-1])
        # @endif
        # @if longestPal
        self.longestUpTo.append(max(palLen[node], self.longestUpTo[-1] if i else 0))
        # @endif
        # @if numPalsTotal
        self.totalPals += self.depth[node]
        # @endif
        # @if rightmostRForPalStartingAtL rightmostRForPalStartingAtEachL
        self._revLens = None
        # @endif

    # @if append
    # @if pop
    # @if quickLinks
    # O(log n) expected
    # @endif
    # @if itemLinks
    # O(alphabet) expected
    # @endif
    # @if persistentLinks
    # O(log alphabet) expected
    # @endif
    # @else
    # O(1) amortized expected
    # @endif
    # adds x to the end
    def append(self, x):
        self._append(x)

    # @endif
    # @if pop
    # O(1) expected -- removes and returns the last item
    def pop(self):
        if not self.seq:
            raise IndexError("pop from an empty Eertree")
        node = self.sufNode.pop()
        # @if numPalsTotal
        self.totalPals -= self.depth[node]
        # @endif
        # @if numDistinctPalsInPrefixEndingAtR numDistinctPalsInPrefixEndingAtEachR
        self.distinctInPrefix.pop()
        # @endif
        # @if longestPalStartingAtCurrentL
        self.palPrefixLen.pop()
        # @endif
        # @if numPalsStartingAtCurrentL
        self.palPrefixNode.pop()
        # @endif
        # @if longestPal
        self.longestUpTo.pop()
        # @endif
        # @if rightmostRForPalStartingAtL rightmostRForPalStartingAtEachL
        self._revLens = None
        # @endif
        x = self.seq.pop()
        if self.createdAt.pop():  # this position made the newest node: take it back out
            del self.nxt[self.parent[node]][self._key(x)]
            self.palLen.pop()
            self.palLink.pop()
            self.nxt.pop()
            self.parent.pop()
            # @if numPalsEndingAtR numPalsTotal numPalsEndingAtEachR numPalsEndingAtCurrentR numPalsStartingAtCurrentL
            self.depth.pop()
            # @endif
            # @if distinctPalsWithCounts
            self.firstEnd.pop()
            # @endif
            # @if minPalPartition
            self.diff.pop()
            self.seriesLink.pop()
            # @endif
            # @if append+pop+quickLinks
            self.quick.pop()
            # @endif
            # @if append+pop+itemLinks
            self.itemLink.pop()
            # @endif
            # @if append+pop+persistentLinks
            self.linkRoot.pop()
            self.linkDepth.pop()
            size = self.trieSizeBefore.pop()
            del self.trieLeft[size:], self.trieRight[size:], self.trieVal[size:]
            # @endif
        return x

    # @endif
    # @if leftmostLForPalEndingAtR rightmostRForPalStartingAtL numDistinctPalsInPrefixEndingAtR numPalsEndingAtR
    def _checkIndex(self, i):
        if not 0 <= i < len(self.seq):
            raise IndexError(f"index {i} out of range for an Eertree of length {len(self.seq)}")

    # @endif
    # @if leftmostLForPalEndingAtR leftmostLForPalEndingAtEachR
    # @if leftmostLForPalEndingAtR
    # O(1) -- the smallest l such that seq[l..r] is a palindrome
    def leftmostLForPalEndingAtR(self, r):
        self._checkIndex(r)
        return r - self.palLen[self.sufNode[r]] + 1

    # @endif
    # @if leftmostLForPalEndingAtEachR
    # O(n) -- list of size n, res[r] = leftmostLForPalEndingAtR(r)
    def leftmostLForPalEndingAtEachR(self):
        palLen = self.palLen
        return [r - palLen[node] + 1 for r, node in enumerate(self.sufNode)]

    # @endif
    # @endif
    # @if rightmostRForPalStartingAtL rightmostRForPalStartingAtEachL
    # @if rightmostRForPalStartingAtL
    # O(n) expected on the first call after a change (builds the eertree of the reversed sequence), O(1) after
    # the largest r such that seq[l..r] is a palindrome
    def rightmostRForPalStartingAtL(self, l):
        self._checkIndex(l)
        return l + self._reversedLongestPalSuffix()[len(self.seq) - 1 - l] - 1

    # @endif
    # @if rightmostRForPalStartingAtEachL
    # O(n) -- list of size n, res[l] = rightmostRForPalStartingAtL(l)
    def rightmostRForPalStartingAtEachL(self):
        rev = self._reversedLongestPalSuffix()
        n = len(self.seq)
        return [l + rev[n - 1 - l] - 1 for l in range(n)]

    # @endif
    def _reversedLongestPalSuffix(self):
        if self._revLens is None:
            rev = [self._key(x) for x in reversed(self.seq)]
            palLen, palLink, nxt = [-1, 0], [0, 0], [{}, {}]
            last = 1
            lens = []
            for i, x in enumerate(rev):
                cur = last
                while True:
                    j = i - palLen[cur] - 1
                    if j >= 0 and rev[j] == x:
                        break
                    cur = palLink[cur]
                node = nxt[cur].get(x)
                if node is None:
                    node = len(palLen)
                    palLen.append(palLen[cur] + 2)
                    if palLen[node] == 1:
                        link = 1
                    else:
                        t = palLink[cur]
                        while True:
                            j = i - palLen[t] - 1
                            if j >= 0 and rev[j] == x:
                                break
                            t = palLink[t]
                        link = nxt[t][x]
                    palLink.append(link)
                    nxt.append({})
                    nxt[cur][x] = node
                last = node
                lens.append(palLen[node])
            self._revLens = lens
        return self._revLens

    # @endif
    # @if longestPalEndingAtCurrentR
    # O(1) -- length of the longest palindrome ending at the current right end (0 if empty)
    def longestPalEndingAtCurrentR(self):
        return self.palLen[self.sufNode[-1]] if self.seq else 0

    # @endif
    # @if longestPalStartingAtCurrentL
    # O(1) -- length of the longest palindrome starting at the current left end (0 if empty)
    def longestPalStartingAtCurrentL(self):
        return self.palPrefixLen[-1] if self.seq else 0

    # @endif
    # @if numDistinctPals
    # O(1) -- how many distinct palindromic substrings the sequence has, at most n
    def numDistinctPals(self):
        return len(self.palLen) - 2

    # @endif
    # @if numDistinctPalsInPrefixEndingAtR numDistinctPalsInPrefixEndingAtEachR
    # @if numDistinctPalsInPrefixEndingAtR
    # O(1) -- how many distinct palindromic substrings seq[0..r] has
    def numDistinctPalsInPrefixEndingAtR(self, r):
        self._checkIndex(r)
        return self.distinctInPrefix[r]

    # @endif
    # @if numDistinctPalsInPrefixEndingAtEachR
    # O(n) -- list of size n, res[r] = numDistinctPalsInPrefixEndingAtR(r)
    def numDistinctPalsInPrefixEndingAtEachR(self):
        return list(self.distinctInPrefix)

    # @endif
    # @endif
    # @if numPalsEndingAtR numPalsEndingAtEachR
    # @if numPalsEndingAtR
    # O(1) -- how many palindromic substrings end exactly at r
    def numPalsEndingAtR(self, r):
        self._checkIndex(r)
        return self.depth[self.sufNode[r]]

    # @endif
    # @if numPalsEndingAtEachR
    # O(n) -- list of size n, res[r] = numPalsEndingAtR(r)
    def numPalsEndingAtEachR(self):
        depth = self.depth
        return [depth[node] for node in self.sufNode]

    # @endif
    # @endif
    # @if numPalsTotal
    # O(1) -- total palindromic substrings counted with multiplicity ("aa" has 3: a, a, aa)
    def numPalsTotal(self):
        return self.totalPals

    # @endif
    # @if numPalsEndingAtCurrentR
    # O(1) -- how many palindromic substrings end at the current right end (0 if empty)
    def numPalsEndingAtCurrentR(self):
        return self.depth[self.sufNode[-1]] if self.seq else 0

    # @endif
    # @if numPalsStartingAtCurrentL
    # O(1) -- how many palindromic substrings start at the current left end (0 if empty)
    def numPalsStartingAtCurrentL(self):
        return self.depth[self.palPrefixNode[-1]] if self.seq else 0

    # @endif
    # @if longestPal
    # O(1) -- length of the longest palindromic substring (0 if empty)
    def longestPal(self):
        return self.longestUpTo[-1] if self.seq else 0

    # @endif
    # @if distinctPalsWithCounts
    # O(n) -- list of (l, r, count), one per distinct palindromic substring: seq[l..r] is its first occurrence and
    # count is how many times it occurs
    def distinctPalsWithCounts(self):
        occ = [0] * len(self.palLen)
        for node in self.sufNode:
            occ[node] += 1
        for node in range(len(self.palLen) - 1, 1, -1):
            occ[self.palLink[node]] += occ[node]
        res = []
        for node in range(2, len(self.palLen)):
            end = self.firstEnd[node]
            res.append((end - self.palLen[node] + 1, end, occ[node]))
        return res

    # @endif
    # @if minPalPartition
    # O(n log n) -- fewest palindromes the sequence can be cut into (0 if empty)
    def minPalPartition(self):
        palLen, palLink, diff, seriesLink = self.palLen, self.palLink, self.diff, self.seriesLink
        n = len(self.seq)
        INF = float("inf")
        dp = [INF] * (n + 1)
        dp[0] = 0
        seriesAns = [0] * len(palLen)
        for i in range(1, n + 1):
            node = self.sufNode[i - 1]
            while palLen[node] > 0:
                seriesAns[node] = dp[i - palLen[seriesLink[node]] - diff[node]]
                if diff[node] == diff[palLink[node]]:
                    seriesAns[node] = min(seriesAns[node], seriesAns[palLink[node]])
                if seriesAns[node] + 1 < dp[i]:
                    dp[i] = seriesAns[node] + 1
                node = seriesLink[node]
        return dp[n]

    # @endif
