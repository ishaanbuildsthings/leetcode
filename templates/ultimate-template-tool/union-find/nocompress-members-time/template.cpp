// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/union-find/nocompress-members-time/template.cpp
// @operations: areUnioned connectedAt elementsInGroup find firstConnectedTime groups largestSize numComponents roots size sizes unite uniteAUnderB
// @data-structure-type: dsu-nocompress
// @complexities:
//   areUnioned: log(N)
//   connectedAt: log(N)
//   elementsInGroup: K
//   find: log(N)
//   firstConnectedTime: log(N)
//   groups: N*log(N)
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
//   other: vals[1*N] nxt[1*N] tm[1*N]
//   note: K = the size of the group; uniteAUnderB skips union by size, so after it any walk up the forest can take O(N)
#include <bits/stdc++.h>
using namespace std;
using ll = long long;

// DSUNoCompress<int> dsu(vals);
// vals: the elements (any type: numbers, strings, pairs, ...); everything works on their indices 0..n-1
template <typename T>
struct DSUNoCompress {
    vector<T> vals;
    vector<int> par, sz;
    int comps, mx;
    vector<int> nxt;  // each component's members linked in a circle: i -> nxt[i] -> ... -> i
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
        nxt = par;
        tm.assign(n, INT_MAX);
    }

    // O(log n), index of the representative of i's component; parents are never rewritten, so the forest records every merge
    int find(int i) {
        while (par[i] != i) i = par[i];
        return i;
    }

    // O(log n), merges the two components, returns {winner, loser}: the new root and the old root now under it,
    // or {-1, -1} if they were already together
    // each call is the next unite in time (0, 1, 2, ...), failed ones too
    pair<int, int> unite(int i, int j) {
        int t = time++;
        i = find(i), j = find(j);
        if (i == j) {
            return {-1, -1};
        }
        if (sz[i] < sz[j]) swap(i, j);
        par[j] = i;
        sz[i] += sz[j];
        comps--;
        mx = max(mx, sz[i]);
        swap(nxt[i], nxt[j]);  // (joins the two circles)
        tm[j] = t;
        return {i, j};
    }

    // O(log n), forces a's root under b's root, false if already together
    // skips union by size, so depth can degrade to O(n) and every walk with it
    bool uniteAUnderB(int a, int b) {
        int t = time++;
        a = find(a), b = find(b);
        if (a == b) return false;
        par[a] = b;
        sz[b] += sz[a];
        comps--;
        mx = max(mx, sz[b]);
        swap(nxt[b], nxt[a]);  // (joins the two circles)
        tm[a] = t;
        return true;
    }

    // O(log n), true if i and j are in the same component
    bool areUnioned(int i, int j) { return find(i) == find(j); }

    // O(log n), how many elements are in i's component
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

    // O(log n), how many unites (failed ones too) it took for i and j to end up together: 0 if i == j, -1 if
    // they still aren't. Climbs from both ends, always moving the one that got its parent first
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
    bool connectedAt(int i, int j, int t) {
        int f = firstConnectedTime(i, j);
        return f != -1 && f <= t;
    }
};
