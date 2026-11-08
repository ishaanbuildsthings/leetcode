// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/strings/longestCommonSubstring.cpp
#include <bits/stdc++.h>
using namespace std;
using ll = long long;

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

// longest contiguous run appearing in both a and b, as {length, startInA, startInB}
// ties go to the earliest start in b, then the earliest start in a; no common item -> {0, 0, 0}
// a and b can be different containers (e.g. string and vector<char>) of any element type that has == and a hash
// auto [len, startA, startB] = longestCommonSubstring(string("xabcdy"), string("zzbcdq"));   // {3, 2, 2}: "bcd"
// longestCommonSubstring(vector<int>{5, -1, 2, 7}, vector<int>{-1, 2, 9}) -> {2, 1, 0}   // {-1, 2}
// O(n + m) expected time, O(n) space (n = a size, m = b size)
template <class T1, class T2>
tuple<int, int, int> longestCommonSubstring(const T1& a, const T2& b) {
    using E = typename T1::value_type;
    // suffix automaton of a: each state is a group of substrings sharing their end positions, with lengths in (len[link], len]
    ChildTable<E> nxt;
    nxt.addNode();
    vector<int> link{-1}, len{0}, firstEnd{-1};  // firstEnd[state] = earliest index in a where its substrings end
    int last = 0;
    for (int i = 0; i < (int)a.size(); i++) {
        const E& c = a[i];
        int cur = nxt.addNode();
        len.push_back(len[last] + 1);
        link.push_back(0);
        firstEnd.push_back(i);
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
                firstEnd.push_back(firstEnd[q]);
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
    // walk b through it, keeping the longest suffix of b[..j] that appears in a
    int state = 0, matched = 0, best = 0, bestState = 0, bestEndB = 0;
    for (int j = 0; j < (int)b.size(); j++) {
        E c = b[j];
        while (state && nxt.get(state, c) == -1) {
            state = link[state];
            matched = len[state];
        }
        int to = nxt.get(state, c);
        if (to != -1) {
            state = to;
            matched++;
        }
        if (matched > best) {
            best = matched;
            bestState = state;
            bestEndB = j;
        }
    }
    if (best == 0) return {0, 0, 0};
    return {best, firstEnd[bestState] - best + 1, bestEndB - best + 1};
}
