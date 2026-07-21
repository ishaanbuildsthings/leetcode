// TEMPLATE BY ISHAANBUILDSTHINGS (see my github)
//
// EXAMPLE
//   // max over long long scores, slots in [0, 1e9]
//   PersistentSeg<long long> seg(
//       1'000'000'000,
//       [](long long raw){ return raw; },                    // base: wrap a raw value
//       [](long long a, long long b){ return a > b ? a : b; }); // combine: never sees empty
//   seg.pointSet(value, rawScore);                            // overwrite slot `value`
//   int versionId = seg.snapshot();                          // freeze -> version id
//   auto r = seg.queryVersion(versionId, low, high);         // r.has -> found?, r.val -> data
//   auto c = seg.queryCurrent(low, high);
//
//   // min: base v->v,      combine = std::min
//   // sum: base v->v,      combine = a+b   (but use ADD semantics: query-then-set, or an add() variant)
//   // min-and-max tuple: T = pair<ll,ll>, base v->{v,v}, combine -> {min(a.first,b.first), max(a.second,b.second)}
//
// Persistent segment tree over slots [0, maxVal], generic over the
// stored type T. base(raw) wraps a raw value into a T; combine merges
// two Ts and NEVER receives an empty node -- empties are dropped by the
// internal combineOpt, exactly like the Python None-sentinel style.
//
// pointSet(value, raw) overwrites a slot. snapshot() freezes the live
// tree, returns a versionId (0, 1, 2, ...). Sparse: an update touches
// O(log maxVal) nodes, so maxVal can be ~1e9 with raw values.
//
// Queries return Result{has, val}: has=false means the range was empty
// (low > high, or nothing set in it) -- the caller decides what empty
// means, e.g. fall back to 0. No sentinel value is baked in.

#include <bits/stdc++.h>
using namespace std;

template <typename T>
class PersistentSeg {
public:
    struct Result {
        bool has;   // false => range empty / nothing set; val is unspecified
        T val;      // aggregate, valid only when has == true
    };

    // O(1)
    PersistentSeg(int maxVal,
                  function<T(long long)> base,
                  function<T(T, T)> combine)
        : maxVal(maxVal), base(base), combine(combine) {
        // node 0 is the empty sentinel: filled=false, children point to itself
        left.push_back(0);
        right.push_back(0);
        data.push_back(T{});
        filled.push_back(false);
        cur = 0;
        versions.push_back(0);
    }

    // O(log maxVal) -- overwrite slot `value` with base(raw) in the live tree
    void pointSet(int value, long long raw) {
        cur = _set(cur, 0, maxVal, value, base(raw));
    }

    // O(1) -- freeze the live tree, return its versionId
    int snapshot() {
        versions.push_back(cur);
        return (int)versions.size() - 1;
    }

    // O(log maxVal) -- aggregate over [low, high] in the live tree
    Result queryCurrent(int low, int high) {
        if (low > high) return {false, T{}};
        return _query(cur, 0, maxVal, low, high);
    }

    // O(log maxVal) -- aggregate over [low, high] in a frozen version
    Result queryVersion(int versionId, int low, int high) {
        if (low > high) return {false, T{}};
        return _query(versions[versionId], 0, maxVal, low, high);
    }

private:
    int maxVal;
    function<T(long long)> base;
    function<T(T, T)> combine;
    vector<int> left, right;
    vector<T> data;
    vector<char> filled;     // filled[node] == false  <=>  Python's data is None
    int cur;
    vector<int> versions;

    // allocate a fresh node, return its index (this is what makes it persistent)
    int _new(int l, int r, const T& d, bool isFilled) {
        left.push_back(l);
        right.push_back(r);
        data.push_back(d);
        filled.push_back(isFilled);
        return (int)data.size() - 1;
    }

    // merge two child aggregates, treating unfilled as empty so combine
    // never sees an empty node -- the exact role of Python's combineOpt
    Result _combineOpt(const Result& a, const Result& b) {
        if (!a.has) return b;
        if (!b.has) return a;
        return {true, combine(a.val, b.val)};
    }

    // pull a node's aggregate up from its children
    Result _pull(int lc, int rc) {
        Result a = filled[lc] ? Result{true, data[lc]} : Result{false, T{}};
        Result b = filled[rc] ? Result{true, data[rc]} : Result{false, T{}};
        return _combineOpt(a, b);
    }

    // rebuild only the root->value path into new nodes, reuse every off-path child
    int _set(int node, int nodeLow, int nodeHigh, int value, const T& newData) {
        if (nodeLow == nodeHigh)
            return _new(0, 0, newData, true);
        int mid = (nodeLow + nodeHigh) >> 1;
        int lc = left[node], rc = right[node];
        if (value <= mid) lc = _set(lc, nodeLow, mid, value, newData);
        else              rc = _set(rc, mid + 1, nodeHigh, value, newData);
        Result up = _pull(lc, rc);
        return _new(lc, rc, up.val, up.has);
    }

    // standard range aggregate; node 0 (empty subtree) contributes {false, _}
    Result _query(int node, int nodeLow, int nodeHigh, int low, int high) {
        if (node == 0 || nodeHigh < low || high < nodeLow)
            return {false, T{}};
        if (low <= nodeLow && nodeHigh <= high)
            return {filled[node], data[node]};
        int mid = (nodeLow + nodeHigh) >> 1;
        return _combineOpt(_query(left[node], nodeLow, mid, low, high),
                           _query(right[node], mid + 1, nodeHigh, low, high));
    }
};