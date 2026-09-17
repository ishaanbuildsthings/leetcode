// TEMPLATE BY https://github.com/agrawalishaan
//
// ========================
// COMPLEXITIES
//
// O(n) build
// BeatsGcd_PERFORMANT seg(arr);
//
// AMORTIZED O(logN):     rangeChmin(l, r, x)    -- a[i] = min(a[i], x)
// AMORTIZED O(logN):     rangeChmax(l, r, x)    -- a[i] = max(a[i], x)
// AMORTIZED O(logN):     rangeAssign(l, r, x)   -- a[i] = x
// AMORTIZED O(logN):     pointSet(pos, newVal)  -- OVERWRITE, may RAISE the value
// AMORTIZED O(log^2 N):  rangeAdd(l, r, x)      -- a[i] += x
//
// O(logN):          rangeSum(l, r)
// O(logN):          rangeMin(l, r)
// O(logN):          rangeMax(l, r)
// O(logN):          pointGet(pos)
// O(logN * logC):   rangeGcd(l, r)      -- the extra logC is the Euclid calls
// O(n) space
//
// IF YOU NEVER CALL rangeAdd the whole structure is O((n + q) logN); with it, O((n + q) log^2 N),
// and that log^2 is proven tight (Tony2_CF, Dec 2025, codeforces.com/blog/entry/149516).
//
// HOW THE GCD WORKS -- the point is that DIFFERENCES ARE INVARIANT UNDER A UNIFORM ADD.
// gcd of a set equals gcd(any one element, all the pairwise differences). So split the node's values
// into three groups: the copies of the max, the copies of the min, and everything strictly between,
// which we call the INTERIOR. chmin only ever moves the max group and chmax only ever moves the min
// group, so the interior values are only ever SHIFTED, all by the same amount -- which means their
// pairwise differences never change at all. diffGcd holds a spanning tree of those differences and
// _applyAdd does not touch it.
//
// At query time we rebuild the full gcd from three bridges:
//     diffGcd                 the interior, already joined up
//     gcd with (mx2 - mx)     bridges the max group in, since mx2 is the largest interior value
//     gcd with (mn2 - mn)     bridges the min group in
//     gcd with mx             anchors the whole thing on an actual element rather than a difference
// _pull is where the bookkeeping lives: a value that was a child's max or min may be INTERIOR in the
// parent, so it has to be folded into the parent's spanning tree, and the two children's trees have
// to be joined to each other. That is what the hasL / hasR / any dance is doing.
//
// WHY THE TAGS ARE JUST ONE ADD PLUS mx AND mn:
// any sequence of add / chmin / chmax on a whole node composes to min(a, max(b, x + c)), so one add
// tag and two clamp bounds is the complete closed form -- there is no need for per-group add tags.
// And the two clamp bounds are already stored: a is the node's mx and b is its mn, because for every
// value actually in the node, clamping to [mn, mx] gives the same answer as clamping to [b, a].
// There is no assign tag either -- an assign leaves mn == mx, and mn == mx already means "every value
// here is this number", so _push just forwards that to both children as an assign.
//
// STILL NEEDS THE CROSS-INTERACTION GLUE (only fires when the two sides meet, so stress test it):
//   - a chmin whose value lands at or below mn collapses the node, so it becomes an assign
//   - a chmin on a node with EXACTLY TWO distinct values has mn2 == mx, so the second-min is the
//     thing being clamped and mn2 must follow the max down
//   - and the mirror of both for chmax
//
// Verified against the official sample of "Minimize, Add, GCD and Their Friends" and against brute
// force. At n = q = 200000 the C++ version runs in about 0.24s.
//
// Values are assumed POSITIVE (the source problem gives 1 <= a[i] <= 1e9 and x >= 1). gcd is taken
// on absolute values so negatives will not crash, but they are untested.
//
// ========================
//

#include <bits/stdc++.h>
using namespace std;
using ll = long long;

static const ll NEG_INF = LLONG_MIN / 4;
static const ll POS_INF = LLONG_MAX / 4;

static ll gcdll(ll a, ll b) {
    if (a < 0) a = -a;
    if (b < 0) b = -b;
    while (a) { b %= a; ll t = a; a = b; b = t; }
    return b;
}

struct BeatsGcd_PERFORMANT {
    struct Node {
        ll mx, mx2, cntMx;
        ll mn, mn2, cntMn;
        ll tot;
        ll diffGcd;   // gcd of differences among INTERIOR values (neither mx nor mn)
        ll addTag;
    };
    int n;
    vector<Node> t;

    explicit BeatsGcd_PERFORMANT(const vector<ll>& arr) {
        n = (int)arr.size();
        t.assign(4 * max(1, n), Node{});
        if (n) _build(1, 0, n - 1, arr);
    }

    void _build(int i, int tl, int tr, const vector<ll>& arr) {
        if (tl == tr) {
            ll v = arr[tl];
            t[i] = Node{v, NEG_INF, 1, v, POS_INF, 1, v, 0, 0};
            return;
        }
        int tm = (tl + tr) / 2;
        _build(2 * i, tl, tm, arr);
        _build(2 * i + 1, tm + 1, tr, arr);
        _pull(i);
    }

    void _pull(int i) {
        Node& nd = t[i];
        const Node& a = t[2 * i];
        const Node& b = t[2 * i + 1];
        nd.tot = a.tot + b.tot;
        if (a.mx > b.mx)      { nd.mx = a.mx; nd.cntMx = a.cntMx;           nd.mx2 = max(a.mx2, b.mx); }
        else if (a.mx < b.mx) { nd.mx = b.mx; nd.cntMx = b.cntMx;           nd.mx2 = max(b.mx2, a.mx); }
        else                  { nd.mx = a.mx; nd.cntMx = a.cntMx + b.cntMx; nd.mx2 = max(a.mx2, b.mx2); }
        if (a.mn < b.mn)      { nd.mn = a.mn; nd.cntMn = a.cntMn;           nd.mn2 = min(a.mn2, b.mn); }
        else if (a.mn > b.mn) { nd.mn = b.mn; nd.cntMn = b.cntMn;           nd.mn2 = min(b.mn2, a.mn); }
        else                  { nd.mn = a.mn; nd.cntMn = a.cntMn + b.cntMn; nd.mn2 = min(a.mn2, b.mn2); }

        ll g = gcdll(a.diffGcd, b.diffGcd);
        // a.mx2 is an interior value of the child unless the child has <= 2 distinct values
        bool hasL = (a.mx2 != NEG_INF && a.mx2 != a.mn);
        bool hasR = (b.mx2 != NEG_INF && b.mx2 != b.mn);
        if (hasL && hasR) g = gcdll(g, a.mx2 - b.mx2);   // join the two spanning trees
        bool haveAny = false;
        ll any = 0;
        if (hasL)      { any = a.mx2; haveAny = true; }
        else if (hasR) { any = b.mx2; haveAny = true; }
        // values that were boundary in a child but are interior in the parent join the tree
        ll cand[4] = {a.mn, a.mx, b.mn, b.mx};
        for (ll val : cand) {
            if (val != nd.mn && val != nd.mx) {
                if (haveAny) g = gcdll(g, val - any);
                else { any = val; haveAny = true; }
            }
        }
        nd.diffGcd = g;
        nd.addTag = 0;
    }

    void _applyAssign(int i, ll sz, ll v) {
        t[i] = Node{v, NEG_INF, sz, v, POS_INF, sz, v * sz, 0, 0};
    }

    void _applyAdd(int i, ll sz, ll v) {
        Node& nd = t[i];
        if (nd.mn == nd.mx) { _applyAssign(i, sz, nd.mx + v); return; }
        nd.mx += v; if (nd.mx2 != NEG_INF) nd.mx2 += v;
        nd.mn += v; if (nd.mn2 != POS_INF) nd.mn2 += v;
        nd.tot += sz * v;
        nd.addTag += v;
        // diffGcd is untouched: a uniform shift does not change any difference
    }

    // requires v > mx2
    void _applyChmin(int i, ll sz, ll v) {
        Node& nd = t[i];
        if (nd.mn >= v) { _applyAssign(i, sz, v); return; }
        if (nd.mx > v) {
            if (nd.mn2 == nd.mx) nd.mn2 = v;
            nd.tot -= (nd.mx - v) * nd.cntMx;
            nd.mx = v;
        }
    }

    // requires v < mn2
    void _applyChmax(int i, ll sz, ll v) {
        Node& nd = t[i];
        if (nd.mx <= v) { _applyAssign(i, sz, v); return; }
        if (nd.mn < v) {
            if (nd.mx2 == nd.mn) nd.mx2 = v;
            nd.tot += (v - nd.mn) * nd.cntMn;
            nd.mn = v;
        }
    }

    void _push(int i, int tl, int tr) {
        if (tl == tr) return;
        int tm = (tl + tr) / 2;
        ll lsz = tm - tl + 1, rsz = tr - tm;
        int l = 2 * i, r = l + 1;
        Node& nd = t[i];
        if (nd.mn == nd.mx) {
            _applyAssign(l, lsz, nd.mx);
            _applyAssign(r, rsz, nd.mx);
            return;
        }
        if (nd.addTag) {
            _applyAdd(l, lsz, nd.addTag);
            _applyAdd(r, rsz, nd.addTag);
            nd.addTag = 0;
        }
        _applyChmin(l, lsz, nd.mx); _applyChmin(r, rsz, nd.mx);
        _applyChmax(l, lsz, nd.mn); _applyChmax(r, rsz, nd.mn);
    }

    void _chmin(int i, int tl, int tr, int ql, int qr, ll x) {
        if (qr < tl || ql > tr || x >= t[i].mx) return;
        if (ql <= tl && qr >= tr && x > t[i].mx2) { _applyChmin(i, tr - tl + 1, x); return; }
        _push(i, tl, tr);
        int tm = (tl + tr) / 2;
        _chmin(2 * i, tl, tm, ql, qr, x);
        _chmin(2 * i + 1, tm + 1, tr, ql, qr, x);
        _pull(i);
    }
    void rangeChmin(int l, int r, ll x) { if (l <= r && n) _chmin(1, 0, n - 1, l, r, x); }

    void _chmax(int i, int tl, int tr, int ql, int qr, ll x) {
        if (qr < tl || ql > tr || x <= t[i].mn) return;
        if (ql <= tl && qr >= tr && x < t[i].mn2) { _applyChmax(i, tr - tl + 1, x); return; }
        _push(i, tl, tr);
        int tm = (tl + tr) / 2;
        _chmax(2 * i, tl, tm, ql, qr, x);
        _chmax(2 * i + 1, tm + 1, tr, ql, qr, x);
        _pull(i);
    }
    void rangeChmax(int l, int r, ll x) { if (l <= r && n) _chmax(1, 0, n - 1, l, r, x); }

    void _add(int i, int tl, int tr, int ql, int qr, ll v) {
        if (qr < tl || ql > tr) return;
        if (ql <= tl && qr >= tr) { _applyAdd(i, tr - tl + 1, v); return; }
        _push(i, tl, tr);
        int tm = (tl + tr) / 2;
        _add(2 * i, tl, tm, ql, qr, v);
        _add(2 * i + 1, tm + 1, tr, ql, qr, v);
        _pull(i);
    }
    void rangeAdd(int l, int r, ll v) { if (l <= r && n) _add(1, 0, n - 1, l, r, v); }

    void _assign(int i, int tl, int tr, int ql, int qr, ll v) {
        if (qr < tl || ql > tr) return;
        if (ql <= tl && qr >= tr) { _applyAssign(i, tr - tl + 1, v); return; }
        _push(i, tl, tr);
        int tm = (tl + tr) / 2;
        _assign(2 * i, tl, tm, ql, qr, v);
        _assign(2 * i + 1, tm + 1, tr, ql, qr, v);
        _pull(i);
    }
    void rangeAssign(int l, int r, ll v) { if (l <= r && n) _assign(1, 0, n - 1, l, r, v); }
    void pointSet(int p, ll v) { rangeAssign(p, p, v); }

    ll _sum(int i, int tl, int tr, int ql, int qr) {
        if (qr < tl || ql > tr) return 0;
        if (ql <= tl && qr >= tr) return t[i].tot;
        _push(i, tl, tr);
        int tm = (tl + tr) / 2;
        return _sum(2 * i, tl, tm, ql, qr) + _sum(2 * i + 1, tm + 1, tr, ql, qr);
    }
    ll rangeSum(int l, int r) { return (l > r || !n) ? 0 : _sum(1, 0, n - 1, l, r); }

    ll _qmax(int i, int tl, int tr, int ql, int qr) {
        if (qr < tl || ql > tr) return NEG_INF;
        if (ql <= tl && qr >= tr) return t[i].mx;
        _push(i, tl, tr);
        int tm = (tl + tr) / 2;
        return max(_qmax(2 * i, tl, tm, ql, qr), _qmax(2 * i + 1, tm + 1, tr, ql, qr));
    }
    ll rangeMax(int l, int r) { return (l > r || !n) ? NEG_INF : _qmax(1, 0, n - 1, l, r); }

    ll _qmin(int i, int tl, int tr, int ql, int qr) {
        if (qr < tl || ql > tr) return POS_INF;
        if (ql <= tl && qr >= tr) return t[i].mn;
        _push(i, tl, tr);
        int tm = (tl + tr) / 2;
        return min(_qmin(2 * i, tl, tm, ql, qr), _qmin(2 * i + 1, tm + 1, tr, ql, qr));
    }
    ll rangeMin(int l, int r) { return (l > r || !n) ? POS_INF : _qmin(1, 0, n - 1, l, r); }
    ll pointGet(int p) { return rangeMax(p, p); }

    ll _nodeGcd(int i) {
        const Node& nd = t[i];
        ll ans = nd.diffGcd;
        if (nd.mx2 != NEG_INF) ans = gcdll(ans, nd.mx2 - nd.mx);
        if (nd.mn2 != POS_INF) ans = gcdll(ans, nd.mn2 - nd.mn);
        return gcdll(ans, nd.mx);
    }

    ll _qgcd(int i, int tl, int tr, int ql, int qr) {
        if (qr < tl || ql > tr) return 0;
        if (ql <= tl && qr >= tr) return _nodeGcd(i);
        _push(i, tl, tr);
        int tm = (tl + tr) / 2;
        return gcdll(_qgcd(2 * i, tl, tm, ql, qr), _qgcd(2 * i + 1, tm + 1, tr, ql, qr));
    }
    ll rangeGcd(int l, int r) { return (l > r || !n) ? 0 : _qgcd(1, 0, n - 1, l, r); }
};