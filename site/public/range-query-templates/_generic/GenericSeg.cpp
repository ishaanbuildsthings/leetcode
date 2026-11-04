// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/segment-trees/generic/GenericSeg.cpp
//
// Generic segment tree: fill in Node and combine, then build it from leaves you make yourself.
// Build O(n) combines; query / set / maxRight / minLeft O(log n) combines; memory up to 4n Nodes.
//
// - A leaf is any Node you build: it can carry whatever a combine needs (the value, its index, a flag, ...).
// - combine(left, right) gets two neighbouring segments, left first, and needn't be commutative.
// - No identity Node is needed: combine is only ever called on real, non-empty segments.
// - Need a node's index range? Put lo / hi in Node: a leaf gets lo = hi = i, combine takes left.lo and right.hi.
//
// Example, max subarray sum (non-empty):
//   struct Node { long long sum, pre, suf, best; };
//   Node combine(const Node& a, const Node& b) {
//       return {a.sum + b.sum, max(a.pre, a.sum + b.pre), max(b.suf, b.sum + a.suf),
//               max({a.best, b.best, a.suf + b.pre})};
//   }
//   vector<Node> leaves(n);
//   for (int i = 0; i < n; i++) leaves[i] = {a[i], a[i], a[i], a[i]};
//   Seg seg(leaves);
//   seg.query(l, r).best;
//   seg.set(i, {x, x, x, x});
//   // first r >= l where the sum of l..r reaches k: seg.maxRight(l, [&](const Node& s) { return s.sum < k; }) + 1
#include <bits/stdc++.h>
using namespace std;

struct Node {
    // TODO: the fields one segment needs, e.g. long long sum; or long long mx; int cnt;
};

// TODO: the Node for the segment left + right (left ends just before right starts)
Node combine(const Node& left, const Node& right) {
    Node res;
    return res;
}

struct Seg {
    int n, cap;
    vector<Node> t;
    vector<char> has; // has[k]: node k covers at least one real leaf (the padding past n has none)

    // leaves: a[0..n-1] as Nodes
    Seg(const vector<Node>& leaves) : n(leaves.size()), cap(1) {
        while (cap < n) cap *= 2;
        t.assign(2 * cap, Node());
        has.assign(2 * cap, 0);
        for (int i = 0; i < n; i++) t[cap + i] = leaves[i], has[cap + i] = 1;
        for (int k = cap - 1; k >= 1; k--) pull(k);
    }

    void pull(int k) {
        // the padding is a suffix, so a node with an empty right child is just its left child
        has[k] = has[2 * k];
        if (has[2 * k + 1]) t[k] = combine(t[2 * k], t[2 * k + 1]);
        else if (has[2 * k]) t[k] = t[2 * k];
    }

    // how many leaves
    int size() { return n; }

    // the leaf at i; needs 0 <= i < n, else out_of_range
    Node get(int i) {
        if (i < 0 || i >= n) throw out_of_range("get: needs 0 <= i < n");
        return t[cap + i];
    }

    // replaces the leaf at i; needs 0 <= i < n, else out_of_range
    void set(int i, const Node& leaf) {
        if (i < 0 || i >= n) throw out_of_range("set: needs 0 <= i < n");
        int k = cap + i;
        t[k] = leaf;
        for (k >>= 1; k >= 1; k >>= 1) pull(k);
    }

    // combine of the leaves l..r; needs 0 <= l <= r < n, else out_of_range
    Node query(int l, int r) {
        if (l < 0 || r >= n || l > r) throw out_of_range("query: needs 0 <= l <= r < n");
        Node sl, sr;
        bool hl = false, hr = false;
        for (l += cap, r += cap + 1; l < r; l >>= 1, r >>= 1) {
            if (l & 1) sl = hl ? combine(sl, t[l]) : t[l], hl = true, l++;
            if (r & 1) --r, sr = hr ? combine(t[r], sr) : t[r], hr = true;
        }
        if (!hl) return sr;
        if (!hr) return sl;
        return combine(sl, sr);
    }

    // combine of every leaf; needs n >= 1, else out_of_range
    Node all() {
        if (n == 0) throw out_of_range("all: needs n >= 1");
        return t[1];
    }

    // The largest r in [l, n - 1] with ok(query(l, r)) true, or l - 1 if ok(query(l, l)) is false.
    // ok must be monotone: true for l..r means true for every shorter l..r'. Needs 0 <= l < n, else out_of_range.
    template <class F>
    int maxRight(int l, F ok) {
        if (l < 0 || l >= n) throw out_of_range("maxRight: needs 0 <= l < n");
        int k = l + cap;
        Node sm;
        bool have = false;
        do {
            while (k % 2 == 0) k >>= 1;
            if (!has[k]) return n - 1; // only padding left: every real leaf fit
            Node nx = have ? combine(sm, t[k]) : t[k];
            if (!ok(nx)) {
                while (k < cap) {
                    k *= 2;
                    Node nl = have ? combine(sm, t[k]) : t[k];
                    if (ok(nl)) sm = nl, have = true, k++;
                }
                return k - cap - 1;
            }
            sm = nx, have = true, k++;
        } while ((k & -k) != k);
        return n - 1;
    }

    // The smallest l in [0, r] with ok(query(l, r)) true, or r + 1 if ok(query(r, r)) is false.
    // ok must be monotone: true for l..r means true for every shorter l'..r. Needs 0 <= r < n, else out_of_range.
    template <class F>
    int minLeft(int r, F ok) {
        if (r < 0 || r >= n) throw out_of_range("minLeft: needs 0 <= r < n");
        int k = r + 1 + cap;
        Node sm;
        bool have = false;
        do {
            k--;
            while (k > 1 && k % 2) k >>= 1;
            Node nx = have ? combine(t[k], sm) : t[k];
            if (!ok(nx)) {
                while (k < cap) {
                    k = 2 * k + 1;
                    Node nr = have ? combine(t[k], sm) : t[k];
                    if (ok(nr)) sm = nr, have = true, k--;
                }
                return k + 1 - cap;
            }
            sm = nx, have = true;
        } while ((k & -k) != k);
        return 0;
    }
};
