// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/strings/DoubleEndedEertree.cpp
#include <bits/stdc++.h>
using namespace std;

// Palindromic tree (eertree) that grows at both ends. A palindrome's longest palindromic suffix is also its longest
// palindromic prefix, so one set of links serves both sides; it tracks the longest palindromic suffix and prefix of the
// whole sequence. Only whole-sequence queries: prepending changes the answers at existing positions.
// works on any element type that has == and a hash (char, int, long long, string, pair of those, ...); E is the element type
// DoubleEndedEertree<char> et("aba");
// DoubleEndedEertree<int> et(vector<int>{-1, 2, -1});
// DoubleEndedEertree<int> et;   // empty, then append / appendLeft
template <class E>
class DoubleEndedEertree {
public:
    // O(n) expected time, O(n) space
    DoubleEndedEertree() {}
    template <class C>
    explicit DoubleEndedEertree(const C& arrOrString) {
        for (const auto& x : arrOrString) appendItem(x);
    }
    explicit DoubleEndedEertree(const char* arrOrString) : DoubleEndedEertree(string(arrOrString)) {}  // a string literal like "abaab"

    // @if append
    // O(1) amortized expected -- adds x to the end
    void append(const E& x) { appendItem(x); }

    // @endif
    // @if appendLeft
    // O(1) amortized expected -- adds x to the front
    void appendLeft(const E& x) {
        seq.push_front(x);
        int n = (int)seq.size();
        auto fits = [&](int t) {  // x + t + x as a prefix: the item after prefix t is x
            int j = palLen[t] + 1;
            return j < n && seq[j] == x;
        };
        int cur = preNode;
        while (!fits(cur)) cur = palLink[cur];
        int node = preNode = child(cur, x, fits);
        if (palLen[node] == n) sufNode = node;
        // @if numPalsTotal
        totalPals += depth[node];  // every palindrome starting at the new item
        // @endif
    }

    // @endif
    // @if longestPalEndingAtCurrentR
    // O(1) -- length of the longest palindrome ending at the current right end (0 if empty)
    int longestPalEndingAtCurrentR() const { return palLen[sufNode]; }

    // @endif
    // @if longestPalStartingAtCurrentL
    // O(1) -- length of the longest palindrome starting at the current left end (0 if empty)
    int longestPalStartingAtCurrentL() const { return palLen[preNode]; }

    // @endif
    // @if numDistinctPals
    // O(1) -- how many distinct palindromic substrings the sequence has, at most n
    int numDistinctPals() const { return (int)palLen.size() - 2; }

    // @endif
    // @if numPalsTotal
    // O(1) -- total palindromic substrings counted with multiplicity ("aa" has 3: a, a, aa)
    long long numPalsTotal() const { return totalPals; }

    // @endif
    // @if longestPal
    // O(1) -- length of the longest palindromic substring (0 if empty)
    int longestPal() const { return longest; }

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

    deque<E> seq;  // O(1) access anywhere
    vector<int> palLen{-1, 0};  // node 0 = the imaginary length -1 root, node 1 = the empty palindrome
    vector<int> palLink{0, 0};  // longest proper palindromic suffix (= longest proper palindromic prefix)
    Table nxt;  // nxt[{node, x}] = the palindrome x + node + x
    int sufNode = 1, preNode = 1;  // longest palindromic suffix / prefix of the whole sequence
    // @if numPalsTotal numPalsEndingAtCurrentR numPalsStartingAtCurrentL
    vector<int> depth{0, 0};  // depth[node] = how many palindromes are suffixes of node (itself included)
    // @endif
    // @if numPalsTotal
    long long totalPals = 0;
    // @endif
    // @if longestPal
    int longest = 0;
    // @endif

    // the node x + cur + x, made if new; fits(t) says whether x + t + x fits on this side (for the new node's link)
    template <class Fits>
    int child(int cur, const E& x, Fits fits) {
        auto found = nxt.find({cur, x});
        if (found != nxt.end()) return found->second;
        int node = (int)palLen.size();
        palLen.push_back(palLen[cur] + 2);
        int link = 1;
        if (palLen[node] != 1) {
            int t = palLink[cur];
            while (!fits(t)) t = palLink[t];
            link = nxt.at({t, x});
        }
        palLink.push_back(link);
        nxt.emplace(make_pair(cur, x), node);
        // @if numPalsTotal numPalsEndingAtCurrentR numPalsStartingAtCurrentL
        depth.push_back(depth[link] + 1);
        // @endif
        // @if longestPal
        longest = max(longest, palLen[node]);
        // @endif
        return node;
    }

    void appendItem(const E& x) {
        seq.push_back(x);
        int n = (int)seq.size(), i = n - 1;
        auto fits = [&](int t) {  // x + t + x as a suffix: the item before suffix t is x
            int j = i - palLen[t] - 1;
            return j >= 0 && seq[j] == x;
        };
        int cur = sufNode;
        while (!fits(cur)) cur = palLink[cur];
        int node = sufNode = child(cur, x, fits);
        if (palLen[node] == n) preNode = node;  // the whole sequence is a palindrome
        // @if numPalsTotal
        totalPals += depth[node];  // every palindrome ending at the new item
        // @endif
    }

public:
    // @if numPalsEndingAtCurrentR
    // O(1) -- how many palindromic substrings end at the current right end
    int numPalsEndingAtCurrentR() const { return depth[sufNode]; }

    // @endif
    // @if numPalsStartingAtCurrentL
    // O(1) -- how many palindromic substrings start at the current left end
    int numPalsStartingAtCurrentL() const { return depth[preNode]; }

    // @endif
};
