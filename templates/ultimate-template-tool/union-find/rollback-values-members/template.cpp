// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/union-find/rollback-values-members/template.cpp
// @operations: areUnioned checkpoint componentMax componentMin componentSum elementsInGroup find groups largestSize numComponents rollbackLastUnion rollbackTo roots size sizes unite
// @data-structure-type: dsu-rollback
// @complexities:
//   areUnioned: log(N)
//   checkpoint: 1
//   componentMax: log(N)
//   componentMin: log(N)
//   componentSum: log(N)
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
//   unite: log(N)
//   build: N
// @memory:
//   layout: none
//   node: par[1*N] sz[1*N]
//   tags: none
//   other: vals[1*N] csum[1*N] cmin[1*N] cmax[1*N] nxt[1*N]
//   note: K = the size of the group; plus the undo stack: one small frame per unite not yet undone
#include <bits/stdc++.h>
using namespace std;
using ll = long long;

// RollbackDSU<int> dsu(vals);
// vals: the elements (numbers: componentSum / Min / Max are over them); everything works on their indices 0..n-1
template <typename T>
struct RollbackDSU {
    vector<T> vals;
    vector<int> par, sz;
    int comps, mx;
    vector<long long> csum;  // at each root: the sum, min and max of its component's values
    vector<T> cmin, cmax;
    vector<int> nxt;  // each component's members linked in a circle: i -> nxt[i] -> ... -> i
    struct Frame { int i, j, mx; T lo, hi; };  // i < 0: a unite that found them already together
    vector<Frame> stk;  // one frame per unite, so rollback can undo it

    // O(n), every element starts in its own component
    RollbackDSU(const vector<T>& vals) : vals(vals) {
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
        stk.push_back({i, j, mx, cmin[i], cmax[i]});
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
        csum[i] -= csum[j];
        cmin[i] = f.lo;
        cmax[i] = f.hi;
        swap(nxt[i], nxt[j]);  // (the same swap splits them again)
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
};
