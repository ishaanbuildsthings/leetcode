// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/union-find/compress-values-members-grow/template.cpp
#include <bits/stdc++.h>
using namespace std;
using ll = long long;

// DSU<int> dsu(vals);
// vals: the elements (numbers: componentSum / Min / Max are over them); everything works on their indices 0..n-1, and add(val) appends more
template <typename T>
struct DSU {
    vector<T> vals;
    vector<int> par, sz;
    int comps, mx;
    vector<long long> csum;  // at each root: the sum, min and max of its component's values
    vector<T> cmin, cmax;
    vector<int> nxt;  // each component's members linked in a circle: i -> nxt[i] -> ... -> i

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
        nxt = par;
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
        csum[i] += csum[j];
        cmin[i] = min(cmin[i], cmin[j]);
        cmax[i] = max(cmax[i], cmax[j]);
        swap(nxt[i], nxt[j]);  // (joins the two circles)
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

    // O(size of the group), the values of every element in the same group as index i, starting at i
    vector<T> elementsInGroup(int i) {
        vector<T> res = {vals[i]};
        for (int j = nxt[i]; j != i; j = nxt[j]) res.push_back(vals[j]);
        return res;
    }

    // O(α(n)) amortized, the sum of the values in i's component
    long long componentSum(int i) { return csum[find(i)]; }

    // O(α(n)) amortized, the smallest value in i's component
    T componentMin(int i) { return cmin[find(i)]; }

    // O(α(n)) amortized, the largest value in i's component
    T componentMax(int i) { return cmax[find(i)]; }

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
        nxt.push_back(i);
        return i;
    }
};
