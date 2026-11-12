// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/strings/multiPatternLongestPrefixInText.cpp
#include <bits/stdc++.h>
using namespace std;

#ifndef CHILD_TABLE_DEFINED
#define CHILD_TABLE_DEFINED
// node -> (item -> child) for tries / automata, in one hash table keyed by (node, item): O(1) expected per lookup
// whatever the alphabet, with a per-run random seed so crafted inputs can't make it collide; get returns -1 when
// there's no child
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

// vector of size patterns.size(): res[i] = longest L such that the first L items of patterns[i] appear somewhere in
// text (0 if none)
// text and the patterns can be different containers (e.g. string and vector<char>) of any element type that has == and
// a hash
// multiPatternLongestPrefixInText(string("xabcaby"), vector<string>{"abd", "cab", "zz"}) -> {2, 3, 0}
// multiPatternLongestPrefixInText(vector<int>{-1, 2, -1, 5}, vector<vector<int>>{{2, -1, 2}, {5, 9}}) -> {2, 1}
// O(n + m) expected time, O(n) space (n = text size, m = total pattern length)
template <class T1, class T2>
vector<int> multiPatternLongestPrefixInText(const T1& text, const vector<T2>& patterns) {
    using E = typename T1::value_type;
    // suffix automaton of text: each state is a group of substrings sharing their end positions, with lengths in
    // (len[link], len]
    ChildTable<E> nxt;
    nxt.addNode();
    vector<int> link{-1}, len{0};
    int last = 0;
    for (const auto& c : text) {
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
            if (len[p] + 1 == len[q]) {
                link[cur] = q;
            } else {
                int clone = nxt.copyNode(q);
                len.push_back(len[p] + 1);
                link.push_back(link[q]);
                while (p != -1 && nxt.get(p, c) == q) {
                    nxt.set(p, c, clone);
                    p = link[p];
                }
                link[q] = clone;
                link[cur] = clone;
            }
        }
        last = cur;
    }
    // walk each pattern in from the start: it stays inside the automaton exactly while its prefix appears in text
    vector<int> res;
    res.reserve(patterns.size());
    for (const auto& pattern : patterns) {
        int state = 0, matched = 0;
        for (const auto& c : pattern) {
            int to = nxt.get(state, c);
            if (to == -1) break;
            state = to;
            matched++;
        }
        res.push_back(matched);
    }
    return res;
}
