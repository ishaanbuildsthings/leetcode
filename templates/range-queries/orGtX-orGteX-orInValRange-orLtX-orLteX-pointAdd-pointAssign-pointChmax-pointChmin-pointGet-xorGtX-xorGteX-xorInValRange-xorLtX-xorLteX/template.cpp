// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/orGtX-orGteX-orInValRange-orLtX-orLteX-pointAdd-pointAssign-pointChmax-pointChmin-pointGet-xorGtX-xorGteX-xorInValRange-xorLtX-xorLteX/template.cpp
// @operations: getAll orGtX orGteX orInValRange orLtX orLteX pointAdd pointAssign pointChmax pointChmin pointGet xorGtX xorGteX xorInValRange xorLtX xorLteX
// @data-structure-type: seg-of-trees
// @complexities:
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
//   node: L[1*N*log(N)*log(U)] R[1*N*log(N)*log(U)] C[1*N*log(N)*log(U)] X[1*N*log(N)*log(U)] O[1*N*log(N)*log(U)]
//   tags: none
//   other: root[2*N] arr[1*N]
//   note: segment tree over positions (2N nodes, bottom-up), each node a dynamic value seg tree over [valLo, valHi] (U = its size); value nodes are never freed, so each point update adds up to 2 log N log U of them

// xor / OR / AND of the values in a value range inside a[l..r], with point updates. A segment tree over positions
// (bottom-up: node p >= n is a[p - n], node p < n covers its children's positions); every node keeps a dynamic value
// seg tree over [valLo, valHi] of the values at its positions: per value node, the copies below it, the xor, the OR
// of the values present. a[l..r] is O(log N) segment nodes, and each answers a value range in O(log U).
// Values are integers; query arguments (x, lowVal, ...) can be anything. T: int, long long, ...
template <typename T>
struct SegOfValueTrees {
    int n;
    long long vlo, vhi;
    vector<T> arr;
    vector<int> root, L, R, C;  // root[p]: segment node p's value tree; value node 0 = the empty tree
    vector<T> X;  // xor of the values present below
    vector<T> O;  // OR of the values present below

    // O(N log N log U) -- arr: the initial array, 0-indexed; every value a[i] ever holds must lie in [valLo, valHi]
    // (any integers, negative is fine; U = valHi - valLo + 1)
    SegOfValueTrees(const vector<T>& a, long long valLo, long long valHi)
        : n((int)a.size()), vlo(valLo), vhi(valHi), arr(a), root(2 * n, 0), L(1, 0), R(1, 0), C(1, 0), X(1, T(0)), O(1, T(0)) {
        for (int i = 0; i < n; i++) add(i, a[i], 1);
    }

    // O(1) -- a[i]
    T pointGet(int i) const { return arr[i]; }

    // O(N) -- the whole array (a copy)
    vector<T> getAll() const { return arr; }

    // O(logN logU) -- a[i] = v
    void pointAssign(int i, T v) {
        if (v == arr[i]) return;
        add(i, arr[i], -1), add(i, v, 1), arr[i] = v;
    }

    // O(logN logU) -- a[i] += v
    void pointAdd(int i, T v) { pointAssign(i, arr[i] + v); }

    // O(logN logU) -- a[i] = max(a[i], v)
    void pointChmax(int i, T v) { pointAssign(i, max(arr[i], v)); }

    // O(logN logU) -- a[i] = min(a[i], v)
    void pointChmin(int i, T v) { pointAssign(i, min(arr[i], v)); }

    // O(logN logU) -- xor of the values < x in a[l..r] (copies count); 0 if there are none
    T xorLtX(int l, int r, T x) const { return xorRange(l, r, vlo, (long long)x - 1); }

    // O(logN logU) -- xor of the values <= x in a[l..r] (copies count); 0 if there are none
    T xorLteX(int l, int r, T x) const { return xorRange(l, r, vlo, (long long)x); }

    // O(logN logU) -- xor of the values > x in a[l..r] (copies count); 0 if there are none
    T xorGtX(int l, int r, T x) const { return xorRange(l, r, (long long)x + 1, vhi); }

    // O(logN logU) -- xor of the values >= x in a[l..r] (copies count); 0 if there are none
    T xorGteX(int l, int r, T x) const { return xorRange(l, r, (long long)x, vhi); }

    // O(logN logU) -- xor of the a[i] with lowVal <= a[i] <= highVal in a[l..r] (copies count); 0 if there are none
    T xorInValRange(int l, int r, T lowVal, T highVal) const { return xorRange(l, r, (long long)lowVal, (long long)highVal); }

    // O(logN logU) -- OR of the values < x in a[l..r]; 0 if there are none
    T orLtX(int l, int r, T x) const { return orRange(l, r, vlo, (long long)x - 1); }

    // O(logN logU) -- OR of the values <= x in a[l..r]; 0 if there are none
    T orLteX(int l, int r, T x) const { return orRange(l, r, vlo, (long long)x); }

    // O(logN logU) -- OR of the values > x in a[l..r]; 0 if there are none
    T orGtX(int l, int r, T x) const { return orRange(l, r, (long long)x + 1, vhi); }

    // O(logN logU) -- OR of the values >= x in a[l..r]; 0 if there are none
    T orGteX(int l, int r, T x) const { return orRange(l, r, (long long)x, vhi); }

    // O(logN logU) -- OR of the a[i] with lowVal <= a[i] <= highVal in a[l..r]; 0 if there are none
    T orInValRange(int l, int r, T lowVal, T highVal) const { return orRange(l, r, (long long)lowVal, (long long)highVal); }

    // ---- internals ----

    // a[i] = v gains d copies in every segment node over i
    void add(int i, T v, int d) {
        for (int p = i + n; p; p >>= 1) {
            int t = ins(root[p], v, d);
            root[p] = t;
        }
    }

    int newNode() {
        L.push_back(0), R.push_back(0), C.push_back(0);
        X.push_back(T(0));
        O.push_back(T(0));
        return (int)C.size() - 1;
    }

    // value tree t (0: a new one) with d more copies of v
    int ins(int t, T v, int d) {
        if (!t) t = newNode();
        int top = t;
        long long nl = vlo, nh = vhi;
        int path[130], dep = 0;
        while (true) {
            C[t] += d;
            if (d & 1) X[t] ^= v;
            path[dep++] = t;
            if (nl == nh) break;
            long long mid = nl + (nh - nl) / 2;
            if (v <= mid) {
                if (!L[t]) { int x = newNode(); L[t] = x; }
                t = L[t], nh = mid;
            } else {
                if (!R[t]) { int x = newNode(); R[t] = x; }
                t = R[t], nl = mid + 1;
            }
        }
        if (!C[t] || C[t] == d) {  // v appeared or disappeared here: OR / AND again up the path
            O[t] = C[t] ? v : T(0);
            for (int k = dep - 2; k >= 0; k--) {
                int u = path[k];
                O[u] = O[L[u]] | O[R[u]];
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
                res ^= X[u];
                continue;
            }
            long long mid = nl + (nh - nl) / 2;
            st[sp++] = {L[u], nl, mid};
            st[sp++] = {R[u], mid + 1, nh};
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
                res |= O[u];
                continue;
            }
            long long mid = nl + (nh - nl) / 2;
            st[sp++] = {L[u], nl, mid};
            st[sp++] = {R[u], mid + 1, nh};
        }
        return res;
    }
};
