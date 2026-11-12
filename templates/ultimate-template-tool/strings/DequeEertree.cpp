// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/strings/DequeEertree.cpp
#include <bits/stdc++.h>
using namespace std;

// Palindromic tree (eertree) over a deque: append, appendLeft, pop, popLeft.
// Works on any E that is integral, has std::hash (e.g. string), or is a pair of those, with operator==.
// DequeEertree<char> et("abaab");
// DequeEertree<long long> et(vector<long long>{-1, 2, -1});
// DequeEertree<pair<int, int>> et;
//
// n = current length. Pops follow Wang, Yang, Zhu "Double-Ended Palindromic Trees" (surface recording).
// A surface is a palindrome occurrence that isn't a prefix or suffix of a longer palindrome occurrence.
// A palindrome occurs iff it's a surface or a link-tree ancestor of one, so a node is alive while
// (its surface count) + (its alive link children) > 0. The longest palindrome at either end is always a surface, and a
// position has at most one surface starting / ending there, kept in preSurf / sufSurf.
// Popping the right end kills its surface t; the copy of link(t) at the front of t becomes a surface unless some
// surface already ends where that copy ends. Pushing is the mirror. So every op changes O(1) surfaces and creates or
// deletes at most one node. Positions are global indices into a ring buffer, so nothing shifts on appendLeft. A push
// has to find the longest palindrome at that end that the new item extends, without amortization
// (pops would break it):
// @if quickLinks
// quick links skip a whole run of equal-difference palindromic suffixes per jump, so O(log n) jumps worst case.
// @endif
// @if itemLinks
// every palindrome keeps a link per item (alphabet = number of distinct items), so it's one scan of that list, but
// making a palindrome copies its suffix link's links: O(alphabet) time and memory per palindrome.
// @endif
// @if persistentLinks
// every palindrome's per-item links are a persistent array (a binary trie over item ids) that shares all but one path
// with its suffix link's, so O(log alphabet) per push; trie nodes nothing points to any more are reused, so memory
// stays O(size * log alphabet).
// @endif
template <class E>
class DequeEertree {
    // hash of a (node, item) key: every item hash mixes in a per-run random seed, so colliding inputs can't be
    // prepared in advance (ints, strings and pairs of them; any other type is only as safe as its std::hash)
    struct KeyHash {
        static uint64_t mix(uint64_t x) {  // splitmix64
            x += 0x9e3779b97f4a7c15ULL;
            x = (x ^ (x >> 30)) * 0xbf58476d1ce4e5b9ULL;
            x = (x ^ (x >> 27)) * 0x94d049bb133111ebULL;
            return x ^ (x >> 31);
        }
        static uint64_t seed() {
            static const uint64_t s = mix(chrono::steady_clock::now().time_since_epoch().count());
            return s;
        }
        template <class T>
        static uint64_t itemHash(const T& x) {
            if constexpr (is_integral_v<T>) return mix((uint64_t)x ^ seed());
            else return mix((uint64_t)hash<T>{}(x) ^ seed());
        }
        template <class C, class Tr, class A>
        static uint64_t itemHash(const basic_string<C, Tr, A>& s) {
            uint64_t h = mix(seed() + s.size());
            for (C c : s) h = mix(h ^ (uint64_t)c);
            return h;
        }
        template <class A, class B>
        static uint64_t itemHash(const pair<A, B>& p) {
            return mix(itemHash(p.first) * 0x9e3779b97f4a7c15ULL + itemHash(p.second));
        }
        size_t operator()(const pair<int, E>& key) const {
            return mix(itemHash(key.second) + (uint64_t)key.first * 0x9e3779b97f4a7c15ULL);
        }
    };

    // node 0: imaginary root (len -1), node 1: empty root (len 0); 0 in preSurf / sufSurf means "no surface"
    vector<int> lens{-1, 0}, link{0, 0};
    // @if quickLinks
    vector<int> quick{0, 0};
    // @endif
    // @if itemLinks
    // itemLink[node] = for each item x, the longest proper palindromic suffix of node with x right before it (absent:
    // the imaginary root); a plain list, since making a palindrome copies it anyway
    vector<vector<pair<E, int>>> itemLink = vector<vector<pair<E, int>>>(2);
    // @endif
    // @if persistentLinks
    struct ItemHash {
        size_t operator()(const E& x) const { return KeyHash::itemHash(x); }
    };
    unordered_map<E, int, ItemHash> idOf;
    vector<int> trieLeft{0}, trieRight{0}, trieVal{0}, trieRefs{0}, trieFree;  // trie node 0 = empty
    vector<int> linkRoot{0, 0}, linkDepth{0, 0};

    int trieGet(int root, int depth, int item) const {
        if (item >> depth) return 0;
        for (int bit = depth - 1; bit >= 0; bit--) {
            root = item >> bit & 1 ? trieRight[root] : trieLeft[root];
            if (!root) return 0;
        }
        return trieVal[root];
    }

    int trieNode(int left, int right, int val) {  // a trie node holding a reference to each child
        if (left) trieRefs[left]++;
        if (right) trieRefs[right]++;
        int t;
        if (!trieFree.empty()) {
            t = trieFree.back();
            trieFree.pop_back();
            trieLeft[t] = left;
            trieRight[t] = right;
            trieVal[t] = val;
            trieRefs[t] = 0;
        } else {
            t = trieLeft.size();
            trieLeft.push_back(left);
            trieRight.push_back(right);
            trieVal.push_back(val);
            trieRefs.push_back(0);
        }
        return t;
    }

    void trieRelease(int t) {  // drop one reference to t, freeing whatever nothing points to any more
        vector<int> stack{t};
        while (!stack.empty()) {
            t = stack.back();
            stack.pop_back();
            if (t && !--trieRefs[t]) {
                stack.push_back(trieLeft[t]);
                stack.push_back(trieRight[t]);
                trieFree.push_back(t);
            }
        }
    }

    // a new version with [item] = val, sharing everything off the one path it copies: O(log alphabet). The caller owns
    // one reference to the returned root
    pair<int, int> trieSet(int root, int depth, int item, int val) {
        int top = root;
        while (item >> depth) {  // too few bits for this item: the old trie becomes the left half of a taller one
            if (root) root = trieNode(root, 0, 0);
            depth++;
        }
        int newRoot = trieNode(trieLeft[root], trieRight[root], trieVal[root]), cur = newRoot;
        for (int bit = depth - 1; bit >= 0; bit--) {
            bool goRight = item >> bit & 1;
            int child = goRight ? trieRight[cur] : trieLeft[cur];
            int copy = trieNode(trieLeft[child], trieRight[child], trieVal[child]);
            (goRight ? trieRight[cur] : trieLeft[cur]) = copy;
            trieRefs[copy]++;
            if (child) trieRelease(child);
            cur = copy;
        }
        trieVal[cur] = val;
        trieRefs[newRoot]++;
        if (root != top) {  // the taller wrappers were only scaffolding
            trieRefs[root]++;
            trieRelease(root);
        }
        return {newRoot, depth};
    }
    // @endif
    vector<E> diff = vector<E>(2);  // node[len(link)], the item right after the copy of link at the front of node
    vector<int> cnt{0, 0};          // surfaces of this palindrome
    vector<int> kids{0, 0};         // alive nodes whose link is this one
    vector<int> par{0, 0};          // node = edge + par + edge
    vector<E> edge = vector<E>(2);
    // @if numPalsTotal numPalsEndingAtCurrentR numPalsStartingAtCurrentL
    vector<int> depth{0, 0};  // palindromic suffixes of node, itself included
    // @endif
    // @if numPalsTotal
    long long total = 0;
    // @endif
    // @if numDistinctPals
    int distinct = 0;
    // @endif
    // @if longestPal
    // live palindromes per length, and the longest live even / odd length. A palindrome only dies while its inner
    // palindrome (2 shorter) is still around, so when the longest length runs out, the next longest is 2 shorter
    vector<int> lenCount{0};
    int longestOfParity[2] = {0, -1};
    // @endif
    vector<int> freeNodes;
    unordered_map<pair<int, E>, int, KeyHash> to;
    long long mask = 7, l = 0, r = 0;
    vector<E> data = vector<E>(8);
    vector<int> preSurf = vector<int>(8), sufSurf = vector<int>(8);

    void grow() {
        long long newMask = mask * 2 + 1;
        vector<E> newData(newMask + 1);
        vector<int> newPre(newMask + 1), newSuf(newMask + 1);
        for (long long pos = l; pos < r; pos++) {
            newData[pos & newMask] = data[pos & mask];
            newPre[pos & newMask] = preSurf[pos & mask];
            newSuf[pos & newMask] = sufSurf[pos & mask];
        }
        data.swap(newData);
        preSurf.swap(newPre);
        sufSurf.swap(newSuf);
        mask = newMask;
    }

    // longest palindromic suffix (step = -1) or prefix (step = 1) of the current string that is preceded / followed by
    // x, where x is already written at pos; lo..hi is the valid range
    int walk(int cur, const E& x, long long pos, int step, long long lo, long long hi) const {
        // @if quickLinks
        while (true) {
            int len = lens[cur];
            if (len == -1) return cur;
            long long j = pos + (long long)step * (len + 1);
            if (lo <= j && j <= hi && data[j & mask] == x) return cur;
            if (len == 0) return 0;
            if (diff[cur] == x) return link[cur];
            cur = quick[cur];
        }
        // @endif
        // @if itemLinks persistentLinks
        int len = lens[cur];
        if (len == -1) return cur;
        long long j = pos + (long long)step * (len + 1);
        if (lo <= j && j <= hi && data[j & mask] == x) return cur;
        // @endif
        // @if itemLinks
        for (const auto& [item, to] : itemLink[cur]) if (item == x) return to;
        return 0;  // the imaginary root fits any x
        // @endif
        // @if persistentLinks
        auto found = idOf.find(x);
        return found == idOf.end() ? 0 : trieGet(linkRoot[cur], linkDepth[cur], found->second);
        // @endif
    }

    // node for x + str(cur) + x, created if missing
    int child(int cur, const E& x, long long pos, int step, long long lo, long long hi) {
        auto it = to.find({cur, x});
        if (it != to.end()) return it->second;
        int len = lens[cur] + 2;
        int lk = len == 1 ? 1 : to.find({walk(link[cur], x, pos, step, lo, hi), x})->second;
        long long start = step == 1 ? pos : pos - len + 1;
        E d = data[(start + lens[lk]) & mask];
        // @if quickLinks
        int q = lens[lk] <= 0 ? 0 : (diff[lk] == d ? quick[lk] : link[lk]);
        // @endif
        // @if itemLinks
        vector<pair<E, int>> links = itemLink[lk];  // node's proper suffixes are lk and lk's proper suffixes
        bool seen = false;  // d is the item right before lk inside node
        for (auto& [item, to] : links) if (item == d) { to = lk; seen = true; }
        if (!seen) links.emplace_back(d, lk);
        // @endif
        // @if persistentLinks
        auto [root, rootDepth] = trieSet(linkRoot[lk], linkDepth[lk], idOf.at(d), lk);
        // @endif
        int node;
        if (!freeNodes.empty()) {
            node = freeNodes.back();
            freeNodes.pop_back();
        } else {
            node = lens.size();
            lens.push_back(0);
            link.push_back(0);
            // @if quickLinks
            quick.push_back(0);
            // @endif
            // @if itemLinks
            itemLink.emplace_back();
            // @endif
            // @if persistentLinks
            linkRoot.push_back(0);
            linkDepth.push_back(0);
            // @endif
            diff.push_back(E());
            cnt.push_back(0);
            kids.push_back(0);
            par.push_back(0);
            edge.push_back(E());
            // @if numPalsTotal numPalsEndingAtCurrentR numPalsStartingAtCurrentL
            depth.push_back(0);
            // @endif
        }
        lens[node] = len;
        link[node] = lk;
        // @if quickLinks
        quick[node] = q;
        // @endif
        // @if itemLinks
        itemLink[node] = move(links);
        // @endif
        // @if persistentLinks
        linkRoot[node] = root;
        linkDepth[node] = rootDepth;
        // @endif
        diff[node] = d;
        cnt[node] = 0;
        kids[node] = 0;
        par[node] = cur;
        edge[node] = x;
        // @if numPalsTotal numPalsEndingAtCurrentR numPalsStartingAtCurrentL
        depth[node] = depth[lk] + 1;
        // @endif
        kids[lk]++;
        // @if longestPal
        if ((int)lenCount.size() <= lens[node]) lenCount.resize(lens[node] + 1, 0);
        lenCount[lens[node]]++;
        longestOfParity[lens[node] & 1] = max(longestOfParity[lens[node] & 1], lens[node]);
        // @endif
        to[{cur, x}] = node;
        // @if numDistinctPals
        distinct++;
        // @endif
        return node;
    }

    // @if pop popLeft
    void maybeDelete(int node) {
        if (cnt[node] || kids[node]) return;
        to.erase({par[node], edge[node]});
        kids[link[node]]--;
        freeNodes.push_back(node);
        // @if itemLinks
        vector<pair<E, int>>().swap(itemLink[node]);
        // @endif
        // @if persistentLinks
        trieRelease(linkRoot[node]);
        linkRoot[node] = 0;
        // @endif
        // @if numDistinctPals
        distinct--;
        // @endif
        // @if longestPal
        if (!--lenCount[lens[node]]
            && longestOfParity[lens[node] & 1] == lens[node]) longestOfParity[lens[node] & 1] -= 2;
        // @endif
    }

    // @endif
public:
    DequeEertree() {}
    template <class C>
    explicit DequeEertree(const C& arrOrString) {
        for (const auto& x : arrOrString) append(x);
    }
    explicit DequeEertree(const char* arrOrString) {  // a string literal like "abaab"
        for (; *arrOrString; arrOrString++) append(*arrOrString);
    }

    int size() const { return r - l; }

    // @if quickLinks
    // O(log n) worst case + expected amortized O(1) (hashing, buffer growth).
    // @endif
    // @if itemLinks
    // O(alphabet) expected + amortized O(1) buffer growth.
    // @endif
    // @if persistentLinks
    // O(log alphabet) expected + amortized O(1) buffer growth.
    // @endif
    void append(const E& x) {
        if (r - l > mask) grow();
        long long pos = r, lo = l;
        data[pos & mask] = x;
        preSurf[pos & mask] = sufSurf[pos & mask] = 0;
        int cur = pos > lo ? sufSurf[(pos - 1) & mask] : 1;
        // @if persistentLinks
        idOf.try_emplace(x, (int)idOf.size());
        // @endif
        cur = walk(cur, x, pos, -1, lo, pos);
        int node = child(cur, x, pos, -1, lo, pos);
        // the surface that started where node starts is now a prefix of node
        long long start = pos - lens[node] + 1;
        int old = preSurf[start & mask];
        if (old) {
            cnt[old]--;
            sufSurf[(start + lens[old] - 1) & mask] = 0;
        }
        preSurf[start & mask] = node;
        sufSurf[pos & mask] = node;
        cnt[node]++;
        r = pos + 1;
        // @if numPalsTotal
        total += depth[node];
        // @endif
    }

    // @if appendLeft
    // @if quickLinks
    // O(log n) worst case + expected amortized O(1) (hashing, buffer growth).
    // @endif
    // @if itemLinks
    // O(alphabet) expected + amortized O(1) buffer growth.
    // @endif
    // @if persistentLinks
    // O(log alphabet) expected + amortized O(1) buffer growth.
    // @endif
    void appendLeft(const E& x) {
        if (r - l > mask) grow();
        long long pos = l - 1, hi = r - 1;
        data[pos & mask] = x;
        preSurf[pos & mask] = sufSurf[pos & mask] = 0;
        int cur = pos < hi ? preSurf[(pos + 1) & mask] : 1;
        // @if persistentLinks
        idOf.try_emplace(x, (int)idOf.size());
        // @endif
        cur = walk(cur, x, pos, 1, pos, hi);
        int node = child(cur, x, pos, 1, pos, hi);
        long long end = pos + lens[node] - 1;
        int old = sufSurf[end & mask];
        if (old) {
            cnt[old]--;
            preSurf[(end - lens[old] + 1) & mask] = 0;
        }
        sufSurf[end & mask] = node;
        preSurf[pos & mask] = node;
        cnt[node]++;
        l = pos;
        // @if numPalsTotal
        total += depth[node];
        // @endif
    }

    // @endif
    // @if pop
    // @if quickLinks
    // expected O(1). Removes and returns the last item.
    // @endif
    // @if itemLinks
    // O(alphabet) expected (a deleted palindrome's links are freed). Removes and returns the last item.
    // @endif
    // @if persistentLinks
    // O(log alphabet) expected (a deleted palindrome's trie path is freed). Removes and returns the last item.
    // @endif
    E pop() {
        if (r == l) throw out_of_range("pop from an empty DequeEertree");
        long long pos = r - 1;
        int node = sufSurf[pos & mask];
        long long start = pos - lens[node] + 1;
        cnt[node]--;
        preSurf[start & mask] = sufSurf[pos & mask] = 0;
        if (lens[node] > 1) {
            // the copy of link(node) at the front of node is a surface now, unless a surface already ends there
            int lk = link[node];
            long long end = start + lens[lk] - 1;
            if (!sufSurf[end & mask]) {
                cnt[lk]++;
                preSurf[start & mask] = sufSurf[end & mask] = lk;
            }
        }
        // @if numPalsTotal
        total -= depth[node];
        // @endif
        maybeDelete(node);
        r = pos;
        return data[pos & mask];
    }

    // @endif
    // @if popLeft
    // @if quickLinks
    // expected O(1). Removes and returns the first item.
    // @endif
    // @if itemLinks
    // O(alphabet) expected (a deleted palindrome's links are freed). Removes and returns the first item.
    // @endif
    // @if persistentLinks
    // O(log alphabet) expected (a deleted palindrome's trie path is freed). Removes and returns the first item.
    // @endif
    E popLeft() {
        if (r == l) throw out_of_range("pop from an empty DequeEertree");
        long long pos = l;
        int node = preSurf[pos & mask];
        long long end = pos + lens[node] - 1;
        cnt[node]--;
        preSurf[pos & mask] = sufSurf[end & mask] = 0;
        if (lens[node] > 1) {
            int lk = link[node];
            long long start = end - lens[lk] + 1;
            if (!preSurf[start & mask]) {
                cnt[lk]++;
                preSurf[start & mask] = sufSurf[end & mask] = lk;
            }
        }
        // @if numPalsTotal
        total -= depth[node];
        // @endif
        maybeDelete(node);
        l = pos + 1;
        return data[pos & mask];
    }

    // @endif
    // @if numDistinctPals
    // O(1). Number of distinct non-empty palindromic substrings.
    int numDistinctPals() const { return distinct; }

    // @endif
    // @if numPalsTotal
    // O(1). Number of palindromic substrings counted with multiplicity (by position).
    long long numPalsTotal() const { return total; }

    // @endif
    // @if longestPalEndingAtCurrentR
    // O(1). Length of the longest palindrome ending at the last item, 0 if empty.
    int longestPalEndingAtCurrentR() const { return r == l ? 0 : lens[sufSurf[(r - 1) & mask]]; }

    // @endif
    // @if longestPalStartingAtCurrentL
    // O(1). Length of the longest palindrome starting at the first item, 0 if empty.
    int longestPalStartingAtCurrentL() const { return r == l ? 0 : lens[preSurf[l & mask]]; }
    // @endif

    // @if longestPal
    // O(1). Length of the longest palindromic substring, 0 if empty.
    int longestPal() const { return max(longestOfParity[0], longestOfParity[1]); }

    // @endif

    // @if numPalsEndingAtCurrentR
    // O(1). How many palindromic substrings end at the current right end, 0 if empty.
    int numPalsEndingAtCurrentR() const { return r == l ? 0 : depth[sufSurf[(r - 1) & mask]]; }

    // @endif
    // @if numPalsStartingAtCurrentL
    // O(1). How many palindromic substrings start at the current left end, 0 if empty.
    int numPalsStartingAtCurrentL() const { return r == l ? 0 : depth[preSurf[l & mask]]; }

    // @endif
};
