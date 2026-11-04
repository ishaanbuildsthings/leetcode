// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/segment-trees/generic/GenericLazySeg.cpp
//
// Generic lazy segment tree: fill in Node, Tag, combine, apply and compose, then build it from leaves you make
// yourself.
// Build O(n) combines; query / update / set / get / maxRight / minLeft O(log n); memory up to 4n Nodes and 2n Tags.
//
// - A leaf is any Node you build: it can carry whatever combine and apply need (the value, its index, a flag, ...).
// - combine(left, right) gets two neighbouring segments, left first, and needn't be commutative.
// - A Tag is a pending update to every element of a segment. apply sees only the Node, so a Node that needs its
//   segment's length (adding to a sum, assigning) stores it: a leaf gets len = 1, combine adds them.
// - No identity Node or Tag is needed: the tree tracks which nodes are empty and which tags are pending itself.
// - Need a node's index range? Put lo / hi in Node: a leaf gets lo = hi = i, combine takes left.lo and right.hi.
//
// Example, range add + range assign, range sum + max:
//   struct Node { long long sum, mx; int len; };
//   struct Tag { bool assign; long long v; }; // assign: every element becomes v; else every element gets + v
//   Node combine(const Node& a, const Node& b) { return {a.sum + b.sum, max(a.mx, b.mx), a.len + b.len}; }
//   void apply(Node& x, const Tag& g) {
//       if (g.assign) x.sum = g.v * x.len, x.mx = g.v;
//       else x.sum += g.v * x.len, x.mx += g.v;
//   }
//   void compose(Tag& old, const Tag& g) { if (g.assign) old = g; else old.v += g.v; }
//   vector<Node> leaves(n);
//   for (int i = 0; i < n; i++) leaves[i] = {a[i], a[i], 1};
//   LazySeg seg(leaves);
//   seg.update(l, r, {false, 5});  // add 5 to l..r
//   seg.update(l, r, {true, 7});   // assign 7 to l..r
//   seg.query(l, r).sum;
//   // first r >= l where max(l..r) reaches k: seg.maxRight(l, [&](const Node& s) { return s.mx < k; }) + 1
#include <bits/stdc++.h>
using namespace std;

struct Node {
    // TODO: the fields one segment needs, e.g. long long sum; int len;
};

struct Tag {
    // TODO: one pending update, e.g. long long add;
};

// TODO: the Node for the segment left + right (left ends just before right starts)
Node combine(const Node& left, const Node& right) {
    Node res;
    return res;
}

// TODO: node becomes its segment after tag is applied to every element of it
void apply(Node& node, const Tag& tag) {
}

// TODO: old becomes the single Tag that does old first, then newer
void compose(Tag& old, const Tag& newer) {
}

struct LazySeg {
    int n, cap, lg;
    vector<Node> t;
    vector<Tag> lz;
    // has[k]: node k covers at least one real leaf; tagged[k]: lz[k] is pending for node k's children
    vector<char> has, tagged;

    // leaves: a[0..n-1] as Nodes
    LazySeg(const vector<Node>& leaves) : n(leaves.size()), cap(1), lg(0) {
        while (cap < n) cap *= 2, lg++;
        t.assign(2 * cap, Node());
        lz.assign(cap, Tag());
        has.assign(2 * cap, 0);
        tagged.assign(cap, 0);
        for (int i = 0; i < n; i++) t[cap + i] = leaves[i], has[cap + i] = 1;
        for (int k = cap - 1; k >= 1; k--) pull(k);
    }

    void pull(int k) {
        // the padding is a suffix, so a node with an empty right child is just its left child
        has[k] = has[2 * k];
        if (has[2 * k + 1]) t[k] = combine(t[2 * k], t[2 * k + 1]);
        else if (has[2 * k]) t[k] = t[2 * k];
    }

    void applyAt(int k, const Tag& tag) {
        if (!has[k]) return;
        apply(t[k], tag);
        if (k < cap) {
            if (tagged[k]) compose(lz[k], tag);
            else lz[k] = tag, tagged[k] = 1;
        }
    }

    void push(int k) {
        if (!tagged[k]) return;
        applyAt(2 * k, lz[k]);
        applyAt(2 * k + 1, lz[k]);
        tagged[k] = 0;
    }

    // pushes the tags above the leaf range [l, r) (l and r already offset by cap)
    void pushAbove(int l, int r) {
        for (int i = lg; i >= 1; i--) {
            if (((l >> i) << i) != l) push(l >> i);
            if (((r >> i) << i) != r) push((r - 1) >> i);
        }
    }

    // how many leaves
    int size() { return n; }

    // the leaf at i, every update applied; needs 0 <= i < n, else out_of_range
    Node get(int i) {
        if (i < 0 || i >= n) throw out_of_range("get: needs 0 <= i < n");
        int k = cap + i;
        for (int j = lg; j >= 1; j--) push(k >> j);
        return t[k];
    }

    // replaces the leaf at i (earlier updates don't apply to the new leaf); needs 0 <= i < n, else out_of_range
    void set(int i, const Node& leaf) {
        if (i < 0 || i >= n) throw out_of_range("set: needs 0 <= i < n");
        int k = cap + i;
        for (int j = lg; j >= 1; j--) push(k >> j);
        t[k] = leaf;
        for (int j = 1; j <= lg; j++) pull(k >> j);
    }

    // combine of the leaves l..r; needs 0 <= l <= r < n, else out_of_range
    Node query(int l, int r) {
        if (l < 0 || r >= n || l > r) throw out_of_range("query: needs 0 <= l <= r < n");
        l += cap, r += cap + 1;
        pushAbove(l, r);
        Node sl, sr;
        bool hl = false, hr = false;
        for (; l < r; l >>= 1, r >>= 1) {
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

    // applies tag to every element of l..r; needs 0 <= l <= r < n, else out_of_range
    void update(int l, int r, const Tag& tag) {
        if (l < 0 || r >= n || l > r) throw out_of_range("update: needs 0 <= l <= r < n");
        l += cap, r += cap + 1;
        pushAbove(l, r);
        for (int a = l, b = r; a < b; a >>= 1, b >>= 1) {
            if (a & 1) applyAt(a++, tag);
            if (b & 1) applyAt(--b, tag);
        }
        for (int i = 1; i <= lg; i++) {
            if (((l >> i) << i) != l) pull(l >> i);
            if (((r >> i) << i) != r) pull((r - 1) >> i);
        }
    }

    // The largest r in [l, n - 1] with ok(query(l, r)) true, or l - 1 if ok(query(l, l)) is false.
    // ok must be monotone: true for l..r means true for every shorter l..r'. Needs 0 <= l < n, else out_of_range.
    template <class F>
    int maxRight(int l, F ok) {
        if (l < 0 || l >= n) throw out_of_range("maxRight: needs 0 <= l < n");
        int k = l + cap;
        for (int i = lg; i >= 1; i--) push(k >> i);
        Node sm;
        bool have = false;
        do {
            while (k % 2 == 0) k >>= 1;
            if (!has[k]) return n - 1; // only padding left: every real leaf fit
            Node nx = have ? combine(sm, t[k]) : t[k];
            if (!ok(nx)) {
                while (k < cap) {
                    push(k);
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
        for (int i = lg; i >= 1; i--) push((k - 1) >> i);
        Node sm;
        bool have = false;
        do {
            k--;
            while (k > 1 && k % 2) k >>= 1;
            Node nx = have ? combine(t[k], sm) : t[k];
            if (!ok(nx)) {
                while (k < cap) {
                    push(k);
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
