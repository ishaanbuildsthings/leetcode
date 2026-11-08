// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/union-find/rollback-merge-members-potential/template.cpp
// @operations: areUnioned checkpoint componentData diff elementsInGroup find groups largestSize numComponents rollbackLastUnion rollbackTo roots size sizes uniteWeighted
// @data-structure-type: dsu-rollback
// @complexities:
//   areUnioned: log(N)
//   checkpoint: 1
//   componentData: log(N)
//   diff: log(N)
//   elementsInGroup: K
//   find: log(N)
//   groups: N*log(N)
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
//   other: vals[1*N] data[1*N] nxt[1*N] pot[1*N]
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
// vals: the elements (any type: numbers, strings, pairs, ...); everything works on their indices 0..n-1
// potential: every element has a hidden number value[i]; uniteWeighted(i, j, w) says value[j] - value[i] = w and diff(i, j)
// reads it back (for parity / two-colouring, swap + and - for ^ throughout)
struct RollbackDSU {
    using T = RawVal;
    vector<T> vals;
    vector<int> par, sz;
    int comps, mx;
    vector<Node> data;  // data[root]: the Node of root's component
    vector<int> nxt;  // each component's members linked in a circle: i -> nxt[i] -> ... -> i
    vector<long long> pot;  // pot[i] = value[i] - value[par[i]] (0 at a root)
    struct Frame { int i, j, mx; Node data; };  // i < 0: a unite that found them already together
    vector<Frame> stk;  // one frame per unite, so rollback can undo it

    // O(n), every element starts in its own component
    RollbackDSU(const vector<T>& vals) : vals(vals) {
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
    // either way it records a frame, so it always takes exactly one rollbackLastUnion to undo
    bool uniteWeighted(int i, int j, long long w) {
        auto [ri, wi] = rootAndWeight(i);
        auto [rj, wj] = rootAndWeight(j);
        i = ri, j = rj;
        if (i == j) {
            stk.push_back({-1, -1, mx});
            return false;
        }
        w += wi - wj;  // now value[j's root] - value[i's root]
        if (sz[i] < sz[j]) {
            swap(i, j);
            w = -w;
        }
        stk.push_back({i, j, mx, data[i]});
        par[j] = i;
        sz[i] += sz[j];
        comps--;
        mx = max(mx, sz[i]);
        data[i] = combine(move(data[i]), data[j]);
        swap(nxt[i], nxt[j]);  // (joins the two circles)
        pot[j] = w;
        return true;
    }

    // O(1), undoes the most recent unite, whether or not it merged anything: k calls always undo the last
    // k unites; out_of_range if there's no unite left to undo
    void rollbackLastUnion() {
        if (stk.empty()) throw out_of_range("rollbackLastUnion: no unite left to undo");
        Frame f = stk.back();
        stk.pop_back();
        if (f.i < 0) return;
        int i = f.i, j = f.j;
        par[j] = j;
        sz[i] -= sz[j];
        comps++;
        mx = f.mx;
        data[i] = move(f.data);
        swap(nxt[i], nxt[j]);  // (the same swap splits them again)
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

    // O(log n), the Node of i's component: every member's baseFn, combined
    Node componentData(int i) { return data[find(i)]; }

    // O(log n), value[j] - value[i] from the unites so far, nullopt if i and j aren't together
    optional<long long> diff(int i, int j) {
        auto [ri, wi] = rootAndWeight(i);
        auto [rj, wj] = rootAndWeight(j);
        if (ri != rj) return nullopt;
        return wj - wi;
    }
};
