// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/union-find/compress-potential/template.cpp
// @operations: areUnioned diff elementsInGroup find groups largestSize numComponents roots size sizes uniteWeighted
// @data-structure-type: dsu
// @complexities:
//   areUnioned: α(N) amortized
//   diff: α(N) amortized
//   elementsInGroup: N
//   find: α(N) amortized
//   groups: N
//   largestSize: 1
//   numComponents: 1
//   roots: N
//   size: α(N) amortized
//   sizes: N*log(N)
//   uniteWeighted: α(N) amortized
//   build: N
// @memory:
//   layout: none
//   node: par[1*N] sz[1*N]
//   tags: none
//   other: vals[1*N] pot[1*N]
#include <bits/stdc++.h>
using namespace std;
using ll = long long;

// DSU<int> dsu(vals);
// vals: the elements (any type: numbers, strings, pairs, ...); everything works on their indices 0..n-1
// potential: every element has a hidden number value[i]; uniteWeighted(i, j, w) says value[j] - value[i] = w and diff(i, j)
// reads it back (for parity / two-colouring, swap + and - for ^ throughout)
template <typename T>
struct DSU {
    vector<T> vals;
    vector<int> par, sz;
    int comps, mx;
    vector<long long> pot;  // pot[i] = value[i] - value[par[i]] (0 at a root)

    // O(n), every element starts in its own component
    DSU(const vector<T>& vals) : vals(vals) {
        int n = vals.size();
        par.resize(n);
        iota(par.begin(), par.end(), 0);
        sz.assign(n, 1);
        comps = n;
        mx = n ? 1 : 0;
        pot.assign(n, 0);
    }

    // O(α(n)) amortized, effectively O(1): index of the representative of i's component (compresses fully, keeping pot
    // right; union by size keeps the recursion log n deep)
    int find(int i) {
        if (par[i] == i) return i;
        int r = find(par[i]);
        pot[i] += pot[par[i]];  // (par[i] now hangs straight off r)
        return par[i] = r;
    }

    // {root of i, value[i] - value[root]}
    pair<int, long long> rootAndWeight(int i) {
        int r = find(i);
        return {r, pot[i]};
    }

    // O(α(n)) amortized, merges the two components, false if i and j were already together
    // w: value[j] - value[i] = w. Already together: nothing changes (diff(i, j) == w says if this agrees)
    bool uniteWeighted(int i, int j, long long w) {
        auto [ri, wi] = rootAndWeight(i);
        auto [rj, wj] = rootAndWeight(j);
        i = ri, j = rj;
        if (i == j) {
            return false;
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
        pot[j] = w;
        return true;
    }

    // O(α(n)) amortized, true if i and j are in the same component
    bool areUnioned(int i, int j) { return find(i) == find(j); }

    // O(α(n)) amortized, how many elements are in i's component
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

    // O(n), groupsArr[rt] = values whose root is rt, empty if rt is not a root
    vector<vector<T>> groups() {
        int n = par.size();
        vector<vector<T>> groupsArr(n);
        for (int i = 0; i < n; i++) groupsArr[find(i)].push_back(vals[i]);
        return groupsArr;
    }

    // O(n), the values of every element sitting in the same group as index i
    vector<T> elementsInGroup(int i) {
        int rt = find(i);
        vector<T> res;
        for (int j = 0; j < (int)par.size(); j++)
            if (find(j) == rt) res.push_back(vals[j]);
        return res;
    }

    // O(α(n)) amortized, value[j] - value[i] from the unites so far, nullopt if i and j aren't together
    optional<long long> diff(int i, int j) {
        auto [ri, wi] = rootAndWeight(i);
        auto [rj, wj] = rootAndWeight(j);
        if (ri != rj) return nullopt;
        return wj - wi;
    }
};
