// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/union-find/nocompress-members-edges-grow/template.cpp
// @operations: add areUnioned edgeCount elementsInGroup find groups isTree largestSize numComponents roots size sizes unite uniteAUnderB
// @data-structure-type: dsu-nocompress
// @complexities:
//   add: 1 amortized
//   areUnioned: log(N)
//   edgeCount: log(N)
//   elementsInGroup: K
//   find: log(N)
//   groups: N*log(N)
//   isTree: log(N)
//   largestSize: 1
//   numComponents: 1
//   roots: N
//   size: log(N)
//   sizes: N*log(N)
//   unite: log(N)
//   uniteAUnderB: log(N)
//   build: N
// @memory:
//   layout: none
//   node: par[1*N] sz[1*N]
//   tags: none
//   other: vals[1*N] nxt[1*N] edges[1*N]
//   note: K = the size of the group; uniteAUnderB skips union by size, so it can build a chain N deep: every log(N) above (and the N*log(N) of groups) holds only if you never call it, otherwise those calls are O(N) (O(N^2))
#include <bits/stdc++.h>
using namespace std;
using ll = long long;

// DSUNoCompress<int> dsu(vals);
// vals: the elements (any type: numbers, strings, pairs, ...); everything works on their indices 0..n-1, and add(val)
// appends more
template <typename T>
struct DSUNoCompress {
    vector<T> vals;
    vector<int> par, sz;
    int comps, mx;
    vector<int> nxt;  // each component's members linked in a circle: i -> nxt[i] -> ... -> i
    vector<int> edges;  // edges[root]: how many unites touched root's component, merging or not

    // O(n), every element starts in its own component
    DSUNoCompress(const vector<T>& vals = {}) : vals(vals) {
        int n = vals.size();
        par.resize(n);
        iota(par.begin(), par.end(), 0);
        sz.assign(n, 1);
        comps = n;
        mx = n ? 1 : 0;
        nxt = par;
        edges.assign(n, 0);
    }

    // O(log n), index of the representative of i's component; parents are never rewritten, so the forest records every
    // merge
    // only O(log n) if you never call uniteAUnderB: forced unions can build a chain, then this is O(n)
    int find(int i) {
        while (par[i] != i) i = par[i];
        return i;
    }

    // O(log n), merges the two components, returns {winner, loser}: the new root and the old root now under it,
    // or {-1, -1} if they were already together
    // either way it counts as an edge of the component (edgeCount)
    // only O(log n) if you never call uniteAUnderB: forced unions can build a chain, then this is O(n)
    pair<int, int> unite(int i, int j) {
        i = find(i), j = find(j);
        if (i == j) {
            edges[i]++;
            return {-1, -1};
        }
        if (sz[i] < sz[j]) swap(i, j);
        par[j] = i;
        sz[i] += sz[j];
        comps--;
        mx = max(mx, sz[i]);
        swap(nxt[i], nxt[j]);  // (joins the two circles)
        edges[i] += edges[j] + 1;
        return {i, j};
    }

    // O(log n), forces a's root under b's root, false if already together
    // skips union by size, so these can build a chain n deep: then this, find, unite and every other call that
    // walks up is O(n); their O(log n) holds only if you never force unions
    bool uniteAUnderB(int a, int b) {
        a = find(a), b = find(b);
        if (a == b) {
            edges[a]++;
            return false;
        }
        par[a] = b;
        sz[b] += sz[a];
        comps--;
        mx = max(mx, sz[b]);
        swap(nxt[b], nxt[a]);  // (joins the two circles)
        edges[b] += edges[a] + 1;
        return true;
    }

    // O(log n), true if i and j are in the same component
    // only O(log n) if you never call uniteAUnderB: forced unions can build a chain, then this is O(n)
    bool areUnioned(int i, int j) { return find(i) == find(j); }

    // O(log n), how many elements are in i's component
    // only O(log n) if you never call uniteAUnderB: forced unions can build a chain, then this is O(n)
    int size(int i) { return sz[find(i)]; }

    // O(1), how many components exist right now
    int numComponents() { return comps; }

    // O(1), size of the biggest component, maintained in unite
    int largestSize() { return mx; }

    // O(n), one index per component: the representative each member's find returns
    vector<int> roots() {
        vector<int> res;
        for (int i = 0; i < (int)par.size(); i++)
            if (par[i] == i) res.push_back(i);
        return res;
    }

    // O(n log n), the sizes of all components, biggest first, e.g. [4, 2, 1]
    vector<int> sizes() {
        vector<int> res;
        for (int i = 0; i < (int)par.size(); i++)
            if (par[i] == i) res.push_back(sz[i]);
        sort(res.rbegin(), res.rend());
        return res;
    }

    // O(n log n), groupsArr[rt] = values whose root is rt, empty if rt is not a root
    // only O(n log n) if you never call uniteAUnderB: forced unions can build a chain, then this is O(n^2)
    vector<vector<T>> groups() {
        int n = par.size();
        vector<vector<T>> groupsArr(n);
        for (int i = 0; i < n; i++) groupsArr[find(i)].push_back(vals[i]);
        return groupsArr;
    }

    // O(size of the group), the values of every element in the same group as index i, starting at i
    vector<T> elementsInGroup(int i) {
        vector<T> res = {vals[i]};
        for (int j = nxt[i]; j != i; j = nxt[j]) res.push_back(vals[j]);
        return res;
    }

    // O(log n), how many unites have touched i's component (merging or not): its edges, if each unite is an edge
    // only O(log n) if you never call uniteAUnderB: forced unions can build a chain, then this is O(n)
    int edgeCount(int i) { return edges[find(i)]; }

    // O(log n), true if i's component has no cycle: exactly size - 1 edges
    // only O(log n) if you never call uniteAUnderB: forced unions can build a chain, then this is O(n)
    bool isTree(int i) {
        int r = find(i);
        return edges[r] == sz[r] - 1;
    }

    // O(1), adds a new element in its own component and returns its index
    int add(const T& val) {
        int i = par.size();
        vals.push_back(val);
        par.push_back(i);
        sz.push_back(1);
        comps++;
        mx = max(mx, 1);
        nxt.push_back(i);
        edges.push_back(0);
        return i;
    }
};
