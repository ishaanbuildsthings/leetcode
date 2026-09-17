// TEMPLATE BY https://github.com/agrawalishaan
//
// ========================
// COMPLEXITIES
//
// O(n) build
// ShrinkSeg_PERFORMANT seg(arr);
//
// C = largest value in the array
// AMORTIZED O(logN * logC):       rangeMod(l, r, x)      -- a[i] %= x
// AMORTIZED O(logN * logC):       rangeDiv(l, r, x)      -- a[i] //= x, floor, needs x >= 2
// AMORTIZED O(logN * log(logC)):  rangeSqrt(l, r)        -- a[i] = floor(sqrt(a[i]))
// AMORTIZED O(logN):              rangeAssign(l, r, x)   -- a[i] = x
// AMORTIZED O(logN):              pointSet(pos, newVal)  -- OVERWRITE, may RAISE the value
//
// O(logN):  rangeSum(l, r)
// O(logN):  rangeMin(l, r)
// O(logN):  rangeMax(l, r)
// O(logN):  pointGet(pos)
// O(n) space
//
// Values must be NON-NEGATIVE. C++ % truncates toward zero and Python // floors toward negative
// infinity, so negatives misbehave in both, differently -- and the max-pruning hides it, because a
// subtree whose max is negative gets skipped entirely.
//
// In C++ the sum is long long, so you need n * maxValue < 9.2e18. Python ints cannot overflow.
//
// ========================
//
/**
HOW DO POTENTIALS WORK?

When we do A%B with A>=B, A always falls by at least half. If B is < half of A the result is under
B so obviously under half of A; if B is bigger than half of A then only one copy of B fits, so what
is left over is A - B which is also under half. Div and sqrt shrink too, sqrt fastest of all: if an
element still has X halvings left in it, mod or div knocks X down by one, but sqrt HALVES X, so one
element can only be sqrt'd log(logC) times before it reaches 1.

WITHOUT ASSIGN the potential is simple. Each of the N values appears in logN nodes, so the tree
captures N logN element-slots, and each value can be halved at most logC times, so the whole tree
holds N logN logC. Every fully covered node we descend into has a max at or above the cutoff, which
means a real shrink is waiting at some leaf below it, so no descent is ever wasted.

ASSIGN LOOKS LIKE IT SHOULD DESTROY THAT, AND IT WOULD, NAIVELY. Assigning a fresh value to a range
of length L hands L elements a full logC of halvings back. Q of those refill Q*N*logC, which is
worse than just walking the range every time. This is the same failure mode range-add has in the
chmin beats templates.

WHAT RESCUES IT IS THAT AN ASSIGNED NODE IS UNIFORM. If every value under a node is the same
number, then mod / div / sqrt applied to the whole node is ONE operation, not L of them -- the new
value stands for the entire subtree and we never descend into it. So the accounting stops being per
ELEMENT and becomes per RUN of equal values:
  - the array starts with at most N runs
  - each assign destroys every run inside its range and creates at most 3 (the new one, plus a
    leftover at each edge)
  - a shrink applies one function to everything it touches, and a function can merge runs but never
    split one, except at the two range edges
so across the whole run there are at most N + O(Q) runs ever, each holding logC of shrinking, and
each one costs logN to reach. That gives O((N + Q) logN logC). This is the Chtholly / ODT argument
bolted onto the beats one.

THERE IS NO ASSIGN TAG FIELD. mn == mx already means "every value in my interval is this number",
which is exactly what an assign leaves behind, so _push just forwards that to both children as an
assign. Nothing to clear, no sentinel to get wrong.

THE COST OF ADDING ASSIGN is that this template is no longer lazy-propagation-free. The old
mod/div/sqrt-only version never summarized anything at an internal node, so nothing was ever stale
and no push existed. Now every traversal that descends must _push first.

THE PRUNE CUTOFFS DIFFER BECAUSE MOD IS SELF-LIMITING AND THE OTHERS ARE NOT. After a % x the
result is strictly below x, which is exactly the thing being tested, so that leaf removes itself
from future descents. Sqrt and div shrink a value but never push it out of range of the test, so 1
would be sqrt'd forever and 0 would be divided forever. Hence cutoff 2 for sqrt and 1 for div.
*/

// ========================


#include <bits/stdc++.h>
using namespace std;
using ll = long long;

template <typename T>
struct ShrinkSeg_PERFORMANT {
    using SumT = long long;
    struct Node { T mx, mn; SumT tot; };
    int n;
    vector<Node> tree;

    explicit ShrinkSeg_PERFORMANT(const vector<T>& arr) {
        n = (int)arr.size();
        tree.resize(4 * max(1, n));
        if (n) _build(1, 0, n - 1, arr);
    }

    Node _agg(const Node& a, const Node& b) {
        return Node{max(a.mx, b.mx), min(a.mn, b.mn), a.tot + b.tot};
    }

    void _build(int i, int tl, int tr, const vector<T>& arr) {
        if (tl == tr) { tree[i] = Node{arr[tl], arr[tl], (SumT)arr[tl]}; return; }
        int tm = (tl + tr) / 2;
        _build(2 * i, tl, tm, arr);
        _build(2 * i + 1, tm + 1, tr, arr);
        tree[i] = _agg(tree[2 * i], tree[2 * i + 1]);
    }

    void _applyAssign(int i, ll sz, T v) { tree[i] = Node{v, v, (SumT)v * sz}; }

    // mn == mx IS the assign tag: a uniform node means every value below it is that number
    void _push(int i, int tl, int tr) {
        if (tl == tr) return;
        if (tree[i].mn != tree[i].mx) return;
        int tm = (tl + tr) / 2;
        _applyAssign(2 * i, tm - tl + 1, tree[i].mx);
        _applyAssign(2 * i + 1, tr - tm, tree[i].mx);
    }

    static T _isqrt(T v) {
        if (v <= 0) return 0;
        T r = (T)::sqrtl((long double)v);
        while (r > 0 && r > v / r) r--;
        while ((r + 1) <= v / (r + 1)) r++;
        return r;
    }

    template <class LeafOp>
    void _rangeShrink(int i, int tl, int tr, int ql, int qr, T cutoff, LeafOp leafOp) {
        if (qr < tl || ql > tr) return;
        if (tree[i].mx < cutoff) return;
        // uniform and fully covered: one value stands for the whole subtree, O(1)
        if (ql <= tl && qr >= tr && tree[i].mn == tree[i].mx) {
            _applyAssign(i, tr - tl + 1, leafOp(tree[i].mx));
            return;
        }
        _push(i, tl, tr);
        int tm = (tl + tr) / 2;
        _rangeShrink(2 * i, tl, tm, ql, qr, cutoff, leafOp);
        _rangeShrink(2 * i + 1, tm + 1, tr, ql, qr, cutoff, leafOp);
        tree[i] = _agg(tree[2 * i], tree[2 * i + 1]);
    }

    void _assign(int i, int tl, int tr, int ql, int qr, T v) {
        if (qr < tl || ql > tr) return;
        if (ql <= tl && qr >= tr) { _applyAssign(i, tr - tl + 1, v); return; }
        _push(i, tl, tr);
        int tm = (tl + tr) / 2;
        _assign(2 * i, tl, tm, ql, qr, v);
        _assign(2 * i + 1, tm + 1, tr, ql, qr, v);
        tree[i] = _agg(tree[2 * i], tree[2 * i + 1]);
    }

    SumT _sum(int i, int tl, int tr, int ql, int qr) {
        if (qr < tl || ql > tr) return 0;
        if (ql <= tl && qr >= tr) return tree[i].tot;
        _push(i, tl, tr);
        int tm = (tl + tr) / 2;
        return _sum(2 * i, tl, tm, ql, qr) + _sum(2 * i + 1, tm + 1, tr, ql, qr);
    }

    T _qmax(int i, int tl, int tr, int ql, int qr) {
        if (qr < tl || ql > tr) return numeric_limits<T>::lowest();
        if (ql <= tl && qr >= tr) return tree[i].mx;
        _push(i, tl, tr);
        int tm = (tl + tr) / 2;
        return max(_qmax(2 * i, tl, tm, ql, qr), _qmax(2 * i + 1, tm + 1, tr, ql, qr));
    }

    T _qmin(int i, int tl, int tr, int ql, int qr) {
        if (qr < tl || ql > tr) return numeric_limits<T>::max();
        if (ql <= tl && qr >= tr) return tree[i].mn;
        _push(i, tl, tr);
        int tm = (tl + tr) / 2;
        return min(_qmin(2 * i, tl, tm, ql, qr), _qmin(2 * i + 1, tm + 1, tr, ql, qr));
    }

    void rangeMod(int l, int r, T x) {
        if (l > r || !n || x < 1) return;
        _rangeShrink(1, 0, n - 1, l, r, x, [x](T v) { return v % x; });
    }
    void rangeDiv(int l, int r, T x) {
        if (l > r || !n || x < 2) return;
        _rangeShrink(1, 0, n - 1, l, r, (T)1, [x](T v) { return v / x; });
    }
    void rangeSqrt(int l, int r) {
        if (l > r || !n) return;
        _rangeShrink(1, 0, n - 1, l, r, (T)2, [](T v) { return _isqrt(v); });
    }
    void rangeAssign(int l, int r, T v) { if (l <= r && n) _assign(1, 0, n - 1, l, r, v); }
    void pointSet(int p, T v) { rangeAssign(p, p, v); }
    SumT rangeSum(int l, int r) { return (l > r || !n) ? 0 : _sum(1, 0, n - 1, l, r); }
    T rangeMax(int l, int r) { return (l > r || !n) ? numeric_limits<T>::lowest() : _qmax(1, 0, n - 1, l, r); }
    T rangeMin(int l, int r) { return (l > r || !n) ? numeric_limits<T>::max() : _qmin(1, 0, n - 1, l, r); }
    T pointGet(int p) { return rangeMax(p, p); }
};

template <typename T>
ShrinkSeg_PERFORMANT(const std::vector<T>&) -> ShrinkSeg_PERFORMANT<T>;