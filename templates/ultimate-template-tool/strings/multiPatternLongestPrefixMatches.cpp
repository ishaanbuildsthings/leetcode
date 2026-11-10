// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/strings/multiPatternLongestPrefixMatches.cpp
#include <bits/stdc++.h>
using namespace std;

#ifndef CHILD_TABLE_DEFINED
#define CHILD_TABLE_DEFINED
// node -> (item -> child) for tries / automata, in one hash table keyed by (node, item): O(1) expected per lookup
// whatever
// the alphabet, with a per-run random seed so crafted inputs can't make it collide; get returns -1 when there's no
// child
template <class E>
struct ChildTable {
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
    unordered_map<pair<int, E>, int, KeyHash> table;
    vector<vector<E>> itemsOf;  // itemsOf[node] = the items node has a child on, in the order they were added

    int size() const { return (int)itemsOf.size(); }
    int addNode() {
        itemsOf.emplace_back();
        return (int)itemsOf.size() - 1;
    }
    int get(int node, const E& x) const {
        auto it = table.find({node, x});
        return it == table.end() ? -1 : it->second;
    }
    void set(int node, const E& x, int child) {
        auto [it, isNew] = table.try_emplace({node, x}, child);
        if (isNew) itemsOf[node].push_back(x);
        else it->second = child;
    }
    int copyNode(int from) {  // a new node with the same children as from
        int node = addNode();
        for (const E& x : itemsOf[from]) set(node, x, table.at({from, x}));
        return node;
    }
    const vector<E>& items(int node) const { return itemsOf[node]; }
};
#endif

// vector of size text.size(): res[idx] = longest L such that text[idx .. idx + L) is a prefix of some pattern (0 if
// none)
// text and the patterns can be different containers (e.g. string and vector<char>) of any element type that has == and
// a hash
// multiPatternLongestPrefixMatches(string("abcab"), vector<string>{"abd", "bca", "x"}) -> {2, 3, 0, 2, 1}
// multiPatternLongestPrefixMatches(vector<int>{-1, 2, -1, 5}, vector<vector<int>>{{-1, 2, -1, 2}, {5, 9}}) -> {3, 0, 1,
// 1}
// O(n + m) expected time, O(m) space (n = text size, m = total pattern length)
template <class T1, class T2>
vector<int> multiPatternLongestPrefixMatches(const T1& text, const vector<T2>& patterns) {
    // reversed, "text[idx .. idx + L) is a prefix of a pattern" becomes "the reversed text's run of length L ending at
    // mirrored idx is a suffix of a reversed pattern": suffix automaton over every reversed pattern
    using E = typename T2::value_type;
    ChildTable<E> nxt;
    nxt.addNode();
    vector<int> link{-1}, len{0};
    auto cloneOf = [&](int p, int q, const E& c) {
        int clone = nxt.copyNode(q);
        len.push_back(len[p] + 1);
        link.push_back(link[q]);
        while (p != -1 && nxt.get(p, c) == q) {
            nxt.set(p, c, clone);
            p = link[p];
        }
        link[q] = clone;
        return clone;
    };
    auto extend = [&](int last, const E& c) {
        int q = nxt.get(last, c);
        if (q != -1) {
            return len[last] + 1 == len[q] ? q : cloneOf(last, q, c);
        }
        int cur = nxt.addNode();
        len.push_back(len[last] + 1);
        link.push_back(0);
        int p = last;
        while (p != -1 && nxt.get(p, c) == -1) {
            nxt.set(p, c, cur);
            p = link[p];
        }
        if (p != -1) {
            int q = nxt.get(p, c);
            link[cur] = len[p] + 1 == len[q] ? q : cloneOf(p, q, c);
        }
        return cur;
    };
    vector<int> ends;
    for (const auto& pattern : patterns) {
        int last = 0;
        for (auto it = pattern.rbegin(); it != pattern.rend(); ++it) last = extend(last, *it);
        ends.push_back(last);
    }
    int states = (int)nxt.size();
    // isSuffix[state]: its runs are suffixes of some reversed pattern (states on the link path up from a pattern's end)
    vector<char> isSuffix(states, 0);
    isSuffix[0] = 1;
    for (int state : ends) {
        while (!isSuffix[state]) {
            isSuffix[state] = 1;
            state = link[state];
        }
    }
    // nearestSuffix[state] = closest state at or above it (by links) whose runs are suffixes; counting sort by length
    int maxLen = *max_element(len.begin(), len.end());
    vector<int> cnt(maxLen + 2, 0), order(states), nearestSuffix(states, 0);
    for (int state = 0; state < states; state++) cnt[len[state] + 1]++;
    for (int L = 1; L <= maxLen + 1; L++) cnt[L] += cnt[L - 1];
    for (int state = 0; state < states; state++) order[cnt[len[state]]++] = state;
    for (int state : order) nearestSuffix[state] = isSuffix[state] ? state : nearestSuffix[link[state]];
    int n = (int)text.size();
    vector<int> res(n, 0);
    int state = 0, matched = 0;
    for (int pos = n - 1; pos >= 0; pos--) {  // walk the reversed text
        E c = text[pos];
        while (state && nxt.get(state, c) == -1) {
            state = link[state];
            matched = len[state];
        }
        int to = nxt.get(state, c);
        if (to != -1) {
            state = to;
            matched++;
        }
        res[pos] = isSuffix[state] ? matched : len[nearestSuffix[state]];
    }
    return res;
}
