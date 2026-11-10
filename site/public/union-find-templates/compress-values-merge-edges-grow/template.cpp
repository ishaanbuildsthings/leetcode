// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/union-find/compress-values-merge-edges-grow/template.cpp
// @operations: add areUnioned componentData componentMax componentMin componentSum edgeCount elementsInGroup find groups isTree largestSize numComponents roots size sizes unite
// @data-structure-type: dsu
// @complexities:
//   add: 1 amortized
//   areUnioned: α(N) amortized
//   componentData: α(N) amortized
//   componentMax: α(N) amortized
//   componentMin: α(N) amortized
//   componentSum: α(N) amortized
//   edgeCount: α(N) amortized
//   elementsInGroup: N
//   find: α(N) amortized
//   groups: N
//   isTree: α(N) amortized
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
//   other: vals[1*N] csum[1*N] cmin[1*N] cmax[1*N] data[1*N] edges[1*N]
//   note: data holds one Node per element
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


// DSU dsu(vals);
// vals: the elements (numbers: componentSum / Min / Max are over them); everything works on their indices 0..n-1, and
// add(val) appends more
struct DSU {
    using T = RawVal;
    vector<T> vals;
    vector<int> par, sz;
    int comps, mx;
    vector<long long> csum;  // at each root: the sum, min and max of its component's values
    vector<T> cmin, cmax;
    vector<Node> data;  // data[root]: the Node of root's component
    vector<int> edges;  // edges[root]: how many unites touched root's component, merging or not

    // O(n), every element starts in its own component
    DSU(const vector<T>& vals = {}) : vals(vals) {
        int n = vals.size();
        par.resize(n);
        iota(par.begin(), par.end(), 0);
        sz.assign(n, 1);
        comps = n;
        mx = n ? 1 : 0;
        csum.assign(vals.begin(), vals.end());
        cmin = cmax = vals;
        for (int i = 0; i < n; i++) data.push_back(baseFn(vals[i], i));
        edges.assign(n, 0);
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
    // either way it counts as an edge of the component (edgeCount)
    bool unite(int i, int j) {
        i = find(i), j = find(j);
        if (i == j) {
            edges[i]++;
            return false;
        }
        if (sz[i] < sz[j]) swap(i, j);
        par[j] = i;
        sz[i] += sz[j];
        comps--;
        mx = max(mx, sz[i]);
        csum[i] += csum[j];
        cmin[i] = min(cmin[i], cmin[j]);
        cmax[i] = max(cmax[i], cmax[j]);
        data[i] = combine(move(data[i]), data[j]);
        edges[i] += edges[j] + 1;
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

    // O(α(n)) amortized, the sum of the values in i's component
    long long componentSum(int i) { return csum[find(i)]; }

    // O(α(n)) amortized, the smallest value in i's component
    T componentMin(int i) { return cmin[find(i)]; }

    // O(α(n)) amortized, the largest value in i's component
    T componentMax(int i) { return cmax[find(i)]; }

    // O(α(n)) amortized, the Node of i's component: every member's baseFn, combined
    Node componentData(int i) { return data[find(i)]; }

    // O(α(n)) amortized, how many unites have touched i's component (merging or not): its edges, if each unite is an
    // edge
    int edgeCount(int i) { return edges[find(i)]; }

    // O(α(n)) amortized, true if i's component has no cycle: exactly size - 1 edges
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
        csum.push_back(val);
        cmin.push_back(val);
        cmax.push_back(val);
        data.push_back(baseFn(val, i));
        edges.push_back(0);
        return i;
    }
};
