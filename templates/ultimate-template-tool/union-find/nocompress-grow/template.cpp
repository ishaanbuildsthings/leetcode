// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/union-find/nocompress-grow/template.cpp
// @operations: add areUnioned elementsInGroup find groups largestSize numComponents parent roots size sizes unite
// @data-structure-type: dsu-nocompress
// @complexities:
//   add: 1 amortized
//   areUnioned: log(N)
//   elementsInGroup: N*log(N)
//   find: log(N)
//   groups: N*log(N)
//   largestSize: 1
//   numComponents: 1
//   parent: 1
//   roots: N
//   size: log(N)
//   sizes: N*log(N)
//   unite: log(N)
//   build: N
// @memory:
//   layout: none
//   node: par[1*N] sz[1*N]
//   tags: none
//   other: vals[1*N]
#include <bits/stdc++.h>
using namespace std;
using ll = long long;

// DSUNoCompress<int> dsu(vals);
// vals: the elements (any type: numbers, strings, pairs, ...); everything works on their indices 0..n-1, and add(val) appends more
template <typename T>
struct DSUNoCompress {
    vector<T> vals;
    vector<int> par, sz;
    int comps, mx;

    // O(n), every element starts in its own component
    DSUNoCompress(const vector<T>& vals = {}) : vals(vals) {
        int n = vals.size();
        par.resize(n);
        iota(par.begin(), par.end(), 0);
        sz.assign(n, 1);
        comps = n;
        mx = n ? 1 : 0;
    }

    // O(log n), index of the representative of i's component; parents are never rewritten, so the forest records every merge
    int find(int i) {
        while (par[i] != i) i = par[i];
        return i;
    }

    // O(log n), merges the two components, returns {winner, loser}: the new root and the old root now under it,
    // or {-1, -1} if they were already together
    pair<int, int> unite(int i, int j) {
        i = find(i), j = find(j);
        if (i == j) {
            return {-1, -1};
        }
        if (sz[i] < sz[j]) swap(i, j);
        par[j] = i;
        sz[i] += sz[j];
        comps--;
        mx = max(mx, sz[i]);
        return {i, j};
    }

    // O(1), i's parent pointer (i itself if it's a root): without path compression the pointers never change
    // once set, so you can walk them and keep your own data per pointer
    int parent(int i) { return par[i]; }

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

    // O(n log n), one vector of values per component (no empty ones), e.g. vals {10, 20, 30, 40} with 0-2 and 1-3
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

    // O(n log n), the values of every element sitting in the same group as index i
    vector<T> elementsInGroup(int i) {
        int rt = find(i);
        vector<T> res;
        for (int j = 0; j < (int)par.size(); j++)
            if (find(j) == rt) res.push_back(vals[j]);
        return res;
    }

    // O(1), adds a new element in its own component and returns its index
    int add(const T& val) {
        int i = par.size();
        vals.push_back(val);
        par.push_back(i);
        sz.push_back(1);
        comps++;
        mx = max(mx, 1);
        return i;
    }
};
