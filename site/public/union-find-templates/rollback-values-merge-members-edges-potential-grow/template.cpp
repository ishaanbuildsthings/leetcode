// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/union-find/rollback-values-merge-members-edges-potential-grow/template.cpp
// @operations: add areUnioned checkpoint componentData componentMax componentMin componentSum diff edgeCount elementsInGroup find groups isTree largestSize numComponents rollbackLastUnion rollbackTo roots size sizes uniteWeighted
// @data-structure-type: dsu-rollback
// @complexities:
//   add: 1 amortized
//   areUnioned: log(N)
//   checkpoint: 1
//   componentData: log(N)
//   componentMax: log(N)
//   componentMin: log(N)
//   componentSum: log(N)
//   diff: log(N)
//   edgeCount: log(N)
//   elementsInGroup: K
//   find: log(N)
//   groups: N*log(N)
//   isTree: log(N)
//   largestSize: 1
//   numComponents: 1
//   rollbackLastUnion: 1
//   rollbackTo: 1 amortized
//   roots: N
//   size: log(N)
//   sizes: N*log(N)
//   uniteWeighted: log(N)
//   build: N
// @memory:
//   layout: none
//   node: par[1*N] sz[1*N]
//   tags: none
//   other: vals[1*N] csum[1*N] cmin[1*N] cmax[1*N] data[1*N] nxt[1*N] edges[1*N] pot[1*N]
//   note: K = the size of the group; plus the undo stack: one small frame per unite not yet undone, holding a copy of the bigger Node; data holds one Node per element
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
// rollback keeps a copy of
// the bigger Node every unite, so keep Nodes small here
Node combine(Node big, const Node& small) {
    // Node res;
    // res.tot = big.tot + small.tot;
    // res.mx = max(big.mx, small.mx);
    // return res;
}


// RollbackDSU dsu(vals);
// vals: the elements (numbers: componentSum / Min / Max are over them); everything works on their indices 0..n-1, and add(val) appends more
// potential: every element has a hidden number value[i]; uniteWeighted(i, j, w) says value[j] - value[i] = w and diff(i, j)
// reads it back (for parity / two-colouring, swap + and - for ^ throughout)
struct RollbackDSU {
    using T = RawVal;
    vector<T> vals;
    vector<int> par, sz;
    int comps, mx;
    vector<long long> csum;  // at each root: the sum, min and max of its component's values
    vector<T> cmin, cmax;
    vector<Node> data;  // data[root]: the Node of root's component
    vector<int> nxt;  // each component's members linked in a circle: i -> nxt[i] -> ... -> i
    vector<int> edges;  // edges[root]: how many unites touched root's component, merging or not
    vector<long long> pot;  // pot[i] = value[i] - value[par[i]] (0 at a root)
    struct Frame { int i, j, mx; T lo, hi; Node data; };  // i < 0: a unite that found them already together (j: its root, for the edge count)
    vector<Frame> stk;  // one frame per unite, so rollback can undo it

    // O(n), every element starts in its own component
    RollbackDSU(const vector<T>& vals = {}) : vals(vals) {
        int n = vals.size();
        par.resize(n);
        iota(par.begin(), par.end(), 0);
        sz.assign(n, 1);
        comps = n;
        mx = n ? 1 : 0;
        csum.assign(vals.begin(), vals.end());
        cmin = cmax = vals;
        for (int i = 0; i < n; i++) data.push_back(baseFn(vals[i], i));
        nxt = par;
        edges.assign(n, 0);
        pot.assign(n, 0);
    }

    // O(log n), index of the representative of i's component; parents are never rewritten, so any unite can be undone
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

    // O(log n), merges the two components, false if i and j were already together
    // w: value[j] - value[i] = w. Already together: nothing changes (diff(i, j) == w says if this agrees)
    // either way it counts as an edge of the component (edgeCount)
    // either way it records a frame, so it always takes exactly one rollbackLastUnion to undo
    bool uniteWeighted(int i, int j, long long w) {
        auto [ri, wi] = rootAndWeight(i);
        auto [rj, wj] = rootAndWeight(j);
        i = ri, j = rj;
        if (i == j) {
            edges[i]++;
            stk.push_back({-1, i, mx});
            return false;
        }
        w += wi - wj;  // now value[j's root] - value[i's root]
        if (sz[i] < sz[j]) {
            swap(i, j);
            w = -w;
        }
        stk.push_back({i, j, mx, cmin[i], cmax[i], data[i]});
        par[j] = i;
        sz[i] += sz[j];
        comps--;
        mx = max(mx, sz[i]);
        csum[i] += csum[j];
        cmin[i] = min(cmin[i], cmin[j]);
        cmax[i] = max(cmax[i], cmax[j]);
        data[i] = combine(move(data[i]), data[j]);
        swap(nxt[i], nxt[j]);  // (joins the two circles)
        edges[i] += edges[j] + 1;
        pot[j] = w;
        return true;
    }

    // O(1), undoes the most recent unite, whether or not it merged anything: k calls always undo the last
    // k unites (an add is never undone); out_of_range if there's no unite left to undo
    void rollbackLastUnion() {
        if (stk.empty()) throw out_of_range("rollbackLastUnion: no unite left to undo");
        Frame f = stk.back();
        stk.pop_back();
        if (f.i < 0) {
            edges[f.j]--;
            return;
        }
        int i = f.i, j = f.j;
        par[j] = j;
        sz[i] -= sz[j];
        comps++;
        mx = f.mx;
        csum[i] -= csum[j];
        cmin[i] = f.lo;
        cmax[i] = f.hi;
        data[i] = move(f.data);
        swap(nxt[i], nxt[j]);  // (the same swap splits them again)
        edges[i] -= edges[j] + 1;
        pot[j] = 0;
    }

    // O(1), a point to roll back to later: how many unites can be undone right now
    int checkpoint() { return stk.size(); }

    // O(1) per unite undone, undoes every unite made since checkpoint() returned k
    void rollbackTo(int k) {
        while ((int)stk.size() > k) rollbackLastUnion();
    }

    // O(log n), true if i and j are in the same component
    bool areUnioned(int i, int j) { return find(i) == find(j); }

    // O(log n), how many elements are in i's component
    int size(int i) { return sz[find(i)]; }

    // O(1), how many components exist right now
    int numComponents() { return comps; }

    // O(1), size of the biggest component, restored by rollback
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

    // O(log n), the sum of the values in i's component
    long long componentSum(int i) { return csum[find(i)]; }

    // O(log n), the smallest value in i's component
    T componentMin(int i) { return cmin[find(i)]; }

    // O(log n), the largest value in i's component
    T componentMax(int i) { return cmax[find(i)]; }

    // O(log n), the Node of i's component: every member's baseFn, combined
    Node componentData(int i) { return data[find(i)]; }

    // O(log n), how many unites have touched i's component (merging or not): its edges, if each unite is an edge
    int edgeCount(int i) { return edges[find(i)]; }

    // O(log n), true if i's component has no cycle: exactly size - 1 edges
    bool isTree(int i) {
        int r = find(i);
        return edges[r] == sz[r] - 1;
    }

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
        csum.push_back(val);
        cmin.push_back(val);
        cmax.push_back(val);
        data.push_back(baseFn(val, i));
        nxt.push_back(i);
        edges.push_back(0);
        pot.push_back(0);
        return i;
    }
};
