// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries/andGtX-andGteX-andInValRange-andLtX-andLteX-orGtX-orGteX-orInValRange-orLtX-orLteX-pointAdd-pointAssign-pointChmax-pointChmin-pointGet-xorGtX-xorGteX-xorInValRange-xorLtX-xorLteX/template.cpp
#include <bits/stdc++.h>
using namespace std;
using ll = long long;

// @operations: andGtX andGteX andInValRange andLtX andLteX getAll orGtX orGteX orInValRange orLtX orLteX pointAdd pointAssign pointChmax pointChmin pointGet xorGtX xorGteX xorInValRange xorLtX xorLteX
// @data-structure-type: seg-of-trees
// @complexities:
//   andGtX: log(N)*log(U)
//   andGteX: log(N)*log(U)
//   andInValRange: log(N)*log(U)
//   andLtX: log(N)*log(U)
//   andLteX: log(N)*log(U)
//   getAll: N
//   orGtX: log(N)*log(U)
//   orGteX: log(N)*log(U)
//   orInValRange: log(N)*log(U)
//   orLtX: log(N)*log(U)
//   orLteX: log(N)*log(U)
//   pointAdd: log(N)*log(U)
//   pointAssign: log(N)*log(U)
//   pointChmax: log(N)*log(U)
//   pointChmin: log(N)*log(U)
//   pointGet: 1
//   xorGtX: log(N)*log(U)
//   xorGteX: log(N)*log(U)
//   xorInValRange: log(N)*log(U)
//   xorLtX: log(N)*log(U)
//   xorLteX: log(N)*log(U)
//   build: N*log(N)*log(U)
// @memory:
//   layout: none
//   node: L[1*N*log(N)*log(U)] R[1*N*log(N)*log(U)] C[1*N*log(N)*log(U)] X[1*N*log(N)*log(U)] O[1*N*log(N)*log(U)] A[1*N*log(N)*log(U)]
//   tags: none
//   other: root[2*N] arr[1*N]
//   note: segment tree over positions (2N nodes, bottom-up), each node a dynamic value seg tree over [valLo, valHi] (U = its size); value nodes are never freed, so each point update adds up to 2 log N log U of them

// xor / OR / AND of the values in a value range inside a[l..r], with point updates. A segment tree over positions
// (bottom-up: node p >= n is a[p - n], node p < n covers its children's positions); every node keeps a dynamic value
// seg tree over [valLo, valHi] of the values at its positions: per value node, the copies below it, the xor, the OR,
// the AND
// of the values present. a[l..r] is O(log N) segment nodes, and each answers a value range in O(log U).
// Values are integers; query arguments (x, lowVal, ...) can be anything. T: int, long long, ...
template <typename T>
struct SegOfValueTrees {
    int n;
    long long vlo, vhi;
    vector<T> arr;
    vector<int> root;  // root[p]: segment node p's value tree; value node 0 = the empty tree
    struct Node {  // a node's fields side by side: a walk reads them together (faster than one array per field)
        T X = T(0);
        T O = T(0);
        T A = ~T(0);
        int L = 0;
        int R = 0;
        int C = 0;
    };
    vector<Node> nd;  // node 0 = the empty tree

    // O(N log N log U) -- arr: the initial array, 0-indexed; every value a[i] ever holds must lie in [valLo, valHi]
    // (any integers, negative is fine; U = valHi - valLo + 1)
    SegOfValueTrees(const vector<T>& a, long long valLo, long long valHi)
        : n((int)a.size()), vlo(valLo), vhi(valHi), arr(a), root(2 * n, 0), nd(1) {
        for (int i = 0; i < n; i++) add(i, a[i], 1);
    }

    // O(1) -- a[i]; needs 0 <= i < n, else throws out_of_range
    T pointGet(int i) const {
        if (i < 0 || i >= n) throw out_of_range("pointGet: needs 0 <= i < n");
        return arr[i];
    }

    // O(N) -- the whole array (a copy)
    vector<T> getAll() const { return arr; }

    // O(logN logU) -- a[i] = v; needs 0 <= i < n, else throws out_of_range
    void pointAssign(int i, T v) {
        if (i < 0 || i >= n) throw out_of_range("pointAssign: needs 0 <= i < n");
        if (v == arr[i]) return;
        add(i, arr[i], -1), add(i, v, 1), arr[i] = v;
    }

    // O(logN logU) -- a[i] += v; needs 0 <= i < n, else throws out_of_range
    void pointAdd(int i, T v) {
        if (i < 0 || i >= n) throw out_of_range("pointAdd: needs 0 <= i < n");
        pointAssign(i, arr[i] + v);
    }

    // O(logN logU) -- a[i] = max(a[i], v); needs 0 <= i < n, else throws out_of_range
    void pointChmax(int i, T v) {
        if (i < 0 || i >= n) throw out_of_range("pointChmax: needs 0 <= i < n");
        pointAssign(i, max(arr[i], v));
    }

    // O(logN logU) -- a[i] = min(a[i], v); needs 0 <= i < n, else throws out_of_range
    void pointChmin(int i, T v) {
        if (i < 0 || i >= n) throw out_of_range("pointChmin: needs 0 <= i < n");
        pointAssign(i, min(arr[i], v));
    }

    // O(logN logU) -- xor of the values < x in a[l..r] (copies count); 0 if there are none; needs 0 <= l <= r < n,
    // else throws out_of_range
    T xorLtX(int l, int r, T x) const {
        if (l < 0 || l > r || r >= n) throw out_of_range("xorLtX: needs 0 <= l <= r < n");
        return xorRange(l, r, vlo, (long long)x - 1);
    }

    // O(logN logU) -- xor of the values <= x in a[l..r] (copies count); 0 if there are none; needs 0 <= l <= r < n,
    // else throws out_of_range
    T xorLteX(int l, int r, T x) const {
        if (l < 0 || l > r || r >= n) throw out_of_range("xorLteX: needs 0 <= l <= r < n");
        return xorRange(l, r, vlo, (long long)x);
    }

    // O(logN logU) -- xor of the values > x in a[l..r] (copies count); 0 if there are none; needs 0 <= l <= r < n,
    // else throws out_of_range
    T xorGtX(int l, int r, T x) const {
        if (l < 0 || l > r || r >= n) throw out_of_range("xorGtX: needs 0 <= l <= r < n");
        return xorRange(l, r, (long long)x + 1, vhi);
    }

    // O(logN logU) -- xor of the values >= x in a[l..r] (copies count); 0 if there are none; needs 0 <= l <= r < n,
    // else throws out_of_range
    T xorGteX(int l, int r, T x) const {
        if (l < 0 || l > r || r >= n) throw out_of_range("xorGteX: needs 0 <= l <= r < n");
        return xorRange(l, r, (long long)x, vhi);
    }

    // O(logN logU) -- xor of the a[i] with lowVal <= a[i] <= highVal in a[l..r] (copies count); 0 if there are none;
    // needs 0 <= l <= r < n, else throws out_of_range
    T xorInValRange(int l, int r, T lowVal, T highVal) const {
        if (l < 0 || l > r || r >= n) throw out_of_range("xorInValRange: needs 0 <= l <= r < n");
        return xorRange(l, r, (long long)lowVal, (long long)highVal);
    }

    // O(logN logU) -- OR of the values < x in a[l..r]; 0 if there are none; needs 0 <= l <= r < n, else throws
    // out_of_range
    T orLtX(int l, int r, T x) const {
        if (l < 0 || l > r || r >= n) throw out_of_range("orLtX: needs 0 <= l <= r < n");
        return orRange(l, r, vlo, (long long)x - 1);
    }

    // O(logN logU) -- OR of the values <= x in a[l..r]; 0 if there are none; needs 0 <= l <= r < n, else throws
    // out_of_range
    T orLteX(int l, int r, T x) const {
        if (l < 0 || l > r || r >= n) throw out_of_range("orLteX: needs 0 <= l <= r < n");
        return orRange(l, r, vlo, (long long)x);
    }

    // O(logN logU) -- OR of the values > x in a[l..r]; 0 if there are none; needs 0 <= l <= r < n, else throws
    // out_of_range
    T orGtX(int l, int r, T x) const {
        if (l < 0 || l > r || r >= n) throw out_of_range("orGtX: needs 0 <= l <= r < n");
        return orRange(l, r, (long long)x + 1, vhi);
    }

    // O(logN logU) -- OR of the values >= x in a[l..r]; 0 if there are none; needs 0 <= l <= r < n, else throws
    // out_of_range
    T orGteX(int l, int r, T x) const {
        if (l < 0 || l > r || r >= n) throw out_of_range("orGteX: needs 0 <= l <= r < n");
        return orRange(l, r, (long long)x, vhi);
    }

    // O(logN logU) -- OR of the a[i] with lowVal <= a[i] <= highVal in a[l..r]; 0 if there are none; needs
    // 0 <= l <= r < n, else throws out_of_range
    T orInValRange(int l, int r, T lowVal, T highVal) const {
        if (l < 0 || l > r || r >= n) throw out_of_range("orInValRange: needs 0 <= l <= r < n");
        return orRange(l, r, (long long)lowVal, (long long)highVal);
    }

    // O(logN logU) -- AND of the values < x in a[l..r]; -1 (every bit) if there are none; needs 0 <= l <= r < n, else
    // throws out_of_range
    T andLtX(int l, int r, T x) const {
        if (l < 0 || l > r || r >= n) throw out_of_range("andLtX: needs 0 <= l <= r < n");
        return andRange(l, r, vlo, (long long)x - 1);
    }

    // O(logN logU) -- AND of the values <= x in a[l..r]; -1 (every bit) if there are none; needs 0 <= l <= r < n,
    // else throws out_of_range
    T andLteX(int l, int r, T x) const {
        if (l < 0 || l > r || r >= n) throw out_of_range("andLteX: needs 0 <= l <= r < n");
        return andRange(l, r, vlo, (long long)x);
    }

    // O(logN logU) -- AND of the values > x in a[l..r]; -1 (every bit) if there are none; needs 0 <= l <= r < n, else
    // throws out_of_range
    T andGtX(int l, int r, T x) const {
        if (l < 0 || l > r || r >= n) throw out_of_range("andGtX: needs 0 <= l <= r < n");
        return andRange(l, r, (long long)x + 1, vhi);
    }

    // O(logN logU) -- AND of the values >= x in a[l..r]; -1 (every bit) if there are none; needs 0 <= l <= r < n,
    // else throws out_of_range
    T andGteX(int l, int r, T x) const {
        if (l < 0 || l > r || r >= n) throw out_of_range("andGteX: needs 0 <= l <= r < n");
        return andRange(l, r, (long long)x, vhi);
    }

    // O(logN logU) -- AND of the a[i] with lowVal <= a[i] <= highVal in a[l..r]; -1 (every bit) if there are none;
    // needs 0 <= l <= r < n, else throws out_of_range
    T andInValRange(int l, int r, T lowVal, T highVal) const {
        if (l < 0 || l > r || r >= n) throw out_of_range("andInValRange: needs 0 <= l <= r < n");
        return andRange(l, r, (long long)lowVal, (long long)highVal);
    }

    // ---- internals ----

    // a[i] = v gains d copies in every segment node over i
    void add(int i, T v, int d) {
        for (int p = i + n; p; p >>= 1) {
            int t = ins(root[p], v, d);
            root[p] = t;
        }
    }

    int newNode() {
        Node n;
        n.L = 0, n.R = 0, n.C = 0, n.X = T(0), n.O = T(0), n.A = ~T(0);
        nd.push_back(n);
        return (int)nd.size() - 1;
    }

    // value tree t (0: a new one) with d more copies of v
    int ins(int t, T v, int d) {
        if (!t) t = newNode();
        int top = t;
        long long nl = vlo, nh = vhi;
        int path[130], dep = 0;
        while (true) {
            nd[t].C += d;
            if (d & 1) nd[t].X ^= v;
            path[dep++] = t;
            if (nl == nh) break;
            long long mid = nl + (nh - nl) / 2;
            if (v <= mid) {
                if (!nd[t].L) { int x = newNode(); nd[t].L = x; }
                t = nd[t].L, nh = mid;
            } else {
                if (!nd[t].R) { int x = newNode(); nd[t].R = x; }
                t = nd[t].R, nl = mid + 1;
            }
        }
        if (!nd[t].C || nd[t].C == d) {  // v appeared or disappeared here: OR / AND again up the path
            nd[t].O = nd[t].C ? v : T(0);
            nd[t].A = nd[t].C ? v : ~T(0);
            for (int k = dep - 2; k >= 0; k--) {
                int u = path[k];
                nd[u].O = nd[nd[u].L].O | nd[nd[u].R].O;
                nd[u].A = nd[nd[u].L].A & nd[nd[u].R].A;
            }
        }
        return top;
    }

    // xor of the values in [lo, hi] over a[l..r]: the segment nodes covering [l, r], each a value range walk
    T xorRange(int l, int r, long long lo, long long hi) const {
        T res = T(0);
        if (lo > hi) return res;
        for (l += n, r += n + 1; l < r; l >>= 1, r >>= 1) {
            if (l & 1) res ^= xorIn(root[l++], lo, hi);
            if (r & 1) res ^= xorIn(root[--r], lo, hi);
        }
        return res;
    }

    // xor of value tree t's values in [lo, hi]: whole value nodes inside it, at most 4 a level
    T xorIn(int t, long long lo, long long hi) const {
        T res = T(0);
        array<long long, 3> st[260];
        int sp = 0;
        st[sp++] = {t, vlo, vhi};
        while (sp) {
            auto [u, nl, nh] = st[--sp];
            if (!u || nh < lo || hi < nl) continue;
            if (lo <= nl && nh <= hi) {
                res ^= nd[u].X;
                continue;
            }
            long long mid = nl + (nh - nl) / 2;
            st[sp++] = {nd[u].L, nl, mid};
            st[sp++] = {nd[u].R, mid + 1, nh};
        }
        return res;
    }

    // OR of the values in [lo, hi] over a[l..r]: the segment nodes covering [l, r], each a value range walk
    T orRange(int l, int r, long long lo, long long hi) const {
        T res = T(0);
        if (lo > hi) return res;
        for (l += n, r += n + 1; l < r; l >>= 1, r >>= 1) {
            if (l & 1) res |= orIn(root[l++], lo, hi);
            if (r & 1) res |= orIn(root[--r], lo, hi);
        }
        return res;
    }

    // OR of value tree t's values in [lo, hi]: whole value nodes inside it, at most 4 a level
    T orIn(int t, long long lo, long long hi) const {
        T res = T(0);
        array<long long, 3> st[260];
        int sp = 0;
        st[sp++] = {t, vlo, vhi};
        while (sp) {
            auto [u, nl, nh] = st[--sp];
            if (!u || nh < lo || hi < nl) continue;
            if (lo <= nl && nh <= hi) {
                res |= nd[u].O;
                continue;
            }
            long long mid = nl + (nh - nl) / 2;
            st[sp++] = {nd[u].L, nl, mid};
            st[sp++] = {nd[u].R, mid + 1, nh};
        }
        return res;
    }

    // AND of the values in [lo, hi] over a[l..r]: the segment nodes covering [l, r], each a value range walk
    T andRange(int l, int r, long long lo, long long hi) const {
        T res = ~T(0);
        if (lo > hi) return res;
        for (l += n, r += n + 1; l < r; l >>= 1, r >>= 1) {
            if (l & 1) res &= andIn(root[l++], lo, hi);
            if (r & 1) res &= andIn(root[--r], lo, hi);
        }
        return res;
    }

    // AND of value tree t's values in [lo, hi]: whole value nodes inside it, at most 4 a level
    T andIn(int t, long long lo, long long hi) const {
        T res = ~T(0);
        array<long long, 3> st[260];
        int sp = 0;
        st[sp++] = {t, vlo, vhi};
        while (sp) {
            auto [u, nl, nh] = st[--sp];
            if (!u || nh < lo || hi < nl) continue;
            if (lo <= nl && nh <= hi) {
                res &= nd[u].A;
                continue;
            }
            long long mid = nl + (nh - nl) / 2;
            st[sp++] = {nd[u].L, nl, mid};
            st[sp++] = {nd[u].R, mid + 1, nh};
        }
        return res;
    }
};
