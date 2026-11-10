// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/union-find/nocompress-merge-members-edges-time/template.cpp
// @operations: areUnioned componentData connectedAt edgeCount elementsInGroup find firstConnectedTime groups isTree largestSize numComponents roots size sizes unite uniteAUnderB
// @data-structure-type: dsu-nocompress
// @complexities:
//   areUnioned: log(N)
//   componentData: log(N)
//   connectedAt: log(N)
//   edgeCount: log(N)
//   elementsInGroup: K
//   find: log(N)
//   firstConnectedTime: log(N)
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
//   other: vals[1*N] data[1*N] nxt[1*N] edges[1*N] tm[1*N]
//   note: K = the size of the group; uniteAUnderB skips union by size, so it can build a chain N deep: every log(N) above (and the N*log(N) of groups) holds only if you never call it, otherwise those calls are O(N) (O(N^2)); data holds one Node per element
#include <bits/stdc++.h>
using namespace std;
using ll = long long;

// e.g. long long, string, pair, struct, ...
using RawVal = long long;

struct Node {
    // long long tot;
    // long long mx;
};

Node baseFn(const RawVal& v, int i) {
    // Node res;
    // res.tot = v, res.mx = v;
    // return res;
}

// called once per merge: big is the bigger component's Node (on a tie, either one). big is moved in, so adding small's
// items into big and returning it costs O(size of small) (small-to-large: O(n log n) in total)
Node combine(Node big, const Node& small) {
    // Node res;
    // res.tot = big.tot + small.tot;
    // res.mx = max(big.mx, small.mx);
    // return res;
}


// DSUNoCompress dsu(vals);
// vals: the elements (any type: numbers, strings, pairs, ...); everything works on their indices 0..n-1
struct DSUNoCompress {
    using T = RawVal;
    vector<T> vals;
    vector<int> par, sz;
    int comps, mx;
    vector<Node> data;  // data[root]: the Node of root's component
    vector<int> nxt;  // each component's members linked in a circle: i -> nxt[i] -> ... -> i
    vector<int> edges;  // edges[root]: how many unites touched root's component, merging or not
    int time = 0;  // how many unites so far, failed ones too
    vector<int> tm;  // tm[i]: the unite (0, 1, 2, ...) that gave i its parent, INT_MAX at a root

    // O(n), every element starts in its own component
    DSUNoCompress(const vector<T>& vals) : vals(vals) {
        int n = vals.size();
        par.resize(n);
        iota(par.begin(), par.end(), 0);
        sz.assign(n, 1);
        comps = n;
        mx = n ? 1 : 0;
        for (int i = 0; i < n; i++) data.push_back(baseFn(vals[i], i));
        nxt = par;
        edges.assign(n, 0);
        tm.assign(n, INT_MAX);
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
    // each call is the next unite in time (0, 1, 2, ...), failed ones too
    // only O(log n) if you never call uniteAUnderB: forced unions can build a chain, then this is O(n)
    pair<int, int> unite(int i, int j) {
        int t = time++;
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
        data[i] = combine(move(data[i]), data[j]);
        swap(nxt[i], nxt[j]);  // (joins the two circles)
        edges[i] += edges[j] + 1;
        tm[j] = t;
        return {i, j};
    }

    // O(log n), forces a's root under b's root, false if already together
    // skips union by size, so these can build a chain n deep: then this, find, unite and every other call that
    // walks up is O(n); their O(log n) holds only if you never force unions
    // combine gets b's component's Node first here, even when it's the smaller one
    bool uniteAUnderB(int a, int b) {
        int t = time++;
        a = find(a), b = find(b);
        if (a == b) {
            edges[a]++;
            return false;
        }
        par[a] = b;
        sz[b] += sz[a];
        comps--;
        mx = max(mx, sz[b]);
        data[b] = combine(move(data[b]), data[a]);
        swap(nxt[b], nxt[a]);  // (joins the two circles)
        edges[b] += edges[a] + 1;
        tm[a] = t;
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

    // O(log n), the Node of i's component: every member's baseFn, combined
    // only O(log n) if you never call uniteAUnderB: forced unions can build a chain, then this is O(n)
    Node componentData(int i) { return data[find(i)]; }

    // O(log n), how many unites have touched i's component (merging or not): its edges, if each unite is an edge
    // only O(log n) if you never call uniteAUnderB: forced unions can build a chain, then this is O(n)
    int edgeCount(int i) { return edges[find(i)]; }

    // O(log n), true if i's component has no cycle: exactly size - 1 edges
    // only O(log n) if you never call uniteAUnderB: forced unions can build a chain, then this is O(n)
    bool isTree(int i) {
        int r = find(i);
        return edges[r] == sz[r] - 1;
    }

    // O(log n), how many unites (failed ones too) it took for i and j to end up together: 0 if i == j, -1 if
    // they still aren't. Climbs from both ends, always moving the one that got its parent first
    // only O(log n) if you never call uniteAUnderB: forced unions can build a chain, then this is O(n)
    int firstConnectedTime(int i, int j) {
        if (find(i) != find(j)) return -1;
        int last = -1;
        while (i != j) {
            if (tm[i] < tm[j]) last = max(last, tm[i]), i = par[i];
            else last = max(last, tm[j]), j = par[j];
        }
        return last + 1;
    }

    // O(log n), were i and j together after the first t unites
    // only O(log n) if you never call uniteAUnderB: forced unions can build a chain, then this is O(n)
    bool connectedAt(int i, int j, int t) {
        int f = firstConnectedTime(i, j);
        return f != -1 && f <= t;
    }
};
