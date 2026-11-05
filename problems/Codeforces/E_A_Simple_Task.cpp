#include <bits/stdc++.h>
using namespace std;
using ll = long long;
constexpr int ALPHA = 26;

struct Node {
    int cnt[ALPHA] = {};
    int width = 0;
};

struct Tag {
    char lazyAssign = -1; // -1 is a sentinel, otherwise 0 means assign this range to A, 1 to B, etc
};

struct Seg {
    int n;
    vector<Node> tree;
    vector<Tag> lazy;
    void _build(int nodeI, int tl, int tr, string& s) {
        if (tl == tr) {
            char c = s[tl];
            int idx = c - 'a';
            tree[nodeI].cnt[idx]++;
            tree[nodeI].width = 1;
            return;
        }
        int tm = (tl + tr) / 2;
        _build(2 * nodeI, tl, tm, s);
        _build(2 * nodeI + 1, tm + 1 , tr, s);
        _pull(nodeI);
    }
    void _pull(int nodeI) {
        tree[nodeI] = _combine(tree[2*nodeI],tree[2*nodeI+1]);
    }
    Node _combine(Node& a, Node&b) {
        Node out;
        for (int i = 0; i < ALPHA; i++) {
            out.cnt[i] = a.cnt[i] + b.cnt[i];
        }
        out.width = a.width + b.width;
        return out;
    }
    Seg(string& s) {
        n = s.size();
        tree.resize(4 * n);
        lazy.resize(4 * n);
        _build(1, 0, n - 1, s);
    }
    Tag _compose(Tag& a, Tag& b) {
        return b;
    }
    void _applyTagAndCompose(int nodeI, Tag t) {
        if (t.lazyAssign == -1) return;
        Node& node = tree[nodeI];
        for (int i = 0; i < ALPHA; i++) {
            if (i == t.lazyAssign) {
                node.cnt[i] = node.width;
            } else {
                node.cnt[i] = 0;
            }
        }
        lazy[nodeI] = _compose(lazy[nodeI], t);
    }
    void _pushDownAndClear(int nodeI) {
        _applyTagAndCompose(2 * nodeI, lazy[nodeI]);
        _applyTagAndCompose(2 * nodeI + 1, lazy[nodeI]);
        lazy[nodeI] = {-1};
    }
    Node _query(int nodeI, int tl, int tr, int ql, int qr) {
        // fully inside
        if (ql <= tl && qr >= tr) {
            return tree[nodeI];
        }
        _pushDownAndClear(nodeI);
        int tm = (tl + tr) / 2;
        if (qr <= tm) {
            Node left = _query(2 * nodeI, tl, tm, ql, qr);
            return left;
        } else if (ql >= tm + 1) {
            Node right = _query(2 * nodeI + 1, tm + 1, tr, ql, qr);
            return right;
        }
        Node left = _query(2 * nodeI, tl, tm, ql, qr);
        Node right = _query(2 * nodeI + 1, tm + 1, tr, ql, qr);
        return _combine(left, right);
    }
    Node query(int l, int r) {
        return _query(1, 0, n - 1, l, r);
    }
    void _rangeAssign(int nodeI, int tl, int tr, int ql, int qr, int newIdx) {
        // oob
        if (qr < tl || ql > tr) return;
        // fully inside
        if (ql <= tl && qr >= tr) {
            Tag t; t.lazyAssign = newIdx;
            _applyTagAndCompose(nodeI, t);
            return;
        }
        _pushDownAndClear(nodeI);
        int tm = (tl + tr) / 2;
        _rangeAssign(2 * nodeI, tl, tm, ql, qr, newIdx);
        _rangeAssign(2 * nodeI + 1, tm + 1, tr, ql, qr, newIdx);
        _pull(nodeI);
    }
    void rangeAssign(int l, int r, int idx) {
        _rangeAssign(1, 0, n - 1, l, r, idx);
    }
};

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n, q; cin >> n >> q;
    string s; cin >> s;
    Seg seg(s);
    while (q--) {
        int l, r, qtype; cin >> l >> r >> qtype; l--; r--;
        Node counts = seg.query(l, r);
        int currL = l;
        if (qtype == 1) {
            for (int idx = 0; idx < ALPHA; idx++) {
                if (counts.cnt[idx] == 0) {
                    continue;
                }
                int right = currL + counts.cnt[idx] - 1;
                seg.rangeAssign(currL, right, idx);
                currL = right + 1;
            }
        } else {
            for (int idx = ALPHA - 1; idx >= 0; idx--) {
                if (counts.cnt[idx] == 0) {
                    continue;
                }
                int right = currL + counts.cnt[idx] - 1;
                seg.rangeAssign(currL, right, idx);
                currL = right + 1;
            }         
        }
    }
    string out(n, '?');
    for (int i = 0; i < n; i++) {
        Node leaf = seg.query(i, i);
        for (int c = 0; c < ALPHA; c++) {
            if (leaf.cnt[c]) {
                out[i] = 'a' + c; break;
            }
        }
    }
    cout << out << endl;

}

// SOLN 2
#include<bits/stdc++.h>
using namespace std;

// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/pointAssign-pointGet-rangeSortAsc-rangeSortDesc-rangeSum/template.cpp
// @operations: getAll pointAssign pointGet rangeSortAsc rangeSortDesc rangeSum
// @data-structure-type: sorted-runs
// @complexities:
//   getAll: N*log(U)
//   pointAssign: log(N)+log(U) amortized
//   pointGet: log(N)+log(U)
//   rangeSortAsc: log(N)+log(U) amortized
//   rangeSortDesc: log(N)+log(U) amortized
//   rangeSum: log(N)+log(U) amortized
//   build: N*log(U)
// @memory:
//   layout: none
//   node: Lc[1*N*log(U)] Rc[1*N*log(U)] cnt[1*N*log(U)] sm[1*N*log(U)]
//   tags: none
//   other: root[1*N] desc[1*N] len[1*N] starts[1*N] sums[1*N]
//   note: value nodes: N log U to start, plus O(log U) per split or point write (merges free nodes, which are reused); U = valHi - valLo + 1

// An array whose ranges you can sort in place (ascending or descending), amortized O(log N + log U) a sort, with point
// reads / writes, range sums and the whole array. It is kept as a sequence of sorted runs: each run is a dynamic value
// seg tree over [valLo, valHi] (copies and their sum per node) and an up / down flag, and a Fenwick tree over positions
// marks where runs start (another holds each run's sum at its start). Sorting [l, r] splits the runs at l and r + 1 and
// merges every run inside into one; a[i] is the k-th value of the run holding it. Merges cost about as many nodes as
// they free and every run is merged away at most once, hence the amortized bounds. Indices 0-based, ranges inclusive.
// T: int, long long, ...; sums in S (long long for small T).
template <typename T>
struct RangeSortArray {
    using S = conditional_t<(sizeof(T) < sizeof(long long)), long long, T>;
    int n, top;
    long long vlo, vhi;
    vector<int> Lc{0}, Rc{0}, freeList;  // value node 0 = the empty tree; nodes freed by merges are reused first
    vector<long long> cnt{0};
    vector<S> sm{S(0)};
    vector<int> root, len;  // per run start: its value tree, its length
    vector<char> desc;      // per run start: sorted descending?
    vector<long long> bc;   // Fenwick: 1 at each run start
    vector<S> bs;           // Fenwick: each run's sum, at its start

    // O(N log U) -- arr: the initial array; every value a[i] ever holds must lie in [valLo, valHi] (U = valHi - valLo + 1)
    RangeSortArray(const vector<T>& arr, long long valLo, long long valHi)
        : n((int)arr.size()), vlo(valLo), vhi(valHi), root(n), len(n, 1), desc(n, 0), bc(n + 1, 0), bs(n + 1, S(0)) {
        top = n ? 1 << (31 - __builtin_clz(n)) : 0;
        for (int i = 0; i < n; i++) root[i] = leaf(arr[i]), fen(bc, i, 1LL), fen(bs, i, S(arr[i]));
    }

    // O(log N + log U) -- a[i]
    T pointGet(int i) {
        int s = startOf(i), k = i - s;
        return kth(root[s], desc[s] ? len[s] - k : k + 1);
    }

    // O(log N + log U) amortized -- a[i] = v
    void pointAssign(int i, T v) {
        cutAt(i), cutAt(i + 1);
        fen(bs, i, S(v) - sm[root[i]]);
        freeTree(root[i]);
        int t = leaf(v);
        root[i] = t;
    }

    // O(log N + log U) amortized -- sort a[l..r] ascending
    void rangeSortAsc(int l, int r) { sortRange(l, r, false); }

    // O(log N + log U) amortized -- sort a[l..r] descending
    void rangeSortDesc(int l, int r) { sortRange(l, r, true); }

    // O(log N + log U) amortized -- a[l] + ... + a[r] (cuts the runs at l and r + 1, then the run sums in between)
    S rangeSum(int l, int r) {
        cutAt(l), cutAt(r + 1);
        return pre(bs, r + 1) - pre(bs, l);
    }

    // O(N log U) -- the whole current array
    vector<T> getAll() const {
        vector<T> out;
        out.reserve(n);
        for (int s = 0; s < n; s += len[s]) {
            size_t from = out.size();
            vector<tuple<int, long long, long long>> st{{root[s], vlo, vhi}};
            while (!st.empty()) {  // in-order, pushed right first
                auto [t, nl, nh] = st.back();
                st.pop_back();
                if (!cnt[t]) continue;
                if (nl == nh) {
                    out.insert(out.end(), cnt[t], T(nl));
                    continue;
                }
                long long mid = nl + (nh - nl) / 2;
                st.push_back({Rc[t], mid + 1, nh}), st.push_back({Lc[t], nl, mid});
            }
            if (desc[s]) reverse(out.begin() + from, out.end());
        }
        return out;
    }

    // ---- internals: runs ----

    void sortRange(int l, int r, bool d) {
        cutAt(l), cutAt(r + 1);
        int t = root[l];
        S old = sm[t];
        for (int s = l + len[l]; s <= r;) {  // every run inside merges into the first
            int b = root[s], nxt = s + len[s];
            fen(bc, s, -1LL), fen(bs, s, -sm[b]);
            t = merge(t, b, vlo, vhi);
            s = nxt;
        }
        fen(bs, l, sm[t] - old);
        root[l] = t, len[l] = r - l + 1, desc[l] = d;
    }

    // make a run start at p (0 < p < n): split the run holding it by count
    void cutAt(int p) {
        if (p <= 0 || p >= n) return;
        int s = startOf(p);
        if (s == p) return;
        int t = root[s], k = p - s, ln = len[s], a, b;
        if (desc[s]) split(t, ln - k, vlo, vhi, b, a);  // the first k are the k largest
        else split(t, k, vlo, vhi, a, b);
        root[s] = a, len[s] = k;
        root[p] = b, len[p] = ln - k, desc[p] = desc[s];
        fen(bc, p, 1LL), fen(bs, s, -sm[b]), fen(bs, p, sm[b]);
    }

    // the start of the run holding i: the (# of starts <= i)-th start, by binary lifting
    int startOf(int i) const {
        long long k = pre(bc, i + 1);
        int pos = 0;
        for (int step = top; step; step >>= 1)
            if (pos + step <= n && bc[pos + step] < k) pos += step, k -= bc[pos];
        return pos;
    }

    template <class V>
    void fen(vector<V>& f, int i, V v) {
        for (i++; i <= n; i += i & -i) f[i] += v;
    }

    template <class V>
    static V pre(const vector<V>& f, int i) {  // f's total over positions 0..i-1
        V s = 0;
        for (; i > 0; i &= i - 1) s += f[i];
        return s;
    }

    // ---- internals: value trees (copies and sum per node; node 0 = empty) ----

    int node() {
        if (!freeList.empty()) {
            int t = freeList.back();
            freeList.pop_back();
            Lc[t] = Rc[t] = 0, cnt[t] = 0, sm[t] = 0;
            return t;
        }
        Lc.push_back(0), Rc.push_back(0), cnt.push_back(0), sm.push_back(S(0));
        return (int)cnt.size() - 1;
    }

    void freeTree(int t) {  // hand every node of t back
        vector<int> st;
        if (t) st.push_back(t);
        while (!st.empty()) {
            int u = st.back();
            st.pop_back();
            freeList.push_back(u);
            if (Lc[u]) st.push_back(Lc[u]);
            if (Rc[u]) st.push_back(Rc[u]);
        }
    }

    // a tree holding one copy of v: one node per level
    int leaf(T v) {
        int top_ = node(), t = top_;
        long long nl = vlo, nh = vhi;
        while (true) {
            cnt[t] = 1, sm[t] = S(v);
            if (nl == nh) return top_;
            long long mid = nl + (nh - nl) / 2;
            int u = node();
            if (v <= mid) Lc[t] = u, nh = mid;
            else Rc[t] = u, nl = mid + 1;
            t = u;
        }
    }

    // a = the k smallest of t, b = the rest (0 <= k <= cnt[t]); t keeps the first part, new nodes hold the second
    void split(int t, long long k, long long nl, long long nh, int& a, int& b) {
        if (k <= 0) { a = 0, b = t; return; }
        if (k >= cnt[t]) { a = t, b = 0; return; }
        int nb = node();
        if (nl == nh) {  // one value, split copies
            cnt[nb] = cnt[t] - k, sm[nb] = S(cnt[nb]) * S(nl);
            cnt[t] = k, sm[t] = S(k) * S(nl);
            a = t, b = nb;
            return;
        }
        long long mid = nl + (nh - nl) / 2, cl = cnt[Lc[t]];
        int x, y;
        if (k <= cl) {
            split(Lc[t], k, nl, mid, x, y);
            Lc[t] = x, Lc[nb] = y, Rc[nb] = Rc[t], Rc[t] = 0;
        } else {
            split(Rc[t], k - cl, mid + 1, nh, x, y);
            Rc[t] = x, Rc[nb] = y;
        }
        for (int u : {t, nb}) cnt[u] = cnt[Lc[u]] + cnt[Rc[u]], sm[u] = sm[Lc[u]] + sm[Rc[u]];
        a = t, b = nb;
    }

    // the union of a and b (b's nodes are freed)
    int merge(int a, int b, long long nl, long long nh) {
        if (!a || !b) return a ? a : b;
        cnt[a] += cnt[b], sm[a] += sm[b];
        if (nl != nh) {
            long long mid = nl + (nh - nl) / 2;
            int x = merge(Lc[a], Lc[b], nl, mid);
            Lc[a] = x;
            int y = merge(Rc[a], Rc[b], mid + 1, nh);
            Rc[a] = y;
        }
        freeList.push_back(b);
        return a;
    }

    // the k-th smallest value of t, 1 <= k <= cnt[t]
    T kth(int t, long long k) const {
        long long nl = vlo, nh = vhi;
        while (nl != nh) {
            long long mid = nl + (nh - nl) / 2, cl = cnt[Lc[t]];
            if (k <= cl) t = Lc[t], nh = mid;
            else k -= cl, t = Rc[t], nl = mid + 1;
        }
        return T(nl);
    }
};


int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n, q; cin >> n >> q;
    string s; cin >> s;
    vector<int>A(n);
    for (int i = 0; i < n; i++) {
        A[i] = s[i] - 'a';
    }
    RangeSortArray seg(A, 0, 25);
    for (int i = 0; i < q; i++) {
        int l, r, qtype; cin >>l >> r >> qtype; l--; r--;
        if (qtype == 1) {
            seg.rangeSortAsc(l, r);
        } else {
            seg.rangeSortDesc(l, r);
        }
    }
    string abc = "abcdefghijklmnopqrstuvwxyz";
    vector<int> out = seg.getAll();
    for (int i = 0; i < n; i++) {
        cout << abc[out[i]];
    }
}