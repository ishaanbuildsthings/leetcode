// TEMPLATE BY https://github.com/agrawalishaan
//
// ========================
// COMPLEXITIES
//
// O(n) build
// AffineSeg_PERFORMANT seg(arr);   // arr is vector<ll>
//
// O(logN):  rangeAdd(l, r, x)         -- a[i] += x
// O(logN):  rangeMult(l, r, m)        -- a[i] *= m
// O(logN):  rangeAssign(l, r, x)      -- a[i] = x
// O(logN):  rangeAffine(l, r, m, x)   -- a[i] = a[i]*m + x, the general one
// O(logN):  pointSet(pos, newVal)     -- OVERWRITE
// O(logN):  rangeSum(l, r)
// O(logN):  pointGet(pos)
// O(n) space
//
// NOT amortized, plain lazy propagation, worst case logN per op. Everything is mod MOD
// (1e9+7 by default, change the constant). Negative inputs are normalized on the way in.
//
// ========================
//
/**
WHY ONE (mult, add) PAIR IS ENOUGH

Every one of these updates is an AFFINE map v -> v*m + x, and affine maps compose into affine
maps, so a whole history of them collapses into two numbers. Applying f(v) = m1*v + a1 and THEN
g(v) = m2*v + a2:

    g(f(v)) = m2*(m1*v + a1) + a2 = (m1*m2)*v + (a1*m2 + a2)

so  newMult = m1*m2  and  newAdd = a1*m2 + a2.

THE ONLY LINE THAT IS EASY TO GET WRONG IS THAT SECOND ONE. The OLD add has to be scaled by the
NEW mult. Writing newAdd = a1 + a2 looks right and passes small tests where no multiply has
landed yet, then silently gives wrong answers the moment one has.

MULTIPLY-BEFORE-ADD IS THE FORM THAT CLOSES, and that is not arbitrary. Keep the other form,
(v + b)*m, and a later add d needs (v + b)*m + d -- there is no b' making (v + b')*m equal that
without dividing. Multiply-first survives both operations, so that is the canonical form.

Every update is a special case, which is why there is only one tag type and one apply function:
    add x     -> (m, a) = (1, x)
    mult m    -> (m, a) = (m, 0)
    assign x  -> (m, a) = (0, x)      multiply by zero, then add -- no separate assign tag
Note that assign being free depends on working mod a prime; without the mod you would still be
fine here since 0 is a legal multiplier, but the inverse does not exist, so nothing that needs to
UNDO a tag would work.

SUM SURVIVES, MIN AND MAX DO NOT. A node's sum transforms as tot*m + a*width, which needs only
the width. min and max are hopeless under multiply because the mod wraps, so ordering is
destroyed -- do not add them to this file.

_push has to run before ANY descent, including in rangeSum and pointSet, or pending tags never
reach the leaves. pointSet also has to reset the leaf's own tag, otherwise the slot inherits
every operation that happened before it was written.
*/

// ========================


#include <bits/stdc++.h>
using namespace std;
using ll = long long;

struct AffineSeg_PERFORMANT {
    static const ll MOD = 1000000007;

    struct Node { ll tot, mult, add; };
    int n;
    vector<Node> t;

    explicit AffineSeg_PERFORMANT(const vector<ll>& arr) {
        n = (int)arr.size();
        t.assign(4 * max(1, n), Node{0, 1, 0});
        if (n) _build(1, 0, n - 1, arr);
    }

    void _build(int i, int tl, int tr, const vector<ll>& arr) {
        t[i].mult = 1; t[i].add = 0;
        if (tl == tr) { t[i].tot = ((arr[tl] % MOD) + MOD) % MOD; return; }
        int tm = (tl + tr) / 2;
        _build(2 * i, tl, tm, arr);
        _build(2 * i + 1, tm + 1, tr, arr);
        _pull(i);
    }

    void _pull(int i) {
        t[i].tot = (t[2 * i].tot + t[2 * i + 1].tot) % MOD;
        t[i].mult = 1; t[i].add = 0;
    }

    // v -> v*m + a on every slot of this node. Composition is (m1*m2, a1*m2 + a2):
    // the OLD add has to be scaled by the NEW mult, which is the step people drop.
    void _applyTag(int i, ll m, ll a, ll width) {
        Node& nd = t[i];
        nd.tot = (nd.tot * m + a * width) % MOD;
        nd.mult = nd.mult * m % MOD;
        nd.add = (nd.add * m + a) % MOD;
    }

    void _push(int i, int tl, int tr) {
        Node& nd = t[i];
        if (nd.mult == 1 && nd.add == 0) return;
        int tm = (tl + tr) / 2;
        _applyTag(2 * i, nd.mult, nd.add, tm - tl + 1);
        _applyTag(2 * i + 1, nd.mult, nd.add, tr - tm);
        nd.mult = 1; nd.add = 0;
    }

    void _affine(int i, int tl, int tr, int ql, int qr, ll m, ll a) {
        if (qr < tl || ql > tr) return;
        if (ql <= tl && qr >= tr) { _applyTag(i, m, a, tr - tl + 1); return; }
        _push(i, tl, tr);
        int tm = (tl + tr) / 2;
        _affine(2 * i, tl, tm, ql, qr, m, a);
        _affine(2 * i + 1, tm + 1, tr, ql, qr, m, a);
        _pull(i);
    }

    ll _sum(int i, int tl, int tr, int ql, int qr) {
        if (qr < tl || ql > tr) return 0;
        if (ql <= tl && qr >= tr) return t[i].tot;
        _push(i, tl, tr);
        int tm = (tl + tr) / 2;
        return (_sum(2 * i, tl, tm, ql, qr) + _sum(2 * i + 1, tm + 1, tr, ql, qr)) % MOD;
    }

    void _set(int i, int tl, int tr, int p, ll v) {
        if (tl == tr) { t[i] = Node{v, 1, 0}; return; }
        _push(i, tl, tr);
        int tm = (tl + tr) / 2;
        if (p <= tm) _set(2 * i, tl, tm, p, v); else _set(2 * i + 1, tm + 1, tr, p, v);
        _pull(i);
    }

    //////////////// PUBLIC METHODS START HERE ////////////////

    // O(log n) -- a[i] = a[i]*m + x for every i in l...r. every other update is this one
    void rangeAffine(int l, int r, ll m, ll x) {
        if (l > r || !n) return;
        _affine(1, 0, n - 1, l, r, ((m % MOD) + MOD) % MOD, ((x % MOD) + MOD) % MOD);
    }
    // O(log n) -- a[i] += x
    void rangeAdd(int l, int r, ll x) { rangeAffine(l, r, 1, x); }
    // O(log n) -- a[i] *= m
    void rangeMult(int l, int r, ll m) { rangeAffine(l, r, m, 0); }
    // O(log n) -- a[i] = x. multiplying by 0 then adding x, no separate tag needed
    void rangeAssign(int l, int r, ll x) { rangeAffine(l, r, 0, x); }

    // O(log n) -- sum of l...r, mod MOD
    ll rangeSum(int l, int r) { return (l > r || !n) ? 0 : _sum(1, 0, n - 1, l, r); }

    // O(log n) -- a[pos] = v, an OVERWRITE that discards every pending tag on that slot
    void pointSet(int pos, ll v) { if (n) _set(1, 0, n - 1, pos, ((v % MOD) + MOD) % MOD); }
    // O(log n)
    ll pointGet(int pos) { return rangeSum(pos, pos); }
};