// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/strings/multiPatternMatches.cpp
#include <bits/stdc++.h>
using namespace std;

#ifndef CHILD_TABLE_DEFINED
#define CHILD_TABLE_DEFINED
// node -> (item -> child) for tries / automata, in one hash table keyed by (node, item): O(1) expected per lookup whatever
// the alphabet, with a per-run random seed so crafted inputs can't make it collide; get returns -1 when there's no child
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
        static uint64_t itemHash(const pair<A, B>& p) { return mix(itemHash(p.first) * 0x9e3779b97f4a7c15ULL + itemHash(p.second)); }
        size_t operator()(const pair<int, E>& key) const { return mix(itemHash(key.second) + (uint64_t)key.first * 0x9e3779b97f4a7c15ULL); }
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

// vector of size patterns.size(): res[k] = every index i where text[i...] matches patterns[k], ascending (overlaps included, Aho-Corasick)
// an empty pattern matches at every i in 0..text.size(); duplicate patterns each get their own list
// text and the patterns can be different containers (e.g. string and vector<char>) of any element type that has == and a hash
// multiPatternMatches(string("ababa"), vector<string>{"aba", "b", "ab", "zz"}) -> {{0, 2}, {1, 3}, {0, 2}, {}}
// multiPatternMatches(vector<int>{-1, 2, -1, 2}, vector<vector<int>>{{-1, 2}, {2}}) -> {{0, 2}, {1, 3}}
// O(n + m + n * sqrt(m)) expected time (m = total pattern length), worst case when the output is huge: patterns of the same length are
// different, so together they match at most n indices, and total length m allows at most about sqrt(2m) different lengths,
// so there are at most n * sqrt(2m) matches (duplicate patterns each get their own copy); use multiPatternCounts for just counts
template <class T1, class T2>
vector<vector<int>> multiPatternMatches(const T1& text, const vector<T2>& patterns) {
    // trie of the patterns; fail[node] = node of the longest proper suffix of node's path that is also a trie path
    using E = typename T2::value_type;
    ChildTable<E> children;
    children.addNode();
    vector<int> nodeOf;
    for (const auto& pattern : patterns) {
        int node = 0;
        for (const auto& c : pattern) {
            int child = children.get(node, c);
            if (child == -1) {
                child = children.addNode();
                children.set(node, c, child);
            }
            node = child;
        }
        nodeOf.push_back(node);
    }
    vector<char> isEnd(children.size(), 0);
    for (int k = 0; k < (int)patterns.size(); k++) if (nodeOf[k]) isEnd[nodeOf[k]] = 1;
    vector<int> endLink(children.size(), 0);  // nearest node down the fail chain where some pattern ends (0 = none)
    vector<int> fail(children.size(), 0), order{0};  // order: BFS, parents before children
    for (int idx = 0; idx < (int)order.size(); idx++) {
        int node = order[idx];
        for (const E& c : children.items(node)) {
            int child = children.get(node, c);
            if (node) {
                int f = fail[node];
                while (f && children.get(f, c) == -1) f = fail[f];
                fail[child] = max(children.get(f, c), 0);
            }
            endLink[child] = isEnd[fail[child]] ? fail[child] : endLink[fail[child]];
            order.push_back(child);
        }
    }
    // ends[node] = every text index where the pattern ending at node ends
    vector<vector<int>> ends(children.size());
    int node = 0;
    for (int i = 0; i < (int)text.size(); i++) {
        E c = text[i];
        while (node && children.get(node, c) == -1) node = fail[node];
        node = max(children.get(node, c), 0);
        for (int out = isEnd[node] ? node : endLink[node]; out; out = endLink[out]) ends[out].push_back(i);
    }
    vector<vector<int>> res(patterns.size());
    for (int k = 0; k < (int)patterns.size(); k++) {
        int m = (int)patterns[k].size();
        if (m == 0) {
            res[k].resize(text.size() + 1);
            iota(res[k].begin(), res[k].end(), 0);
        } else {
            for (int e : ends[nodeOf[k]]) res[k].push_back(e - m + 1);
        }
    }
    return res;
}
