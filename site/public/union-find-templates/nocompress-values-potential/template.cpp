// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/union-find/nocompress-values-potential/template.cpp
// @operations: areUnioned componentMax componentMin componentSum diff elementsInGroup find groups largestSize numComponents roots size sizes uniteAUnderBWeighted uniteWeighted
// @data-structure-type: dsu-nocompress
// @complexities:
//   areUnioned: log(N)
//   componentMax: log(N)
//   componentMin: log(N)
//   componentSum: log(N)
//   diff: log(N)
//   elementsInGroup: N*log(N)
//   find: log(N)
//   groups: N*log(N)
//   largestSize: 1
//   numComponents: 1
//   roots: N
//   size: log(N)
//   sizes: N*log(N)
//   uniteAUnderBWeighted: log(N)
//   uniteWeighted: log(N)
//   build: N
// @memory:
//   layout: none
//   node: par[1*N] sz[1*N]
//   tags: none
//   other: vals[1*N] csum[1*N] cmin[1*N] cmax[1*N] pot[1*N]
//   note: uniteAUnderB skips union by size, so after it any walk up the forest can take O(N)
#include <bits/stdc++.h>
using namespace std;
using ll = long long;

// DSUNoCompress<int> dsu(vals);
// vals: the elements (numbers: componentSum / Min / Max are over them); everything works on their indices 0..n-1
// potential: every element has a hidden number value[i]; uniteWeighted(i, j, w) says value[j] - value[i] = w and diff(i, j)
// reads it back (for parity / two-colouring, swap + and - for ^ throughout)
template <typename T>
struct DSUNoCompress {
    vector<T> vals;
    vector<int> par, sz;
    int comps, mx;
    vector<long long> csum;  // at each root: the sum, min and max of its component's values
    vector<T> cmin, cmax;
    vector<long long> pot;  // pot[i] = value[i] - value[par[i]] (0 at a root)

    // O(n), every element starts in its own component
    DSUNoCompress(const vector<T>& vals) : vals(vals) {
        int n = vals.size();
        par.resize(n);
        iota(par.begin(), par.end(), 0);
        sz.assign(n, 1);
        comps = n;
        mx = n ? 1 : 0;
        csum.assign(vals.begin(), vals.end());
        cmin = cmax = vals;
        pot.assign(n, 0);
    }

    // O(log n), index of the representative of i's component; parents are never rewritten, so the forest records every merge
    int find(int i) {
        while (par[i] != i) i = par[i];
        return i;
    }

    // {root of i, value[i] - value[root]}
    pair<int, long long> rootAndWeight(int i) {
        long long w = 0;
        for (; par[i] != i; i = par[i]) w += pot[i];
        return {i, w};
    }

    // O(log n), merges the two components, returns {winner, loser}: the new root and the old root now under it,
    // or {-1, -1} if they were already together
    // w: value[j] - value[i] = w. Already together: nothing changes (diff(i, j) == w says if this agrees)
    pair<int, int> uniteWeighted(int i, int j, long long w) {
        auto [ri, wi] = rootAndWeight(i);
        auto [rj, wj] = rootAndWeight(j);
        i = ri, j = rj;
        if (i == j) {
            return {-1, -1};
        }
        w += wi - wj;  // now value[j's root] - value[i's root]
        if (sz[i] < sz[j]) {
            swap(i, j);
            w = -w;
        }
        par[j] = i;
        sz[i] += sz[j];
        comps--;
        mx = max(mx, sz[i]);
        csum[i] += csum[j];
        cmin[i] = min(cmin[i], cmin[j]);
        cmax[i] = max(cmax[i], cmax[j]);
        pot[j] = w;
        return {i, j};
    }

    // O(log n), forces a's root under b's root, false if already together
    // skips union by size, so depth can degrade to O(n) and every walk with it
    // w: value[b] - value[a] = w
    bool uniteAUnderBWeighted(int a, int b, long long w) {
        auto [ra, wa] = rootAndWeight(a);
        auto [rb, wb] = rootAndWeight(b);
        a = ra, b = rb;
        if (a == b) return false;
        w = wb - wa - w;  // now value[a's root] - value[b's root]
        par[a] = b;
        sz[b] += sz[a];
        comps--;
        mx = max(mx, sz[b]);
        csum[b] += csum[a];
        cmin[b] = min(cmin[b], cmin[a]);
        cmax[b] = max(cmax[b], cmax[a]);
        pot[a] = w;
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

    // O(n log n), the values of every element sitting in the same group as index i
    vector<T> elementsInGroup(int i) {
        int rt = find(i);
        vector<T> res;
        for (int j = 0; j < (int)par.size(); j++)
            if (find(j) == rt) res.push_back(vals[j]);
        return res;
    }

    // O(log n), the sum of the values in i's component
    long long componentSum(int i) { return csum[find(i)]; }

    // O(log n), the smallest value in i's component
    T componentMin(int i) { return cmin[find(i)]; }

    // O(log n), the largest value in i's component
    T componentMax(int i) { return cmax[find(i)]; }

    // O(log n), value[j] - value[i] from the unites so far, nullopt if i and j aren't together
    optional<long long> diff(int i, int j) {
        auto [ri, wi] = rootAndWeight(i);
        auto [rj, wj] = rootAndWeight(j);
        if (ri != rj) return nullopt;
        return wj - wi;
    }
};
