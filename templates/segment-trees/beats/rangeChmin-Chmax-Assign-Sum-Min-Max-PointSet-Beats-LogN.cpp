// TEMPLATE BY https://github.com/agrawalishaan
//
// ========================
// COMPLEXITIES
//
// O(n) build
// BeatsChminChmaxNoAdd_PERFORMANT seg(arr);
//
// AMORTIZED O(logN):  rangeChmin(l, r, x)    -- a[i] = min(a[i], x)
// AMORTIZED O(logN):  rangeChmax(l, r, x)    -- a[i] = max(a[i], x)
// AMORTIZED O(logN):  rangeAssign(l, r, x)   -- a[i] = x
// AMORTIZED O(logN):  pointSet(pos, newVal)  -- OVERWRITE, may RAISE the value
//
// O(logN):  rangeSum(l, r)
// O(logN):  rangeMin(l, r)
// O(logN):  rangeMax(l, r)
// O(logN):  pointGet(pos)
// O(n) space
//
// Whole structure is O((n + q) logN). THERE IS NO rangeAdd HERE ON PURPOSE -- adding it forces
// O((n + q) log^2 N), and that log^2 is proven tight (Tony2_CF, Dec 2025,
// codeforces.com/blog/entry/149516). If you need add, take the Chmin-Chmax-Add variant instead;
// measured at n = q = 300000 it runs about 1.2x slower than this file on an add-free workload,
// because its node is 104 bytes against 56 here.
//
// THE NODE CARRIES NO TAG FIELDS AT ALL. mx doubles as the pending chmin tag and mn as the pending
// chmax tag -- if a child's mx is above my mx, that IS a pending chmin, and re-pushing a value the
// child already satisfies is a no-op, so nothing needs clearing and there is no sentinel to get
// wrong. There is no assign tag either: an assign leaves the node with mn == mx, and mn == mx
// already means "every value in my interval is this number", so _push just forwards that to both
// children as an assign.
//
// NOT A PLAIN MERGE OF A CHMIN TREE AND A CHMAX TREE. Holding both sides in one node needs glue
// neither one-sided version has, and it only fires when the two sides meet -- which random tests
// hit rarely, so stress test it if you touch it:
//   - a chmin on a UNIFORM node (mn == mx) moves the min too, so mn must follow mx down
//   - a chmin on a node with EXACTLY TWO distinct values has mn2 == mx, so the second-min is the
//     thing being clamped and mn2 must follow
//   - and the mirror of both for chmax
//
// Values may be negative.
//
// ========================
//
/**
HOW DO POTENTIALS WORK? (segment tree beats)

Think about the "potential" of the entire segment tree. Each of the N values appears in logN
nodes, so the tree captures N logN element-slots. A node's potential is the number of DISTINCT
values in its interval, so the potential across the whole tree is at most N logN.

chmin / chmax / assign can never RAISE this. They apply the SAME function to every element of a
covered node, and a function can merge two distinct values into one but can never split one value
into two. That is the whole requirement -- it is not about monotonicity. (Range add is the one
that breaks it, because at a node STRADDLING the range boundary half the elements get shifted and
half do not, so two different functions are applied and equal values come apart. That is why this
file does not have one.)

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
  case 1, x >= mx       -- nothing here is above x, return immediately (this falls into case 2)
  case 2, mx2 < x < mx  -- ONLY the copies of the max move, and they all move to x. We know how
                           many there are (cntMx) so we can patch the sum in O(1) and return.
                           cntMx does NOT change: everything below the max is at most mx2, which
                           is strictly under x, so the tie set is the same set. Nothing got glued,
                           so NO potential was spent -- which is exactly why we are not allowed to
                           descend here, and exactly why we need a tag: we fixed this node and
                           left its children stale.
  case 3, x <= mx2      -- mx and mx2 both land on x, so two distinct values get GLUED together
                           and this node's potential drops by at least one, paying for the visit.
                           We recurse to the children.

So we can only descend when potential actually drops. (Contrast rangeMod, where the prune test and
the potential test are the SAME test -- max >= mod always means a real halving is waiting below --
so you can always descend and never need a lazy tag at all.)

WHY A PUSHED TAG IS ALWAYS LEGAL:
_applyChmin has a precondition, x > mx2, that nothing in the code checks. It holds for two reasons
and they are worth writing down. Case 2 above is the ONLY place a tag is born, and it tests the
condition directly. And a parent's mx is at least its child's mx, which is strictly above the
child's mx2, so a tag that cleared the parent's bar clears the child's too. Mirror for chmax.

ASSIGN / POINT SET:
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

struct BeatsChminChmaxNoAdd_PERFORMANT {
    struct Node {
        ll mx, mx2, cntMx;
        ll mn, mn2, cntMn;
        ll tot;
    };
    int n;
    vector<Node> t;

    explicit BeatsChminChmaxNoAdd_PERFORMANT(const vector<ll>& arr) {
        n = (int)arr.size();
        t.assign(4 * max(1, n), Node{});
        if (n) _build(1, 0, n - 1, arr);
    }

    void _build(int i, int tl, int tr, const vector<ll>& arr) {
        if (tl == tr) {
            ll v = arr[tl];
            t[i] = Node{v, NEG_INF, 1, v, POS_INF, 1, v};
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
    }

    // requires x > mx2
    void _applyChmin(int i, ll x) {
        Node& nd = t[i];
        if (x >= nd.mx) return;
        nd.tot -= (nd.mx - x) * nd.cntMx;
        if (nd.mn == nd.mx) nd.mn = x;            // uniform node
        else if (nd.mn2 == nd.mx) nd.mn2 = x;     // exactly two distinct values
        nd.mx = x;
    }

    // requires x < mn2
    void _applyChmax(int i, ll x) {
        Node& nd = t[i];
        if (x <= nd.mn) return;
        nd.tot += (x - nd.mn) * nd.cntMn;
        if (nd.mx == nd.mn) nd.mx = x;
        else if (nd.mx2 == nd.mn) nd.mx2 = x;
        nd.mn = x;
    }

    void _applyAssign(int i, ll v, ll sz) {
        t[i] = Node{v, NEG_INF, sz, v, POS_INF, sz, v * sz};
    }

    void _push(int i, int tl, int tr) {
        if (tl == tr) return;
        int tm = (tl + tr) / 2;
        int l = 2 * i, r = l + 1;
        Node& nd = t[i];
        if (nd.mn == nd.mx) {                      // uniform: hand both children an assign
            _applyAssign(l, nd.mx, tm - tl + 1);
            _applyAssign(r, nd.mx, tr - tm);
            return;
        }
        _applyChmin(l, nd.mx); _applyChmin(r, nd.mx);
        _applyChmax(l, nd.mn); _applyChmax(r, nd.mn);
    }

    void _chmin(int i, int tl, int tr, int ql, int qr, ll x) {
        if (qr < tl || ql > tr || x >= t[i].mx) return;
        if (ql <= tl && qr >= tr && x > t[i].mx2) { _applyChmin(i, x); return; }
        _push(i, tl, tr);
        int tm = (tl + tr) / 2;
        _chmin(2 * i, tl, tm, ql, qr, x);
        _chmin(2 * i + 1, tm + 1, tr, ql, qr, x);
        _pull(i);
    }
    void rangeChmin(int l, int r, ll x) { if (l <= r && n) _chmin(1, 0, n - 1, l, r, x); }

    void _chmax(int i, int tl, int tr, int ql, int qr, ll x) {
        if (qr < tl || ql > tr || x <= t[i].mn) return;
        if (ql <= tl && qr >= tr && x < t[i].mn2) { _applyChmax(i, x); return; }
        _push(i, tl, tr);
        int tm = (tl + tr) / 2;
        _chmax(2 * i, tl, tm, ql, qr, x);
        _chmax(2 * i + 1, tm + 1, tr, ql, qr, x);
        _pull(i);
    }
    void rangeChmax(int l, int r, ll x) { if (l <= r && n) _chmax(1, 0, n - 1, l, r, x); }

    void _assign(int i, int tl, int tr, int ql, int qr, ll v) {
        if (qr < tl || ql > tr) return;
        if (ql <= tl && qr >= tr) { _applyAssign(i, v, tr - tl + 1); return; }
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
};