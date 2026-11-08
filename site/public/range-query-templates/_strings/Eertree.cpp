// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/strings/Eertree.cpp
#include <bits/stdc++.h>
using namespace std;

// Palindromic tree (eertree) over a sequence: every distinct palindromic substring is one node inside, but every method
// below talks in indices into the sequence. A sequence of length n has at most n distinct palindromic substrings.
// works on any element type that has == and a hash (char, int, long long, string, pair of those, ...); E is the element type
// Eertree<char> et("abaab");
// Eertree<int> et(vector<int>{-1, 2, -1});
// Eertree<int> et;   // empty, then append
template <class E>
class Eertree {
public:
    // @if append+pop
    // @if quickLinks
    // O(n log n) expected time, O(n) space (append finds its palindrome through quick links, so it stays fast after pops)
    // @endif
    // @if itemLinks
    // O(n * alphabet) expected time and space, alphabet = number of distinct items (every palindrome keeps a link per item)
    // @endif
    // @if persistentLinks
    // O(n log alphabet) expected time and space, alphabet = number of distinct items (every palindrome's links are a persistent array)
    // @endif
    // @else
    // O(n) expected time, O(n) space
    // @endif
    Eertree() {}
    template <class C>
    explicit Eertree(const C& arrOrString) {
        for (const auto& x : arrOrString) appendItem(x);
    }
    explicit Eertree(const char* arrOrString) : Eertree(string(arrOrString)) {}  // a string literal like "abaab"

    // @if append
    // @if pop
    // @if quickLinks
    // O(log n) expected
    // @endif
    // @if itemLinks
    // O(alphabet) expected
    // @endif
    // @if persistentLinks
    // O(log alphabet) expected
    // @endif
    // @else
    // O(1) amortized expected
    // @endif
    // adds x to the end
    void append(const E& x) { appendItem(x); }

    // @endif
    // @if pop
    // O(1) expected -- removes and returns the last item
    E pop() {
        if (seq.empty()) throw out_of_range("pop from an empty Eertree");
        int node = sufNode.back();
        sufNode.pop_back();
        // @if numPalsTotal
        totalPals -= depth[node];
        // @endif
        // @if numDistinctPalsInPrefixEndingAtR numDistinctPalsInPrefixEndingAtEachR
        distinctInPrefix.pop_back();
        // @endif
        // @if longestPalStartingAtCurrentL
        palPrefixLen.pop_back();
        // @endif
        // @if numPalsStartingAtCurrentL
        palPrefixNode.pop_back();
        // @endif
        // @if longestPal
        longestUpTo.pop_back();
        // @endif
        // @if rightmostRForPalStartingAtL rightmostRForPalStartingAtEachL
        revLens.clear();
        // @endif
        E x = seq.back();
        seq.pop_back();
        bool created = createdAt.back();
        createdAt.pop_back();
        if (created) {  // this position made the newest node: take it back out
            nxt.erase({parent[node], x});
            palLen.pop_back();
            palLink.pop_back();
            parent.pop_back();
            // @if numPalsEndingAtR numPalsTotal numPalsEndingAtEachR numPalsEndingAtCurrentR numPalsStartingAtCurrentL
            depth.pop_back();
            // @endif
            // @if distinctPalsWithCounts
            firstEnd.pop_back();
            // @endif
            // @if minPalPartition
            diff.pop_back();
            seriesLink.pop_back();
            // @endif
            // @if append+pop+quickLinks
            quick.pop_back();
            // @endif
            // @if append+pop+itemLinks
            itemLink.pop_back();
            // @endif
            // @if append+pop+persistentLinks
            linkRoot.pop_back();
            linkDepth.pop_back();
            int size = trieSizeBefore.back();
            trieSizeBefore.pop_back();
            trieLeft.resize(size);
            trieRight.resize(size);
            trieVal.resize(size);
            // @endif
        }
        return x;
    }

    // @endif
    // @if leftmostLForPalEndingAtR leftmostLForPalEndingAtEachR
    // @if leftmostLForPalEndingAtR
    // O(1) -- the smallest l such that seq[l..r] is a palindrome
    int leftmostLForPalEndingAtR(int r) const {
        checkIndex(r);
        return r - palLen[sufNode[r]] + 1;
    }

    // @endif
    // @if leftmostLForPalEndingAtEachR
    // O(n) -- vector of size n, res[r] = leftmostLForPalEndingAtR(r)
    vector<int> leftmostLForPalEndingAtEachR() const {
        vector<int> res(seq.size());
        for (int r = 0; r < (int)seq.size(); r++) res[r] = r - palLen[sufNode[r]] + 1;
        return res;
    }

    // @endif
    // @endif
    // @if rightmostRForPalStartingAtL rightmostRForPalStartingAtEachL
    // @if rightmostRForPalStartingAtL
    // O(n) expected on the first call after a change (builds the eertree of the reversed sequence), O(1) after
    // the largest r such that seq[l..r] is a palindrome
    int rightmostRForPalStartingAtL(int l) {
        checkIndex(l);
        return l + reversedLongestPalSuffix()[seq.size() - 1 - l] - 1;
    }

    // @endif
    // @if rightmostRForPalStartingAtEachL
    // O(n) -- vector of size n, res[l] = rightmostRForPalStartingAtL(l)
    vector<int> rightmostRForPalStartingAtEachL() {
        const vector<int>& rev = reversedLongestPalSuffix();
        int n = (int)seq.size();
        vector<int> res(n);
        for (int l = 0; l < n; l++) res[l] = l + rev[n - 1 - l] - 1;
        return res;
    }

    // @endif
    // @endif
    // @if longestPalEndingAtCurrentR
    // O(1) -- length of the longest palindrome ending at the current right end (0 if empty)
    int longestPalEndingAtCurrentR() const { return seq.empty() ? 0 : palLen[sufNode.back()]; }

    // @endif
    // @if longestPalStartingAtCurrentL
    // O(1) -- length of the longest palindrome starting at the current left end (0 if empty)
    int longestPalStartingAtCurrentL() const { return seq.empty() ? 0 : palPrefixLen.back(); }

    // @endif
    // @if numDistinctPals
    // O(1) -- how many distinct palindromic substrings the sequence has, at most n
    int numDistinctPals() const { return (int)palLen.size() - 2; }

    // @endif
    // @if numDistinctPalsInPrefixEndingAtR numDistinctPalsInPrefixEndingAtEachR
    // @if numDistinctPalsInPrefixEndingAtR
    // O(1) -- how many distinct palindromic substrings seq[0..r] has
    int numDistinctPalsInPrefixEndingAtR(int r) const {
        checkIndex(r);
        return distinctInPrefix[r];
    }

    // @endif
    // @if numDistinctPalsInPrefixEndingAtEachR
    // O(n) -- vector of size n, res[r] = numDistinctPalsInPrefixEndingAtR(r)
    vector<int> numDistinctPalsInPrefixEndingAtEachR() const { return distinctInPrefix; }

    // @endif
    // @endif
    // @if numPalsEndingAtR numPalsEndingAtEachR
    // @if numPalsEndingAtR
    // O(1) -- how many palindromic substrings end exactly at r
    int numPalsEndingAtR(int r) const {
        checkIndex(r);
        return depth[sufNode[r]];
    }

    // @endif
    // @if numPalsEndingAtEachR
    // O(n) -- vector of size n, res[r] = numPalsEndingAtR(r)
    vector<int> numPalsEndingAtEachR() const {
        vector<int> res(seq.size());
        for (int r = 0; r < (int)seq.size(); r++) res[r] = depth[sufNode[r]];
        return res;
    }

    // @endif
    // @endif
    // @if numPalsTotal
    // O(1) -- total palindromic substrings counted with multiplicity ("aa" has 3: a, a, aa)
    long long numPalsTotal() const { return totalPals; }

    // @endif
    // @if numPalsEndingAtCurrentR
    // O(1) -- how many palindromic substrings end at the current right end (0 if empty)
    int numPalsEndingAtCurrentR() const { return seq.empty() ? 0 : depth[sufNode.back()]; }

    // @endif
    // @if numPalsStartingAtCurrentL
    // O(1) -- how many palindromic substrings start at the current left end (0 if empty)
    int numPalsStartingAtCurrentL() const { return seq.empty() ? 0 : depth[palPrefixNode.back()]; }

    // @endif
    // @if longestPal
    // O(1) -- length of the longest palindromic substring (0 if empty)
    int longestPal() const { return seq.empty() ? 0 : longestUpTo.back(); }

    // @endif
    // @if distinctPalsWithCounts
    // O(n) -- vector of {l, r, count}, one per distinct palindromic substring: seq[l..r] is its first occurrence and
    // count is how many times it occurs
    vector<tuple<int, int, long long>> distinctPalsWithCounts() const {
        int nodes = (int)palLen.size();
        vector<long long> occ(nodes, 0);
        for (int node : sufNode) occ[node]++;
        for (int node = nodes - 1; node > 1; node--) occ[palLink[node]] += occ[node];
        vector<tuple<int, int, long long>> res;
        for (int node = 2; node < nodes; node++) res.emplace_back(firstEnd[node] - palLen[node] + 1, firstEnd[node], occ[node]);
        return res;
    }

    // @endif
    // @if minPalPartition
    // O(n log n) -- fewest palindromes the sequence can be cut into (0 if empty)
    int minPalPartition() const {
        int n = (int)seq.size();
        const int INF = INT_MAX / 2;
        vector<int> dp(n + 1, INF), seriesAns(palLen.size(), 0);
        dp[0] = 0;
        for (int i = 1; i <= n; i++) {
            for (int node = sufNode[i - 1]; palLen[node] > 0; node = seriesLink[node]) {
                seriesAns[node] = dp[i - palLen[seriesLink[node]] - diff[node]];
                if (diff[node] == diff[palLink[node]]) seriesAns[node] = min(seriesAns[node], seriesAns[palLink[node]]);
                dp[i] = min(dp[i], seriesAns[node] + 1);
            }
        }
        return dp[n];
    }

    // @endif
private:
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
        static uint64_t itemHash(const pair<A, B>& p) { return mix(itemHash(p.first) * 0x9e3779b97f4a7c15ULL + itemHash(p.second)); }
        size_t operator()(const pair<int, E>& key) const { return mix(itemHash(key.second) + (uint64_t)key.first * 0x9e3779b97f4a7c15ULL); }
    };
    using Table = unordered_map<pair<int, E>, int, KeyHash>;

    vector<E> seq;
    vector<int> palLen{-1, 0};  // node 0 = the imaginary length -1 root, node 1 = the empty palindrome
    vector<int> palLink{0, 0};  // longest proper palindromic suffix
    Table nxt;  // nxt[{node, x}] = the palindrome x + node + x
    vector<int> sufNode;  // sufNode[r] = longest palindrome ending at r
    // @if numPalsEndingAtR numPalsTotal numPalsEndingAtEachR numPalsEndingAtCurrentR numPalsStartingAtCurrentL
    vector<int> depth{0, 0};  // depth[node] = how many palindromes are suffixes of node (itself included)
    // @endif
    // @if distinctPalsWithCounts
    vector<int> firstEnd{-1, -1};
    // @endif
    // @if minPalPartition
    vector<int> diff{0, 0}, seriesLink{0, 0};
    // @endif
    // @if append+pop+quickLinks
    vector<int> quick{0, 0};  // quick link: lets append skip runs of suffixes preceded by the same item
    // @endif
    // @if append+pop+itemLinks
    // itemLink[node] = for each item x, the longest proper palindromic suffix of node with x right before it (absent: the
    // imaginary root); a plain list, since append copies it anyway
    vector<vector<pair<E, int>>> itemLink = vector<vector<pair<E, int>>>(2);
    // @endif
    // @if append+pop+persistentLinks
    // the same links as a persistent array per palindrome: item -> id, then a binary trie over the id's bits where a new
    // palindrome copies only the O(log alphabet) trie nodes on one path of its suffix link's trie
    struct ItemHash {
        size_t operator()(const E& x) const { return KeyHash::itemHash(x); }
    };
    unordered_map<E, int, ItemHash> idOf;
    vector<int> trieLeft{0}, trieRight{0}, trieVal{0};  // trie node 0 = empty
    vector<int> linkRoot{0, 0}, linkDepth{0, 0};
    vector<int> trieSizeBefore{0, 0};  // trie size before each palindrome was made, to undo it on pop
    // @endif
    // @if pop
    vector<int> parent{0, 0};  // node = x + parent + x
    vector<char> createdAt;  // createdAt[r] = whether position r made a new node
    // @endif
    // @if numDistinctPalsInPrefixEndingAtR numDistinctPalsInPrefixEndingAtEachR
    vector<int> distinctInPrefix;
    // @endif
    // @if longestPalStartingAtCurrentL
    vector<int> palPrefixLen;  // palPrefixLen[r] = longest palindromic prefix of seq[0..r]
    // @endif
    // @if numPalsStartingAtCurrentL
    vector<int> palPrefixNode;  // palPrefixNode[r] = node of the longest palindromic prefix of seq[0..r]
    // @endif
    // @if longestPal
    vector<int> longestUpTo;  // longestUpTo[r] = length of the longest palindrome in seq[0..r]
    // @endif
    // @if numPalsTotal
    long long totalPals = 0;
    // @endif
    // @if rightmostRForPalStartingAtL rightmostRForPalStartingAtEachL
    vector<int> revLens;  // empty = needs rebuilding
    // @endif

    // @if leftmostLForPalEndingAtR rightmostRForPalStartingAtL numDistinctPalsInPrefixEndingAtR numPalsEndingAtR
    void checkIndex(int i) const {
        if (i < 0 || i >= (int)seq.size()) throw out_of_range("index " + to_string(i) + " out of range for an Eertree of length " + to_string(seq.size()));
    }

    // @endif
    // @if append+pop
    // longest palindromic suffix of seq[0..i-1], at or below node, with x right before it
    int findPrecededBy(int node, int i, const E& x) const {
        int j = i - palLen[node] - 1;
        if (j >= 0 && seq[j] == x) return node;
        // @if quickLinks
        while (true) {
            int link = palLink[node];
            if (seq[i - palLen[link] - 1] == x) return link;
            node = quick[node];  // every suffix between link and quick[node] has the same item before it as link does
            j = i - palLen[node] - 1;
            if (j >= 0 && seq[j] == x) return node;
        }
        // @endif
        // @if itemLinks
        for (const auto& [item, to] : itemLink[node]) if (item == x) return to;
        return 0;  // the imaginary root fits any x
        // @endif
        // @if persistentLinks
        auto found = idOf.find(x);
        return found == idOf.end() ? 0 : trieGet(linkRoot[node], linkDepth[node], found->second);
        // @endif
    }

    // @endif
    // @if append+pop+persistentLinks
    int trieGet(int root, int depth, int item) const {
        if (item >> depth) return 0;
        for (int bit = depth - 1; bit >= 0; bit--) {
            root = item >> bit & 1 ? trieRight[root] : trieLeft[root];
            if (!root) return 0;
        }
        return trieVal[root];
    }

    // a new version of the trie with [item] = val, sharing everything off the one path it copies: O(log alphabet)
    pair<int, int> trieSet(int root, int depth, int item, int val) {
        while (item >> depth) {  // too few bits for this item: the old trie becomes the left half of a taller one
            if (root) {
                trieLeft.push_back(root);
                trieRight.push_back(0);
                trieVal.push_back(0);
                root = (int)trieLeft.size() - 1;
            }
            depth++;
        }
        auto copyOf = [&](int from) {
            trieLeft.push_back(trieLeft[from]);
            trieRight.push_back(trieRight[from]);
            trieVal.push_back(trieVal[from]);
            return (int)trieLeft.size() - 1;
        };
        int newRoot = copyOf(root), cur = newRoot;
        for (int bit = depth - 1; bit >= 0; bit--) {
            bool goRight = item >> bit & 1;
            int copy = copyOf(goRight ? trieRight[cur] : trieLeft[cur]);
            (goRight ? trieRight[cur] : trieLeft[cur]) = copy;
            cur = copy;
        }
        trieVal[cur] = val;
        return {newRoot, depth};
    }

    // @endif
    void appendItem(const E& x) {
        int i = (int)seq.size();
        seq.push_back(x);
        // @if append+pop+persistentLinks
        idOf.try_emplace(x, (int)idOf.size());
        // @endif
        // @if append+pop
        int cur = findPrecededBy(i ? sufNode.back() : 1, i, x);
        // @else
        int cur = i ? sufNode.back() : 1;
        while (true) {
            int j = i - palLen[cur] - 1;
            if (j >= 0 && seq[j] == x) break;
            cur = palLink[cur];
        }
        // @endif
        auto found = nxt.find({cur, x});
        int node = found == nxt.end() ? -1 : found->second;
        // @if pop
        createdAt.push_back(node == -1);
        // @endif
        if (node == -1) {
            node = (int)palLen.size();
            palLen.push_back(palLen[cur] + 2);
            int link;
            if (palLen[node] == 1) {
                link = 1;
            } else {
                // @if append+pop
                link = nxt.at({findPrecededBy(palLink[cur], i, x), x});
                // @else
                int t = palLink[cur];
                while (true) {
                    int j = i - palLen[t] - 1;
                    if (j >= 0 && seq[j] == x) break;
                    t = palLink[t];
                }
                link = nxt.at({t, x});
                // @endif
            }
            palLink.push_back(link);
            nxt.emplace(make_pair(cur, x), node);
            // @if numPalsEndingAtR numPalsTotal numPalsEndingAtEachR numPalsEndingAtCurrentR numPalsStartingAtCurrentL
            depth.push_back(depth[link] + 1);
            // @endif
            // @if distinctPalsWithCounts
            firstEnd.push_back(i);
            // @endif
            // @if minPalPartition
            int d = palLen[node] - palLen[link];
            diff.push_back(d);
            seriesLink.push_back(d != diff[link] ? link : seriesLink[link]);
            // @endif
            // @if append+pop+quickLinks
            if (palLen[link] <= 0) quick.push_back(0);
            else if (!(seq[i - palLen[palLink[link]]] == seq[i - palLen[link]])) quick.push_back(palLink[link]);
            else quick.push_back(quick[link]);
            // @endif
            // @if append+pop+itemLinks
            {
                vector<pair<E, int>> links = itemLink[link];  // node's proper suffixes are link and link's proper suffixes
                const E& before = seq[i - palLen[link]];  // the item right before link inside node
                bool found = false;
                for (auto& [item, to] : links) if (item == before) { to = link; found = true; }
                if (!found) links.emplace_back(before, link);
                itemLink.push_back(move(links));
            }
            // @endif
            // @if append+pop+persistentLinks
            {
                trieSizeBefore.push_back((int)trieLeft.size());
                auto [root, depth] = trieSet(linkRoot[link], linkDepth[link], idOf.at(seq[i - palLen[link]]), link);
                linkRoot.push_back(root);
                linkDepth.push_back(depth);
            }
            // @endif
            // @if pop
            parent.push_back(cur);
            // @endif
        }
        sufNode.push_back(node);
        // @if numDistinctPalsInPrefixEndingAtR numDistinctPalsInPrefixEndingAtEachR
        distinctInPrefix.push_back((int)palLen.size() - 2);
        // @endif
        // @if longestPalStartingAtCurrentL
        palPrefixLen.push_back(palLen[node] == i + 1 ? i + 1 : (i ? palPrefixLen.back() : 0));
        // @endif
        // @if numPalsStartingAtCurrentL
        palPrefixNode.push_back(palLen[node] == i + 1 ? node : palPrefixNode.back());
        // @endif
        // @if longestPal
        longestUpTo.push_back(max(palLen[node], i ? longestUpTo.back() : 0));
        // @endif
        // @if numPalsTotal
        totalPals += depth[node];
        // @endif
        // @if rightmostRForPalStartingAtL rightmostRForPalStartingAtEachL
        revLens.clear();
        // @endif
    }
    // @if rightmostRForPalStartingAtL rightmostRForPalStartingAtEachL

    const vector<int>& reversedLongestPalSuffix() {
        if (revLens.empty() && !seq.empty()) {
            vector<E> rev(seq.rbegin(), seq.rend());
            vector<int> len{-1, 0}, link{0, 0};
            Table next;
            int last = 1;
            for (int i = 0; i < (int)rev.size(); i++) {
                const E& x = rev[i];
                int cur = last;
                while (true) {
                    int j = i - len[cur] - 1;
                    if (j >= 0 && rev[j] == x) break;
                    cur = link[cur];
                }
                auto found = next.find({cur, x});
                int node;
                if (found != next.end()) {
                    node = found->second;
                } else {
                    node = (int)len.size();
                    len.push_back(len[cur] + 2);
                    int l = 1;
                    if (len[node] != 1) {
                        int t = link[cur];
                        while (true) {
                            int j = i - len[t] - 1;
                            if (j >= 0 && rev[j] == x) break;
                            t = link[t];
                        }
                        l = next.at({t, x});
                    }
                    link.push_back(l);
                    next.emplace(make_pair(cur, x), node);
                }
                last = node;
                revLens.push_back(len[node]);
            }
        }
        return revLens;
    }
    // @endif
};
