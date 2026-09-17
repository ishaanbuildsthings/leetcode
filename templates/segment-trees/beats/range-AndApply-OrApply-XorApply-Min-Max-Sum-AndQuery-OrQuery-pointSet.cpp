// TEMPLATE BY https://github.com/agrawalishaan
//
// ========================
// COMPLEXITIES
//
// O(n) build
// BitBeats_PERFORMANT seg(arr, 20);   // second arg is the bit width
//
// K = bit width (20 for values < 2^20)
// AMORTIZED O(logN * K):  rangeAnd(l, r, x)      -- a[i] &= x
// AMORTIZED O(logN * K):  rangeOr(l, r, x)       -- a[i] |= x
// AMORTIZED O(logN * K):  rangeXor(l, r, x)      -- a[i] ^= x
// AMORTIZED O(logN):      pointSet(pos, newVal)
//
// O(logN):  rangeMax(l, r)
// O(logN):  rangeMin(l, r)
// O(logN):  rangeSum(l, r)
// O(logN):  rangeAndQuery(l, r)    -- AND of the whole range
// O(logN):  rangeOrQuery(l, r)     -- OR of the whole range
// O(logN):  pointGet(pos)
// O(n) space
//
// Whole thing is O((n + q) * K * logN). Values must be NON-NEGATIVE and below 2^K.
//
// ========================
//
/**
HOW DO POTENTIALS WORK? (bitwise beats)

THE POTENTIAL IS PER BIT, NOT PER VALUE. This is what makes this template different from the
chmin/chmax beats ones, where the potential counts distinct values.

Call a bit MIXED in a node when the node's values do not all agree on it. Since the node stores
the AND and the OR of everything under it, the mixed bits are exactly andAll ^ orAll -- one
&-and-^ gives you the whole set in O(1), which is the only reason this is affordable.

Give each node a score equal to how many of its K bits are mixed, and sum that over all nodes.
A node's score is at most K, and there are O(n) nodes over logN levels, so the whole tree starts
at O(n * K * logN).

WHY THIS IS THE RIGHT THING TO COUNT: an AND / OR / XOR is uniform across a node exactly when it
leaves every mixed bit alone. If it touches only bits the node already agrees on, then every value
changes by the SAME delta -- which is why max, min AND sum all survive the O(1) apply here, not
just max. And if it does touch a mixed bit, then after the operation that bit is no longer mixed
(an AND forces it to 0 everywhere, an OR forces it to 1 everywhere), so the score drops.

So the three cases are:
  1) the op cannot change anything here                  -> return, free
  2) fully covered and no mixed bit is touched           -> O(1) apply, no potential spent, which
                                                            is exactly why we must NOT descend
  3) a mixed bit is touched                              -> descend, and that bit becomes uniform
                                                            in the nodes below, paying for the visit
Same shape as chmin beats: we can only descend when potential actually drops.

Pushing a tag to the children costs O(K) of potential and there are logN of them per op, so q ops
add O(q * K * logN). Total O((n + q) * K * logN).

THE TAG IS TWO MASKS, (tagAnd, tagXor), meaning  v -> (v & tagAnd) ^ tagXor.
Every per-bit function you can build out of AND / OR / XOR is one of four things -- keep, force 0,
force 1, flip -- and all four fit:
    keep     a=1 x=0        force 0  a=0 x=0
    force 1  a=0 x=1        flip     a=1 x=1
so the three operations are just
    AND x  ->  (a, x) = (x,  0)
    OR  x  ->  (a, x) = (~x, x)
    XOR x  ->  (a, x) = (~0, x)
and two tags compose into one:
    a = a1 & a2,   x = (x1 & a2) ^ x2

WHY A PUSHED TAG IS ALWAYS LEGAL:
_apply has a precondition -- mixed <= a and mixed & x == 0 -- that nothing in the code checks.
It holds because a tag is only ever created at a node that satisfied it, the operation does not
change that node's mixed set (it only touches uniform bits), and composing two tags that both
respect a mixed set gives a tag that still respects it. A child's mixed bits are a subset of its
parent's, so a tag legal for the parent is legal for the child.

WHY THE PRUNE NEEDS ALL THREE CHECKS (_noEffect):
nothing changes iff for every value v in the node, (v & a) ^ x == v. Per bit:
  flip bits    (a=1,x=1) always change something         -> a & x must be 0
  force-0 bits (a=0,x=0) need the bit already 0 for all  -> ~a & ~x & orAll must be 0
  force-1 bits (a=0,x=1) need the bit already 1 for all  -> ~a & x & ~andAll must be 0
Dropping the last two costs real time -- a pure OR would never prune.
*/

// ========================


#include <bits/stdc++.h>
using namespace std;
using ll = long long;

struct BitBeats_PERFORMANT {
    struct Node {
        ll mx, mn, sum, sz;
        unsigned andAll, orAll;
        unsigned tagAnd, tagXor;   // v -> (v & tagAnd) ^ tagXor
    };
    int n;
    unsigned FULL;
    vector<Node> t;

    BitBeats_PERFORMANT(const vector<unsigned>& arr, int bits = 20) {
        n = (int)arr.size();
        FULL = (bits >= 32) ? ~0u : ((1u << bits) - 1u);
        t.assign(4 * max(1, n), Node{});
        if (n) _build(1, 0, n - 1, arr);
    }

    void _build(int i, int tl, int tr, const vector<unsigned>& arr) {
        t[i].tagAnd = FULL; t[i].tagXor = 0;
        if (tl == tr) {
            unsigned v = arr[tl];
            t[i].mx = t[i].mn = t[i].sum = v;
            t[i].andAll = t[i].orAll = v;
            t[i].sz = 1;
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
        nd.mx = max(a.mx, b.mx);
        nd.mn = min(a.mn, b.mn);
        nd.sum = a.sum + b.sum;
        nd.sz = a.sz + b.sz;
        nd.andAll = a.andAll & b.andAll;
        nd.orAll = a.orAll | b.orAll;
        nd.tagAnd = FULL; nd.tagXor = 0;
    }

    // legal only when every bit the node disagrees on is kept: mixed <= a and mixed & x == 0.
    // then every value changes by the SAME delta, so mx / mn / sum all just shift.
    void _apply(int i, unsigned a, unsigned x) {
        Node& nd = t[i];
        unsigned keep = (a ^ x) & FULL;              // uniform-1 bits survive as 1 exactly here
        ll delta = (ll)((~nd.orAll) & x & FULL) - (ll)(nd.andAll & ~keep & FULL);
        nd.mx += delta; nd.mn += delta;
        nd.sum += delta * nd.sz;
        nd.andAll = ((nd.andAll & a) ^ x) & FULL;
        nd.orAll = ((nd.orAll & a) ^ x) & FULL;
        nd.tagAnd = (nd.tagAnd & a) & FULL;
        nd.tagXor = ((nd.tagXor & a) ^ x) & FULL;
    }

    void _push(int i, int tl, int tr) {
        if (tl == tr) return;
        Node& nd = t[i];
        if (nd.tagAnd == FULL && nd.tagXor == 0) return;
        _apply(2 * i, nd.tagAnd, nd.tagXor);
        _apply(2 * i + 1, nd.tagAnd, nd.tagXor);
        nd.tagAnd = FULL; nd.tagXor = 0;
    }

    void _upd(int i, int tl, int tr, int ql, int qr, unsigned a, unsigned x) {
        if (qr < tl || ql > tr) return;
        if (_noEffect(i, a, x)) return;
        unsigned mixed = (t[i].andAll ^ t[i].orAll) & FULL;
        if (ql <= tl && qr >= tr && (mixed & ((~a) | x) & FULL) == 0) {
            _apply(i, a, x);
            return;
        }
        _push(i, tl, tr);
        int tm = (tl + tr) / 2;
        _upd(2 * i, tl, tm, ql, qr, a, x);
        _upd(2 * i + 1, tm + 1, tr, ql, qr, a, x);
        _pull(i);
    }

    // nothing changes iff for every value v in the node, (v & a) ^ x == v.
    // per bit: keep (a=1,x=0) is always fine; flip (a=1,x=1) always changes;
    // force-0 (a=0,x=0) is fine only if the bit is already 0 everywhere (not in orAll);
    // force-1 (a=0,x=1) is fine only if it is already 1 everywhere (in andAll).
    bool _noEffect(int i, unsigned a, unsigned x) {
        if ((a & x & FULL) != 0) return false;
        if ((~a & ~x & t[i].orAll & FULL) != 0) return false;
        if ((~a & x & ~t[i].andAll & FULL) != 0) return false;
        return true;
    }

    void rangeAnd(int l, int r, unsigned X) { if (l <= r && n) _upd(1, 0, n - 1, l, r, X & FULL, 0); }
    void rangeOr(int l, int r, unsigned X)  { if (l <= r && n) _upd(1, 0, n - 1, l, r, (~X) & FULL, X & FULL); }
    void rangeXor(int l, int r, unsigned X) { if (l <= r && n) _upd(1, 0, n - 1, l, r, FULL, X & FULL); }

    void _set(int i, int tl, int tr, int p, unsigned v) {
        if (tl == tr) {
            t[i].mx = t[i].mn = t[i].sum = v;
            t[i].andAll = t[i].orAll = v;
            t[i].tagAnd = FULL; t[i].tagXor = 0;
            return;
        }
        _push(i, tl, tr);
        int tm = (tl + tr) / 2;
        if (p <= tm) _set(2 * i, tl, tm, p, v); else _set(2 * i + 1, tm + 1, tr, p, v);
        _pull(i);
    }
    void pointSet(int p, unsigned v) { if (n) _set(1, 0, n - 1, p, v & FULL); }

    ll _qmax(int i, int tl, int tr, int ql, int qr) {
        if (qr < tl || ql > tr) return LLONG_MIN;
        if (ql <= tl && qr >= tr) return t[i].mx;
        _push(i, tl, tr);
        int tm = (tl + tr) / 2;
        return max(_qmax(2 * i, tl, tm, ql, qr), _qmax(2 * i + 1, tm + 1, tr, ql, qr));
    }
    ll rangeMax(int l, int r) { return (l > r || !n) ? LLONG_MIN : _qmax(1, 0, n - 1, l, r); }

    ll _qmin(int i, int tl, int tr, int ql, int qr) {
        if (qr < tl || ql > tr) return LLONG_MAX;
        if (ql <= tl && qr >= tr) return t[i].mn;
        _push(i, tl, tr);
        int tm = (tl + tr) / 2;
        return min(_qmin(2 * i, tl, tm, ql, qr), _qmin(2 * i + 1, tm + 1, tr, ql, qr));
    }
    ll rangeMin(int l, int r) { return (l > r || !n) ? LLONG_MAX : _qmin(1, 0, n - 1, l, r); }

    ll _qsum(int i, int tl, int tr, int ql, int qr) {
        if (qr < tl || ql > tr) return 0;
        if (ql <= tl && qr >= tr) return t[i].sum;
        _push(i, tl, tr);
        int tm = (tl + tr) / 2;
        return _qsum(2 * i, tl, tm, ql, qr) + _qsum(2 * i + 1, tm + 1, tr, ql, qr);
    }
    ll rangeSum(int l, int r) { return (l > r || !n) ? 0 : _qsum(1, 0, n - 1, l, r); }

    unsigned _qand(int i, int tl, int tr, int ql, int qr) {
        if (qr < tl || ql > tr) return FULL;
        if (ql <= tl && qr >= tr) return t[i].andAll;
        _push(i, tl, tr);
        int tm = (tl + tr) / 2;
        return _qand(2 * i, tl, tm, ql, qr) & _qand(2 * i + 1, tm + 1, tr, ql, qr);
    }
    unsigned rangeAndQuery(int l, int r) { return (l > r || !n) ? FULL : _qand(1, 0, n - 1, l, r); }

    unsigned _qor(int i, int tl, int tr, int ql, int qr) {
        if (qr < tl || ql > tr) return 0;
        if (ql <= tl && qr >= tr) return t[i].orAll;
        _push(i, tl, tr);
        int tm = (tl + tr) / 2;
        return _qor(2 * i, tl, tm, ql, qr) | _qor(2 * i + 1, tm + 1, tr, ql, qr);
    }
    unsigned rangeOrQuery(int l, int r) { return (l > r || !n) ? 0u : _qor(1, 0, n - 1, l, r); }

    ll pointGet(int p) { return rangeMax(p, p); }
};