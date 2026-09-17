// TEMPLATE BY https://github.com/agrawalishaan

// ========================
// COMPLEXITIES

// O(n) build
// BeatsChminChmax_PERFORMANT seg(arr);

// AMORTIZED O(logN):     rangeChmin(l, r, x)    -- a[i] = min(a[i], x)
// AMORTIZED O(logN):     rangeChmax(l, r, x)    -- a[i] = max(a[i], x)
// AMORTIZED O(logN):     rangeAssign(l, r, x)   -- a[i] = x
// AMORTIZED O(logN):     pointSet(pos, newVal)  -- OVERWRITE, may RAISE the value
// AMORTIZED O(log^2 N):  rangeAdd(l, r, x)      -- a[i] += x

// O(logN):  rangeSum(l, r)
// O(logN):  rangeMin(l, r)
// O(logN):  rangeMax(l, r)
// O(logN):  pointGet(pos)
// O(n) space

// IF YOU NEVER CALL rangeAdd, the whole structure is O((n + q) logN).
// The moment rangeAdd is in the mix EVERYTHING becomes O((n + q) log^2 N). That log^2 was proven
// TIGHT by Tony2_CF in Dec 2025 (codeforces.com/blog/entry/149516).

// This is the ONE-LOG CEILING for a segment tree: every clamp op plus assign plus every aggregate,
// minus range add. If you only need one side, the Chmin-only / Chmax-only variants have half the
// node and none of the cross-interaction code below.

// NOT A PLAIN MERGE OF THE TWO ONE-SIDED VARIANTS. Holding both sides in one node needs glue that
// neither one-sided version has:
//   - a node with ONE distinct value has mx == mn, so the max group and the min group are the SAME
//     group. _applyAdd branches on this and folds the three deltas with (vMax + vMin - vOther),
//     which collapses correctly for a plain add (v+v-v = v), for a chmin (d+0-0 = d), and for a
//     chmax (0+d-0 = d).
//   - with exactly TWO distinct values, mx2 == mn and mn2 == mx, so the second-max belongs to the
//     MIN group and the second-min belongs to the MAX group. They must move with their own group,
//     not with "other". That is what the two ternaries in _applyAdd are for.
// These only fire when the two sides meet, which random tests hit rarely -- stress test it if you
// touch this.

// Values may be negative. Sums are long long. Sentinels are LLONG_MIN/4 and LLONG_MAX/4 so they
// survive being shifted by an add tag.

// ========================
/**
HOW DO POTENTIALS WORK? (segment tree beats)

Think about the "potential" of the entire segment tree. Each of the N values appears in logN
nodes, so the tree captures N logN element-slots. A node's potential is the number of DISTINCT
values in its interval, so the potential across the whole tree is at most N logN.

chmin / chmax / assign can never RAISE this. They apply the SAME function to every element of a
covered node, and a function can merge two distinct values into one but can never split one value
into two. That is the whole requirement -- it is not about monotonicity.

There are 3 types of nodes in a seg tree:

1) STRADDLES THE QUERY RANGE (always recurses)
at most 2*logN visited per query

2) DEAD-END NODE (does not recurse)
always comes from one of the other nodes so these are free

3) FULLY COVERED NODES THAT DO RECURSE
in a normal segment tree we stop as soon as we hit one, here we do not
We must show the # of fully covered nodes we visit is bounded, as the others are bounded, then
our total visits is bounded

For a chmin with value x at a fully covered node:
  case 1, x >= mx           -- nothing here is above x, return immediately (this falls into case 2)
  case 2, mx2 < x < mx      -- ONLY the copies of the max move, and they all move to x. We know how
                               many there are (cntMx) so we can patch the sum in O(1) and return.
                               Nothing got glued, so NO potential was spent -- which is exactly why
                               we are not allowed to descend here, and exactly why we need a lazy
                               tag: we fixed this node but left its children stale.
  case 3, x <= mx2          -- mx and mx2 both land on x, so two distinct values get GLUED together
                               and this node's potential drops by at least one, paying for the visit.
                               We recurse to the children.

So we can only descend when potential actually drops. (Contrast rangeMod, where the prune test and
the potential test are the SAME test -- max >= mod always means a real halving is waiting below --
so you can always descend and never need a lazy tag at all.)

RANGE ADD IS THE ONE THAT BREAKS IT:
A node fully inside the add range has every value shifted by the same amount, so its distinct count
is unchanged. A node fully outside is untouched. But a node STRADDLING the boundary gets half its
elements shifted and half not, so two different functions are applied and equal values come apart.
Each add creates O(logN) such boundary nodes, so the potential refills and the distinct-value
argument dies. jiry_2 switches to a TAG-BASED potential there, which gives O((n + q) log^2 N).
Tony2_CF proved in Dec 2025 that this log^2 is TIGHT -- it is not a gap in the proof.

POINT SET / ASSIGN:
assign collapses a covered node to one distinct value, so it DRAINS potential; it is free.
pointSet can raise a value, injecting at most logN distinct values (one per node on its path), so
Q of them add Q logN. The bound stays O((n + q) logN).
*/

// ========================


#include <bits/stdc++.h>
using namespace std;
using ll = long long;

static const ll NEG_INF = LLONG_MIN / 4;
static const ll POS_INF = LLONG_MAX / 4;

struct Beats3c {
    struct Node {
        ll mx, mx2, cntMx;
        ll mn, mn2, cntMn;
        ll tot;
        ll sz;
        ll addMx, addMn, addOther;
        ll assignVal;
        bool hasAssign;
    };
    int n;
    vector<Node> t;

    explicit Beats3c(const vector<ll>& arr) {
        n = (int)arr.size();
        t.assign(4 * max(1, n), Node{});
        if (n) _build(1, 0, n - 1, arr);
    }

    void _build(int i, int tl, int tr, const vector<ll>& arr) {
        Node& nd = t[i];
        nd.addMx = nd.addMn = nd.addOther = 0;
        nd.hasAssign = false;
        if (tl == tr) {
            ll v = arr[tl];
            nd.mx = v; nd.mx2 = NEG_INF; nd.cntMx = 1;
            nd.mn = v; nd.mn2 = POS_INF; nd.cntMn = 1;
            nd.tot = v; nd.sz = 1;
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
        nd.sz = a.sz + b.sz;
        nd.tot = a.tot + b.tot;
        if (a.mx > b.mx) {
            nd.mx = a.mx; nd.cntMx = a.cntMx; nd.mx2 = max(a.mx2, b.mx);
        } else if (a.mx < b.mx) {
            nd.mx = b.mx; nd.cntMx = b.cntMx; nd.mx2 = max(b.mx2, a.mx);
        } else {
            nd.mx = a.mx; nd.cntMx = a.cntMx + b.cntMx; nd.mx2 = max(a.mx2, b.mx2);
        }
        if (a.mn < b.mn) {
            nd.mn = a.mn; nd.cntMn = a.cntMn; nd.mn2 = min(a.mn2, b.mn);
        } else if (a.mn > b.mn) {
            nd.mn = b.mn; nd.cntMn = b.cntMn; nd.mn2 = min(b.mn2, a.mn);
        } else {
            nd.mn = a.mn; nd.cntMn = a.cntMn + b.cntMn; nd.mn2 = min(a.mn2, b.mn2);
        }
        nd.hasAssign = false;
        nd.addMx = nd.addMn = nd.addOther = 0;
    }

    void _applyAdd(int i, ll vMax, ll vMin, ll vOther) {
        Node& nd = t[i];
        if (nd.mx == nd.mn) {
            ll d = vMax + vMin - vOther;
            nd.tot += d * nd.sz;
            nd.mx += d; nd.mn = nd.mx;
            if (nd.hasAssign) nd.assignVal = nd.mx;
            else { nd.addMx += d; nd.addMn += d; nd.addOther += d; }
            return;
        }
        nd.tot += vMax * nd.cntMx + vMin * nd.cntMn + vOther * (nd.sz - nd.cntMx - nd.cntMn);
        if (nd.mx2 != NEG_INF) nd.mx2 += (nd.mx2 == nd.mn) ? vMin : vOther;
        if (nd.mn2 != POS_INF) nd.mn2 += (nd.mn2 == nd.mx) ? vMax : vOther;
        nd.mx += vMax;
        nd.mn += vMin;
        nd.addMx += vMax; nd.addMn += vMin; nd.addOther += vOther;
    }

    void _applyAssign(int i, ll v) {
        Node& nd = t[i];
        nd.mx = v; nd.mn = v;
        nd.mx2 = NEG_INF; nd.mn2 = POS_INF;
        nd.cntMx = nd.sz; nd.cntMn = nd.sz;
        nd.tot = v * nd.sz;
        nd.addMx = nd.addMn = nd.addOther = 0;
        nd.hasAssign = true; nd.assignVal = v;
    }

    void _push(int i) {
        Node& nd = t[i];
        if (nd.sz == 1) return;
        int l = 2 * i, r = l + 1;
        if (nd.hasAssign) {
            _applyAssign(l, nd.assignVal);
            _applyAssign(r, nd.assignVal);
            nd.hasAssign = false;
            return;
        }
        ll aMx = nd.addMx, aMn = nd.addMn, aO = nd.addOther;
        if (aMx == 0 && aMn == 0 && aO == 0) return;
        ll mxc = max(t[l].mx, t[r].mx);
        ll mnc = min(t[l].mn, t[r].mn);
        _applyAdd(l, t[l].mx == mxc ? aMx : aO, t[l].mn == mnc ? aMn : aO, aO);
        _applyAdd(r, t[r].mx == mxc ? aMx : aO, t[r].mn == mnc ? aMn : aO, aO);
        nd.addMx = nd.addMn = nd.addOther = 0;
    }

    void _chmin(int i, int tl, int tr, int ql, int qr, ll x) {
        if (qr < tl || ql > tr || x >= t[i].mx) return;
        if (ql <= tl && qr >= tr && x > t[i].mx2) { _applyAdd(i, x - t[i].mx, 0, 0); return; }
        _push(i);
        int tm = (tl + tr) / 2;
        _chmin(2 * i, tl, tm, ql, qr, x);
        _chmin(2 * i + 1, tm + 1, tr, ql, qr, x);
        _pull(i);
    }
    void rangeChmin(int l, int r, ll x) { if (l <= r && n) _chmin(1, 0, n - 1, l, r, x); }

    void _chmax(int i, int tl, int tr, int ql, int qr, ll x) {
        if (qr < tl || ql > tr || x <= t[i].mn) return;
        if (ql <= tl && qr >= tr && x < t[i].mn2) { _applyAdd(i, 0, x - t[i].mn, 0); return; }
        _push(i);
        int tm = (tl + tr) / 2;
        _chmax(2 * i, tl, tm, ql, qr, x);
        _chmax(2 * i + 1, tm + 1, tr, ql, qr, x);
        _pull(i);
    }
    void rangeChmax(int l, int r, ll x) { if (l <= r && n) _chmax(1, 0, n - 1, l, r, x); }

    void _add(int i, int tl, int tr, int ql, int qr, ll v) {
        if (qr < tl || ql > tr) return;
        if (ql <= tl && qr >= tr) { _applyAdd(i, v, v, v); return; }
        _push(i);
        int tm = (tl + tr) / 2;
        _add(2 * i, tl, tm, ql, qr, v);
        _add(2 * i + 1, tm + 1, tr, ql, qr, v);
        _pull(i);
    }
    void rangeAdd(int l, int r, ll v) { if (l <= r && n) _add(1, 0, n - 1, l, r, v); }

    void _assign(int i, int tl, int tr, int ql, int qr, ll v) {
        if (qr < tl || ql > tr) return;
        if (ql <= tl && qr >= tr) { _applyAssign(i, v); return; }
        _push(i);
        int tm = (tl + tr) / 2;
        _assign(2 * i, tl, tm, ql, qr, v);
        _assign(2 * i + 1, tm + 1, tr, ql, qr, v);
        _pull(i);
    }
    void rangeAssign(int l, int r, ll v) { if (l <= r && n) _assign(1, 0, n - 1, l, r, v); }
    void pointSet(int pos, ll v) { rangeAssign(pos, pos, v); }

    ll _sum(int i, int tl, int tr, int ql, int qr) {
        if (qr < tl || ql > tr) return 0;
        if (ql <= tl && qr >= tr) return t[i].tot;
        _push(i);
        int tm = (tl + tr) / 2;
        return _sum(2 * i, tl, tm, ql, qr) + _sum(2 * i + 1, tm + 1, tr, ql, qr);
    }
    ll rangeSum(int l, int r) { return (l > r || !n) ? 0 : _sum(1, 0, n - 1, l, r); }

    ll _qmax(int i, int tl, int tr, int ql, int qr) {
        if (qr < tl || ql > tr) return NEG_INF;
        if (ql <= tl && qr >= tr) return t[i].mx;
        _push(i);
        int tm = (tl + tr) / 2;
        return max(_qmax(2 * i, tl, tm, ql, qr), _qmax(2 * i + 1, tm + 1, tr, ql, qr));
    }
    ll rangeMax(int l, int r) { return (l > r || !n) ? NEG_INF : _qmax(1, 0, n - 1, l, r); }

    ll _qmin(int i, int tl, int tr, int ql, int qr) {
        if (qr < tl || ql > tr) return POS_INF;
        if (ql <= tl && qr >= tr) return t[i].mn;
        _push(i);
        int tm = (tl + tr) / 2;
        return min(_qmin(2 * i, tl, tm, ql, qr), _qmin(2 * i + 1, tm + 1, tr, ql, qr));
    }
    ll rangeMin(int l, int r) { return (l > r || !n) ? POS_INF : _qmin(1, 0, n - 1, l, r); }

    ll pointGet(int pos) { return rangeMax(pos, pos); }
};