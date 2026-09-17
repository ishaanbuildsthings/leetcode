// TEMPLATE BY https://github.com/agrawalishaan

// ========================
// COMPLEXITIES

// O(n) build
// LazyClamp_PERFORMANT seg(arr);

// O(logN):  rangeChmin(l, r, x)    -- a[i] = min(a[i], x)
// O(logN):  rangeChmax(l, r, x)    -- a[i] = max(a[i], x)
// O(logN):  rangeAdd(l, r, x)      -- a[i] += x
// O(logN):  rangeAssign(l, r, x)   -- a[i] = x
// O(logN):  pointSet(pos, newVal)

// O(logN):  rangeMin(l, r)
// O(logN):  rangeMax(l, r)
// O(logN):  pointGet(pos)
// O(n) space

// NOT BEATS -- a completely normal lazy segment tree, NOT amortized, worst case logN per op.
// NO rangeSum. That is the whole catch, and it is why segment tree beats has to exist.

// ========================
/**
WHY THIS WORKS (and why there is no sum)

Any sequence of chmin / chmax / add collapses into a SINGLE closed form:

    f(x) = min(a, max(b, x + c))

three numbers, so it is an ordinary lazy tag. Reading it inside out: shift by c, floor at b, cap at
a. That is add-BEFORE-clamp, but it is not a restriction on the order you call things -- an add
arriving AFTER a clamp just gets pushed through, since adding v to min(a, max(b, x+c)) gives
min(a+v, max(b+v, x+c+v)), so all three constants shift and the shape survives.

Composing a new g = (a, b, c) on top of a stored f = (A, B, C):
    newA = min(a, max(b, A + c))
    newB = max(b, B + c)
    newC = C + c
    if (newA < newB) newB = newA;   // the window collapsed, f is now the constant newA

The individual ops are just special cases:
    add v     -> (+INF, -INF, v)
    chmin v   -> (v,    -INF, 0)
    chmax v   -> (+INF, v,    0)
    assign v  -> (v,    v,    0)

min and max survive because f is monotone non-decreasing, so the smallest element is still the
smallest after the shift and both clamps. You just run the node's stored mn and mx through f.

SUM DOES NOT SURVIVE. A node holding [1, 9] and a node holding [5, 5] both have sum 10, and
clamping both at 5 gives 6 and 10. Same sum in, same operation, different sum out -- so there is no
function of (sum, size, tag) that gives the answer. The result genuinely depends on the individual
values, which a node does not store. THAT is the dividing line: if you need sum, you need beats
(and you pay a second log for the add).

Classic problem: IOI 2014 Wall.
*/

// ========================


#include <bits/stdc++.h>
using namespace std;
using ll = long long;

static const ll NEG_INF = LLONG_MIN / 4;
static const ll POS_INF = LLONG_MAX / 4;

struct LazyClamp {
    struct Node { ll mn, mx; ll A, B, C; };
    int n;
    vector<Node> t;

    static ll _shift(ll v, ll c) {
        if (v >= POS_INF) return POS_INF;
        if (v <= NEG_INF) return NEG_INF;
        ll r = v + c;
        if (r > POS_INF) return POS_INF;
        if (r < NEG_INF) return NEG_INF;
        return r;
    }
    static ll _eval(ll x, ll a, ll b, ll c) {
        ll v = _shift(x, c);
        if (v < b) v = b;
        if (v > a) v = a;
        return v;
    }

    explicit LazyClamp(const vector<ll>& arr) {
        n = (int)arr.size();
        t.assign(4 * max(1, n), Node{});
        if (n) _build(1, 0, n - 1, arr);
    }

    void _build(int i, int tl, int tr, const vector<ll>& arr) {
        t[i].A = POS_INF; t[i].B = NEG_INF; t[i].C = 0;
        if (tl == tr) { t[i].mn = t[i].mx = arr[tl]; return; }
        int tm = (tl + tr) / 2;
        _build(2 * i, tl, tm, arr);
        _build(2 * i + 1, tm + 1, tr, arr);
        _pull(i);
    }

    void _pull(int i) {
        t[i].mn = min(t[2 * i].mn, t[2 * i + 1].mn);
        t[i].mx = max(t[2 * i].mx, t[2 * i + 1].mx);
        t[i].A = POS_INF; t[i].B = NEG_INF; t[i].C = 0;
    }

    void _apply(int i, ll a, ll b, ll c) {
        Node& nd = t[i];
        nd.mn = _eval(nd.mn, a, b, c);
        nd.mx = _eval(nd.mx, a, b, c);
        ll nA = min(a, max(b, _shift(nd.A, c)));
        ll nB = max(b, _shift(nd.B, c));
        nd.C += c;
        if (nA < nB) nB = nA;
        nd.A = nA; nd.B = nB;
    }

    void _push(int i, int tl, int tr) {
        if (tl == tr) return;
        Node& nd = t[i];
        if (nd.A == POS_INF && nd.B == NEG_INF && nd.C == 0) return;
        _apply(2 * i, nd.A, nd.B, nd.C);
        _apply(2 * i + 1, nd.A, nd.B, nd.C);
        nd.A = POS_INF; nd.B = NEG_INF; nd.C = 0;
    }

    void _upd(int i, int tl, int tr, int ql, int qr, ll a, ll b, ll c) {
        if (qr < tl || ql > tr) return;
        if (ql <= tl && qr >= tr) { _apply(i, a, b, c); return; }
        _push(i, tl, tr);
        int tm = (tl + tr) / 2;
        _upd(2 * i, tl, tm, ql, qr, a, b, c);
        _upd(2 * i + 1, tm + 1, tr, ql, qr, a, b, c);
        _pull(i);
    }

    void rangeChmin(int l, int r, ll x) { if (l <= r && n) _upd(1, 0, n - 1, l, r, x, NEG_INF, 0); }
    void rangeChmax(int l, int r, ll x) { if (l <= r && n) _upd(1, 0, n - 1, l, r, POS_INF, x, 0); }
    void rangeAdd(int l, int r, ll x)   { if (l <= r && n) _upd(1, 0, n - 1, l, r, POS_INF, NEG_INF, x); }
    void rangeAssign(int l, int r, ll x){ if (l <= r && n) _upd(1, 0, n - 1, l, r, x, x, 0); }
    void pointSet(int p, ll x) { rangeAssign(p, p, x); }

    ll _qmin(int i, int tl, int tr, int ql, int qr) {
        if (qr < tl || ql > tr) return POS_INF;
        if (ql <= tl && qr >= tr) return t[i].mn;
        _push(i, tl, tr);
        int tm = (tl + tr) / 2;
        return min(_qmin(2 * i, tl, tm, ql, qr), _qmin(2 * i + 1, tm + 1, tr, ql, qr));
    }
    ll rangeMin(int l, int r) { return (l > r || !n) ? POS_INF : _qmin(1, 0, n - 1, l, r); }

    ll _qmax(int i, int tl, int tr, int ql, int qr) {
        if (qr < tl || ql > tr) return NEG_INF;
        if (ql <= tl && qr >= tr) return t[i].mx;
        _push(i, tl, tr);
        int tm = (tl + tr) / 2;
        return max(_qmax(2 * i, tl, tm, ql, qr), _qmax(2 * i + 1, tm + 1, tr, ql, qr));
    }
    ll rangeMax(int l, int r) { return (l > r || !n) ? NEG_INF : _qmax(1, 0, n - 1, l, r); }
    ll pointGet(int p) { return rangeMin(p, p); }
};