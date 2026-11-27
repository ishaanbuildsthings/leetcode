// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/union-find/compress/template.cpp
// @operations: areUnioned elementsInGroup find groups largestSize numComponents roots size sizes unite
// @data-structure-type: dsu
// @complexities:
//   areUnioned: α(N) amortized
//   elementsInGroup: N
//   find: α(N) amortized
//   groups: N
//   largestSize: 1
//   numComponents: 1
//   roots: N
//   size: α(N) amortized
//   sizes: N*log(N)
//   unite: α(N) amortized
//   build: N
// @memory:
//   layout: none
//   node: par[1*N] sz[1*N]
//   tags: none
//   other: vals[1*N]
#include <bits/stdc++.h>
using namespace std;
using ll = long long;

// DSU<int> dsu(vals);
// vals: the elements (any type: numbers, strings, pairs, ...); everything works on their indices 0..n-1
template <typename T>
struct DSU {
    vector<T> vals;
    vector<int> par, sz;
    int comps, mx;

    // O(n), every element starts in its own component
    DSU(const vector<T>& vals) : vals(vals) {
        int n = vals.size();
        par.resize(n);
        iota(par.begin(), par.end(), 0);
        sz.assign(n, 1);
        comps = n;
        mx = n ? 1 : 0;
    }

    // O(α(n)) amortized, effectively O(1): index of the representative of i's component
    int find(int i) {
        while (par[i] != i) {
            par[i] = par[par[i]];
            i = par[i];
        }
        return i;
    }

    // O(α(n)) amortized, merges the two components, false if i and j were already together
    bool unite(int i, int j) {
        i = find(i), j = find(j);
        if (i == j) {
            return false;
        }
        if (sz[i] < sz[j]) swap(i, j);
        par[j] = i;
        sz[i] += sz[j];
        comps--;
        mx = max(mx, sz[i]);
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

    // O(n), one vector of values per component (no empty ones), e.g. vals {10, 20, 30, 40} with 0-2 and 1-3
    // united -> {{10, 30}, {20, 40}}; components ordered by their smallest index, values in index order
    vector<vector<T>> groups() {
        int n = par.size();
        vector<int> slot(n, -1);  // slot[rt] = where root rt's vector sits in groupsArr
        vector<vector<T>> groupsArr;
        for (int i = 0; i < n; i++) {
            int rt = find(i);
            if (slot[rt] == -1) {
                slot[rt] = groupsArr.size();
                groupsArr.emplace_back();
            }
            groupsArr[slot[rt]].push_back(vals[i]);
        }
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
};
