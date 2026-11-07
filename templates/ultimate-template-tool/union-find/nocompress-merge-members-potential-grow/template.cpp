// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/union-find/nocompress-merge-members-potential-grow/template.cpp
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
// vals: the elements (any type: numbers, strings, pairs, ...); everything works on their indices 0..n-1, and add(val) appends more
// potential: every element has a hidden number value[i]; unite(i, j, w) says value[j] - value[i] = w and diff(i, j)
// reads it back (for parity / two-colouring, swap + and - for ^ throughout)
struct DSUNoCompress {
    using T = RawVal;
    vector<T> vals;
    vector<int> par, sz;
    int comps, mx;
    vector<Node> data;  // data[root]: the Node of root's component
    vector<int> nxt;  // each component's members linked in a circle: i -> nxt[i] -> ... -> i
    vector<long long> pot;  // pot[i] = value[i] - value[par[i]] (0 at a root)

    // O(n), every element starts in its own component
    DSUNoCompress(const vector<T>& vals = {}) : vals(vals) {
        int n = vals.size();
        par.resize(n);
        iota(par.begin(), par.end(), 0);
        sz.assign(n, 1);
        comps = n;
        mx = n ? 1 : 0;
        for (int i = 0; i < n; i++) data.push_back(baseFn(vals[i], i));
        nxt = par;
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
    pair<int, int> unite(int i, int j, long long w) {
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
        data[i] = combine(move(data[i]), data[j]);
        swap(nxt[i], nxt[j]);  // (joins the two circles)
        pot[j] = w;
        return {i, j};
    }

    // O(log n), forces a's root under b's root, false if already together
    // skips union by size, so depth can degrade to O(n) and every walk with it
    // w: value[b] - value[a] = w
    // combine gets b's component's Node first here, even when it's the smaller one
    bool uniteAUnderB(int a, int b, long long w) {
        auto [ra, wa] = rootAndWeight(a);
        auto [rb, wb] = rootAndWeight(b);
        a = ra, b = rb;
        if (a == b) return false;
        w = wb - wa - w;  // now value[a's root] - value[b's root]
        par[a] = b;
        sz[b] += sz[a];
        comps--;
        mx = max(mx, sz[b]);
        data[b] = combine(move(data[b]), data[a]);
        swap(nxt[b], nxt[a]);  // (joins the two circles)
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

    // O(size of the group), the values of every element in the same group as index i, starting at i
    vector<T> elementsInGroup(int i) {
        vector<T> res = {vals[i]};
        for (int j = nxt[i]; j != i; j = nxt[j]) res.push_back(vals[j]);
        return res;
    }

    // O(log n), the Node of i's component: every member's baseFn, combined
    Node componentData(int i) { return data[find(i)]; }

    // O(log n), value[j] - value[i] from the unites so far, nullopt if i and j aren't together
    optional<long long> diff(int i, int j) {
        auto [ri, wi] = rootAndWeight(i);
        auto [rj, wj] = rootAndWeight(j);
        if (ri != rj) return nullopt;
        return wj - wi;
    }

    // O(1), adds a new element in its own component and returns its index
    int add(const T& val) {
        int i = par.size();
        vals.push_back(val);
        par.push_back(i);
        sz.push_back(1);
        comps++;
        mx = max(mx, 1);
        data.push_back(baseFn(val, i));
        nxt.push_back(i);
        pot.push_back(0);
        return i;
    }
};
