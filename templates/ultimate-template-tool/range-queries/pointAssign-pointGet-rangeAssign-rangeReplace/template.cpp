// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries/pointAssign-pointGet-rangeAssign-rangeReplace/template.cpp
#include <bits/stdc++.h>
using namespace std;
using ll = long long;

// @operations: getAll pointAssign pointGet rangeAssign rangeReplace
// @data-structure-type: lazy-seg-tree
// @complexities:
//   getAll: N*log(N)
//   pointAssign: U*log(N)
//   pointGet: log(N)
//   rangeAssign: U*log(N)
//   rangeReplace: U*log(N)
//   build: N*U
// @memory:
//   layout: pow2-iterative
//   node: t[4*N]
//   tags: mp[2*N*U]
//   other: none
//   note: U = valHi - valLo + 1 (every value ever in the array is in [valLo, valHi]); each tag is a whole map old value -> new value, so a push costs O(U); a map is kept only while pending (handed down, its memory is reused), so mp is far below 2*N*U in practice

// Lazy seg tree whose tag is a value map (mass change, CF 911G): rangeReplace(l, r, x, y) turns every x in a[l..r]
// into y, and rangeAssign(l, r, v) sets a[l..r] = v, in O(U log N), U = valHi - valLo + 1: good when the values are
// few (911G: 1..100). A pending tag is a map old value -> new value for the whole segment, so any mix of changes
// composes into one map. All indices 0-based, ranges inclusive [l, r]; searches return -1 when nothing qualifies.
// T: int, long long, char, ...: the values; valLo / valHi bound every value the array will ever hold

template <typename T>
struct ValueMapSeg {
    // leaves t[cap + i] hold a[i] - valLo (-1: padding past n); node k's pending map for its children is
    // rows[row[k] * U ..] (row[k] = -1: none). A map row exists only while pending: pushed down, it is reused
    int n, cap, lg, U;
    T valLo;
    vector<int> t, row, rows, freeRows, gbuf, tmp;

    // O(N*U) -- arr: the initial array; every value it will ever hold must be in [valLo, valHi]
    ValueMapSeg(const vector<T>& arr, T valLo, T valHi) : n((int)arr.size()), cap(1), lg(0),
        U(int(valHi - valLo) + 1), valLo(valLo) {
        while (cap < n) cap <<= 1, lg++;
        t.assign(2 * cap, -1), row.assign(cap, -1), tmp.assign(U, 0);
        for (int i = 0; i < n; i++) {
            t[cap + i] = off(arr[i]);
        }
    }

    // O(1) -- the length of the array
    int size() const { return n; }

    // O(logN) -- a[i]; needs 0 <= i < size(), else throws out_of_range
    T pointGet(int i) const {
        if (i < 0 || i >= size()) throw out_of_range("pointGet: needs 0 <= i < size()");
        int k = cap + i, v = t[k];
        for (k >>= 1; k; k >>= 1)  // (a map higher up is newer: apply them bottom-up)
            if (row[k] >= 0) v = rows[(size_t)row[k] * U + v];
        return T(v + valLo);
    }

    // O(U*logN) -- a[i] = v; needs valLo <= v <= valHi; needs 0 <= i < size(), else throws out_of_range
    void pointAssign(int i, const T& v) {
        if (i < 0 || i >= size()) throw out_of_range("pointAssign: needs 0 <= i < size()");
        int o = off(v), k = cap + i;
        for (int h = lg; h >= 1; h--) push(k >> h);
        t[k] = o;
    }

    // O(U*logN) -- every a[i] == x with l <= i <= r becomes y; needs valLo <= y <= valHi; needs 0 <= l <= r < size(),
    // else throws out_of_range
    void rangeReplace(int l, int r, const T& x, const T& y) {
        if (l < 0 || l > r || r >= size()) throw out_of_range("rangeReplace: needs 0 <= l <= r < size()");
        int b = off(y);
        long long a = (long long)x - (long long)valLo;
        if (a < 0 || a >= U || a == b) return;
        update(l, r, [&](int k) { applyRep(k, (int)a, b); });
    }

    // O(U*logN) -- a[l..r] = v; needs valLo <= v <= valHi; needs 0 <= l <= r < size(), else throws out_of_range
    void rangeAssign(int l, int r, const T& v) {
        if (l < 0 || l > r || r >= size()) throw out_of_range("rangeAssign: needs 0 <= l <= r < size()");
        vector<int> g(U, off(v));
        update(l, r, [&](int k) { applyMap(k, g.data()); });
    }

    // O(N log N) -- the whole current array
    vector<T> getAll() const {
        vector<T> out(n);
        for (int i = 0; i < n; i++) out[i] = pointGet(i);
        return out;
    }

    // ---- internals ----

    int off(const T& v) const {  // v's index into a map
        long long o = (long long)v - (long long)valLo;
        if (o < 0 || o >= U) throw invalid_argument("value outside [valLo, valHi]");
        return (int)o;
    }

    void applyMap(int k, const int* g) {  // node k's segment goes through map g (newer than anything below k)
        if (k >= cap) {
            if (t[k] >= 0) {
                t[k] = g[t[k]];
            }
            return;
        }
        if (row[k] < 0) {
            row[k] = newRow();
            std::copy(g, g + U, &rows[(size_t)row[k] * U]);
        } else {
            int* m = &rows[(size_t)row[k] * U];
            for (int v = 0; v < U; v++) m[v] = g[m[v]];
        }
    }

    void applyRep(int k, int a, int b) {  // every a in node k's segment becomes b
        if (k >= cap) {
            if (t[k] == a) {
                t[k] = b;
            }
            return;
        }
        if (row[k] < 0) {
            row[k] = newRow();
            iota(&rows[(size_t)row[k] * U], &rows[(size_t)row[k] * U] + U, 0);
        }
        int* m = &rows[(size_t)row[k] * U];
        for (int v = 0; v < U; v++) if (m[v] == a) m[v] = b;
    }

    void push(int k) {  // hand node k's pending map to its children (its row is free again)
        if (row[k] < 0) return;
        gbuf.assign(rows.begin() + (size_t)row[k] * U, rows.begin() + (size_t)(row[k] + 1) * U);
        freeRows.push_back(row[k]), row[k] = -1;
        applyMap(2 * k, gbuf.data()), applyMap(2 * k + 1, gbuf.data());
    }

    int newRow() {  // a map row (a freed one if there is one)
        if (!freeRows.empty()) {
            int r = freeRows.back();
            freeRows.pop_back();
            return r;
        }
        rows.resize(rows.size() + U);
        return int(rows.size() / U) - 1;
    }

    void pushAbove(int l, int r) {  // push every map above the leaves l..r - 1 (offset by cap) down to them
        for (int h = lg; h >= 1; h--) {
            if (((l >> h) << h) != l) push(l >> h);
            if (((r >> h) << h) != r) push((r - 1) >> h);
        }
    }

    template <class F>
    void update(int l, int r, F apply) {
        l += cap, r += cap + 1;
        pushAbove(l, r);
        for (int a = l, b = r; a < b; a >>= 1, b >>= 1) {
            if (a & 1) apply(a++);
            if (b & 1) apply(--b);
        }
    }
};
