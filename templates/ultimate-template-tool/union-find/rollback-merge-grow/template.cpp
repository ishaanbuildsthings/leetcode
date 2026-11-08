// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/union-find/rollback-merge-grow/template.cpp
// @operations: add areUnioned checkpoint componentData elementsInGroup find groups largestSize numComponents rollbackLastUnion rollbackTo roots size sizes unite
// @data-structure-type: dsu-rollback
// @complexities:
//   add: 1 amortized
//   areUnioned: log(N)
//   checkpoint: 1
//   componentData: log(N)
//   elementsInGroup: N*log(N)
//   find: log(N)
//   groups: N*log(N)
//   largestSize: 1
//   numComponents: 1
//   rollbackLastUnion: 1
//   rollbackTo: 1 amortized
//   roots: N
//   size: log(N)
//   sizes: N*log(N)
//   unite: log(N)
//   build: N
// @memory:
//   layout: none
//   node: par[1*N] sz[1*N]
//   tags: none
//   other: vals[1*N] data[1*N]
//   note: plus the undo stack: one small frame per unite not yet undone, holding a copy of the bigger Node; data holds one Node per element
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
// vals: the elements (any type: numbers, strings, pairs, ...); everything works on their indices 0..n-1, and add(val) appends more
struct RollbackDSU {
    using T = RawVal;
    vector<T> vals;
    vector<int> par, sz;
    int comps, mx;
    vector<Node> data;  // data[root]: the Node of root's component
    struct Frame { int i, j, mx; Node data; };  // i < 0: a unite that found them already together
    vector<Frame> stk;  // one frame per unite, so rollback can undo it

    // O(n), every element starts in its own component
    RollbackDSU(const vector<T>& vals = {}) : vals(vals) {
        int n = vals.size();
        par.resize(n);
        iota(par.begin(), par.end(), 0);
        sz.assign(n, 1);
        comps = n;
        mx = n ? 1 : 0;
        for (int i = 0; i < n; i++) data.push_back(baseFn(vals[i], i));
    }

    // O(log n), index of the representative of i's component; parents are never rewritten, so any unite can be undone
    int find(int i) {
        while (par[i] != i) i = par[i];
        return i;
    }

    // O(log n), merges the two components, false if i and j were already together
    // either way it records a frame, so it always takes exactly one rollbackLastUnion to undo
    bool unite(int i, int j) {
        i = find(i), j = find(j);
        if (i == j) {
            stk.push_back({-1, -1, mx});
            return false;
        }
        if (sz[i] < sz[j]) swap(i, j);
        stk.push_back({i, j, mx, data[i]});
        par[j] = i;
        sz[i] += sz[j];
        comps--;
        mx = max(mx, sz[i]);
        data[i] = combine(move(data[i]), data[j]);
        return true;
    }

    // O(1), undoes the most recent unite, whether or not it merged anything: k calls always undo the last
    // k unites (an add is never undone); out_of_range if there's no unite left to undo
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

    // O(n log n), the values of every element sitting in the same group as index i
    vector<T> elementsInGroup(int i) {
        int rt = find(i);
        vector<T> res;
        for (int j = 0; j < (int)par.size(); j++)
            if (find(j) == rt) res.push_back(vals[j]);
        return res;
    }

    // O(log n), the Node of i's component: every member's baseFn, combined
    Node componentData(int i) { return data[find(i)]; }

    // O(1), adds a new element in its own component and returns its index
    int add(const T& val) {
        int i = par.size();
        vals.push_back(val);
        par.push_back(i);
        sz.push_back(1);
        comps++;
        mx = max(mx, 1);
        data.push_back(baseFn(val, i));
        return i;
    }
};
