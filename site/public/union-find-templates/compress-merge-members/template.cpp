// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/union-find/compress-merge-members/template.cpp
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
// vals: the elements (any type: numbers, strings, pairs, ...); everything works on their indices 0..n-1
struct DSU {
    using T = RawVal;
    vector<T> vals;
    vector<int> par, sz;
    int comps, mx;
    vector<Node> data;  // data[root]: the Node of root's component
    vector<int> nxt;  // each component's members linked in a circle: i -> nxt[i] -> ... -> i

    // O(n), every element starts in its own component
    DSU(const vector<T>& vals) : vals(vals) {
        int n = vals.size();
        par.resize(n);
        iota(par.begin(), par.end(), 0);
        sz.assign(n, 1);
        comps = n;
        mx = n ? 1 : 0;
        for (int i = 0; i < n; i++) data.push_back(baseFn(vals[i], i));
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
        data[i] = combine(move(data[i]), data[j]);
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

    // O(α(n)) amortized, the Node of i's component: every member's baseFn, combined
    Node componentData(int i) { return data[find(i)]; }
};
