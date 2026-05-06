#include <bits/stdc++.h>
using namespace std;
using ll = long long;

const int MAX_N = 100000;
const ll B1 = 131, MOD1 = 1000000007;
const ll B2 = 137, MOD2 = 998244353;

ll repHash1[MAX_N + 1], powHash1[MAX_N + 1];
ll repHash2[MAX_N + 1], powHash2[MAX_N + 1];

inline ll uniformHash1(ll c, ll sz) { return c * repHash1[sz] % MOD1; }
inline ll uniformHash2(ll c, ll sz) { return c * repHash2[sz] % MOD2; }

inline ll concat1(ll hl, ll hr, ll szR) { return (hl * powHash1[szR] + hr) % MOD1; }
inline ll concat2(ll hl, ll hr, ll szR) { return (hl * powHash2[szR] + hr) % MOD2; }

struct Node {
    ll h1 = 0, h2 = 0;
    ll sz = 1;
};

struct Tag {
    int pending = -1;
};

struct Seg {
    int n;
    vector<Node> tree;
    vector<Tag> lazy;

    Seg(const vector<int>& A) {
        n = A.size();
        tree.resize(4 * n); lazy.resize(4 * n);
        _build(1, 0, n - 1, A);
    }

    void _build(int nodeI, int tl, int tr, const vector<int>& A) {
        if (tl == tr) { tree[nodeI] = {A[tl], A[tl], 1}; return; }
        int tm = (tl + tr) / 2;
        _build(2*nodeI, tl, tm, A);
        _build(2*nodeI+1, tm+1, tr, A);
        _pull(nodeI);
    }

    Node _combine(Node& a, Node& b) {
        Node out;
        out.h1 = concat1(a.h1, b.h1, b.sz);
        out.h2 = concat2(a.h2, b.h2, b.sz);
        out.sz = a.sz + b.sz;
        return out;
    }

    void _pull(int nodeI) { tree[nodeI] = _combine(tree[2*nodeI], tree[2*nodeI+1]); }

    void _applyAndCompose(int nodeI, Tag t) {
        if (t.pending == -1) return;
        tree[nodeI].h1 = uniformHash1(t.pending, tree[nodeI].sz);
        tree[nodeI].h2 = uniformHash2(t.pending, tree[nodeI].sz);
        lazy[nodeI] = t;
    }

    void _pushDownAndClear(int nodeI) {
        if (lazy[nodeI].pending == -1) return;
        _applyAndCompose(2*nodeI, lazy[nodeI]);
        _applyAndCompose(2*nodeI+1, lazy[nodeI]);
        lazy[nodeI] = {-1};
    }

    void _rangeAssign(int nodeI, int tl, int tr, int ql, int qr, int v) {
        if (qr < tl || ql > tr) return;
        if (ql <= tl && qr >= tr) { _applyAndCompose(nodeI, {v}); return; }
        _pushDownAndClear(nodeI);
        int tm = (tl + tr) / 2;
        _rangeAssign(2*nodeI, tl, tm, ql, qr, v);
        _rangeAssign(2*nodeI+1, tm+1, tr, ql, qr, v);
        _pull(nodeI);
    }

    void rangeAssign(int l, int r, int v) { _rangeAssign(1, 0, n-1, l, r, v); }

    Node _query(int nodeI, int tl, int tr, int ql, int qr) {
        if (qr < tl || ql > tr) return Node{0, 0, 0};
        if (ql <= tl && qr >= tr) return tree[nodeI];
        _pushDownAndClear(nodeI);
        int tm = (tl + tr) / 2;
        Node L = _query(2*nodeI, tl, tm, ql, qr);
        Node R = _query(2*nodeI+1, tm+1, tr, ql, qr);
        return _combine(L, R);
    }

    Node query(int l, int r) { return _query(1, 0, n-1, l, r); }
};

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    repHash1[0] = 0; powHash1[0] = 1;
    repHash2[0] = 0; powHash2[0] = 1;
    for (int i = 1; i <= MAX_N; i++) {
        repHash1[i] = (repHash1[i-1] * B1 + 1) % MOD1;
        powHash1[i] = powHash1[i-1] * B1 % MOD1;
        repHash2[i] = (repHash2[i-1] * B2 + 1) % MOD2;
        powHash2[i] = powHash2[i-1] * B2 % MOD2;
    }

    int n, m, k; cin >> n >> m >> k;
    string s; cin >> s;
    vector<int> A(n);
    for (int i = 0; i < n; i++) A[i] = s[i] - '0';

    Seg seg(A);
    for (int i = 0; i < m + k; i++) {
        int qtype; cin >> qtype;
        if (qtype == 1) {
            int l, r, c; cin >> l >> r >> c; l--; r--;
            seg.rangeAssign(l, r, c);
        } else {
            int l, r, d; cin >> l >> r >> d; l--; r--;
            if (l + d > r) { cout << "YES\n"; continue; }
            Node q1 = seg.query(l, r - d);
            Node q2 = seg.query(l + d, r);
            cout << (q1.h1 == q2.h1 && q1.h2 == q2.h2 ? "YES" : "NO") << "\n";
        }
    }
}