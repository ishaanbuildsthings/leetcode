// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/countOccurrences-leftmostIndexOf-leftmostIndexOfInRange-pointAssign-pointGet-rangeReplace-rightmostIndexOf-rightmostIndexOfInRange/template.cpp
#include <bits/stdc++.h>
using namespace std;
using ll = long long;

// @operations: countOccurrences getAll leftmostIndexOf leftmostIndexOfInRange pointAssign pointGet rangeReplace rightmostIndexOf rightmostIndexOfInRange
// @data-structure-type: position-trees
// @letters: same
// @complexities:
//   countOccurrences: log(N)
//   getAll: N*log(N)
//   leftmostIndexOf: log(N)
//   leftmostIndexOfInRange: log(N)
//   pointAssign: log(N) amortized
//   pointGet: log(N)
//   rangeReplace: log(N) amortized
//   rightmostIndexOf: log(N)
//   rightmostIndexOfInRange: log(N)
//   build: N*log(N)
// @memory:
//   layout: none
//   node: L[1*N*log(N)] R[1*N*log(N)] C[1*N*log(N)] P[1*N*log(N)] W[1*N*log(N)]
//   tags: none
//   other: roots[1*N] vals[1*N] leaf[1*N]
//   note: one dynamic seg tree over the positions per distinct value; at most about N log N nodes live at once (freed nodes are reused); values are hashed, so any values work

// One seg tree over the positions per value (mass change, CF 911G): rangeReplace(l, r, x, y) turns every x in a[l..r]
// into y in O(log N) amortized, for any values. Each distinct value keeps a seg tree over 0..n-1 holding the
// positions where it is; a change splits x's tree at [l, r] (O(log N) new nodes) and merges the cut part into y's
// tree (each step of a merge frees a node, so merges cost O(log N) amortized over the whole run). Also: where x first
// / last appears (in a range), how many times x appears in a range, a[i] and a[i] = v. All indices 0-based, ranges
// inclusive [l, r]; searches return -1 when nothing qualifies.
// T: any type with a hash (int, long long, char, ...)

template <typename T>
struct PositionTrees {
    struct SafeHash {  // splitmix64 with a seed random per run (the default hash of an integer is easy to attack)
        size_t operator()(const T& x) const {
            static const unsigned long long seed = chrono::steady_clock::now().time_since_epoch().count();
            unsigned long long z = (unsigned long long)x + seed + 0x9e3779b97f4a7c15ULL;
            z = (z ^ (z >> 30)) * 0xbf58476d1ce4e5b9ULL;
            z = (z ^ (z >> 27)) * 0x94d049bb133111ebULL;
            return z ^ (z >> 31);
        }
    };
    // node 0 = the empty tree; L / R: children, C: how many positions below, P: parent, W: which value (at roots)
    struct Node {  // a node's fields side by side: a walk reads them together (faster than one array per field)
        int L = 0, R = 0;
        int C = 0;
        int P = 0, W = 0;
    };
    int n;
    vector<Node> nd;
    vector<int> roots, freeList;
    vector<int> leaf;
    vector<T> vals;
    unordered_map<T, int, SafeHash> ids;

    // O(N log N) -- arr: the initial array
    PositionTrees(const vector<T>& arr) : n((int)arr.size()), nd(1) {
        nd.reserve(2 * n + 2);
        leaf.assign(n, 0);
        for (int i = 0; i < n; i++) {
            int k = id(arr[i]);
            roots[k] = insert(roots[k], i);
        }
        for (int k = 0; k < (int)roots.size(); k++) nd[roots[k]].W = k;
    }

    // O(1) -- the length of the array
    int size() const { return n; }

    // O(logN) amortized -- every a[i] == x with l <= i <= r becomes y; needs 0 <= l <= r < size(), else throws
    // out_of_range
    void rangeReplace(int l, int r, const T& x, const T& y) {
        if (l < 0 || l > r || r >= size()) throw out_of_range("rangeReplace: needs 0 <= l <= r < size()");
        auto it = ids.find(x);
        if (it != ids.end() && x != y) moveTo(it->second, l, r, y);
    }

    // O(logN) -- # of i in [l, r] with a[i] == x; needs 0 <= l <= r < size(), else throws out_of_range
    int countOccurrences(int l, int r, const T& x) const {
        if (l < 0 || l > r || r >= size()) throw out_of_range("countOccurrences: needs 0 <= l <= r < size()");
        auto it = ids.find(x);
        return it == ids.end() ? 0 : countIn(roots[it->second], 0, n - 1, l, r);
    }

    // O(logN) -- the smallest i with a[i] == x, or -1 if x isn't in the array
    int leftmostIndexOf(const T& x) const { return edgeOf(x, true); }

    // O(logN) -- the largest i with a[i] == x, or -1 if x isn't in the array
    int rightmostIndexOf(const T& x) const { return edgeOf(x, false); }

    // O(logN) -- the smallest i in [l, r] with a[i] == x, or -1 if there is none; needs 0 <= l <= r < size(), else
    // throws out_of_range
    int leftmostIndexOfInRange(int l, int r, const T& x) const {
        if (l < 0 || l > r || r >= size()) throw out_of_range("leftmostIndexOfInRange: needs 0 <= l <= r < size()");
        auto it = ids.find(x);
        return it == ids.end() ? -1 : firstIn(roots[it->second], 0, n - 1, l, r, true);
    }

    // O(logN) -- the largest i in [l, r] with a[i] == x, or -1 if there is none; needs 0 <= l <= r < size(), else
    // throws out_of_range
    int rightmostIndexOfInRange(int l, int r, const T& x) const {
        if (l < 0 || l > r || r >= size()) throw out_of_range("rightmostIndexOfInRange: needs 0 <= l <= r < size()");
        auto it = ids.find(x);
        return it == ids.end() ? -1 : firstIn(roots[it->second], 0, n - 1, l, r, false);
    }

    // O(logN) -- a[i]; needs 0 <= i < size(), else throws out_of_range
    T pointGet(int i) const {
        if (i < 0 || i >= size()) throw out_of_range("pointGet: needs 0 <= i < size()");
        return vals[owner(i)];
    }

    // O(logN) amortized -- a[i] = v; needs 0 <= i < size(), else throws out_of_range
    void pointAssign(int i, const T& v) {
        if (i < 0 || i >= size()) throw out_of_range("pointAssign: needs 0 <= i < size()");
        int k = owner(i);
        if (vals[k] != v) moveTo(k, i, i, v);
    }

    // O(N log N) -- the whole current array
    vector<T> getAll() const {
        vector<T> out(n);
        vector<array<int, 3>> st;
        for (int k = 0; k < (int)roots.size(); k++) {
            if (!roots[k]) continue;
            st.push_back({roots[k], 0, n - 1});
            while (!st.empty()) {
                auto [t, lo, hi] = st.back();
                st.pop_back();
                if (lo == hi) {
                    out[lo] = vals[k];
                    continue;
                }
                int mid = (lo + hi) >> 1;
                if (nd[t].L) st.push_back({nd[t].L, lo, mid});
                if (nd[t].R) st.push_back({nd[t].R, mid + 1, hi});
            }
        }
        return out;
    }

    // ---- internals ----

    int id(const T& v) {  // v's index into vals / roots (a new one, with an empty tree, the first time v is seen)
        auto [it, fresh] = ids.try_emplace(v, (int)vals.size());
        if (fresh) vals.push_back(v), roots.push_back(0);
        return it->second;
    }

    int newNode() {  // an empty node (a freed one if there is one)
        if (!freeList.empty()) {
            int x = freeList.back();
            freeList.pop_back();
            nd[x] = Node();
            return x;
        }
        nd.emplace_back();
        return (int)nd.size() - 1;
    }

    int pull(int x) {  // recompute x from its children
        int l = nd[x].L, r = nd[x].R;
        nd[x].C = nd[l].C + nd[r].C;
        nd[l].P = nd[r].P = x;
        return x;
    }

    int insert(int t, int i) {  // t's tree with position i (not in it) added; returns the root
        if (!t) t = newNode();
        int root = t, lo = 0, hi = n - 1;
        while (true) {
            nd[t].C++;
            if (lo == hi) {
                leaf[i] = t;
                return root;
            }
            int mid = (lo + hi) >> 1;
            bool left = i <= mid;
            if (!(left ? nd[t].L : nd[t].R)) {
                int c = newNode();
                (left ? nd[t].L : nd[t].R) = c;
                nd[c].P = t;
            }
            t = left ? nd[t].L : nd[t].R;
            (left ? hi : lo) = left ? mid : mid + 1;
        }
    }

    // (t without the positions in [l, r], a tree of just those); no empty nodes are left behind
    pair<int, int> split(int t, int lo, int hi, int l, int r) {
        if (!t || r < lo || hi < l) return {t, 0};
        if (l <= lo && hi <= r) return {0, t};
        int mid = (lo + hi) >> 1;
        auto [a1, b1] = split(nd[t].L, lo, mid, l, r);
        auto [a2, b2] = split(nd[t].R, mid + 1, hi, l, r);
        int cut = 0;
        if (b1 || b2) {
            cut = newNode();
            nd[cut].L = b1, nd[cut].R = b2;
            pull(cut);
        }
        if (a1 || a2) {
            nd[t].L = a1, nd[t].R = a2;
            return {pull(t), cut};
        }
        freeList.push_back(t);
        return {0, cut};
    }

    int merge(int a, int b) {  // the union of two trees over disjoint positions; b's nodes that overlap a's are freed
        if (!a || !b) return a ? a : b;
        int l = merge(nd[a].L, nd[b].L);
        int r = merge(nd[a].R, nd[b].R);
        nd[a].L = l, nd[a].R = r;
        freeList.push_back(b);
        return pull(a);
    }

    void moveTo(int k, int l, int r, const T& y) {  // the positions in [l, r] of vals[k]'s tree go to y's
        auto [keep, cut] = split(roots[k], 0, n - 1, l, r);
        roots[k] = keep;
        if (!cut) return;
        int ky = id(y);
        int t = roots[ky] = merge(roots[ky], cut);
        nd[t].P = 0, nd[t].W = ky;
    }

    int countIn(int t, int lo, int hi, int l, int r) const {
        if (!t || r < lo || hi < l) return 0;
        if (l <= lo && hi <= r) return nd[t].C;
        int mid = (lo + hi) >> 1;
        return countIn(nd[t].L, lo, mid, l, r) + countIn(nd[t].R, mid + 1, hi, l, r);
    }

    int edgeOf(const T& x, bool left) const {  // the first (left) / last position of x, or -1
        auto it = ids.find(x);
        int t = it == ids.end() ? 0 : roots[it->second];
        if (!t) return -1;
        int lo = 0, hi = n - 1;
        while (lo < hi) {
            int mid = (lo + hi) >> 1;
            if (left ? nd[t].L : !nd[t].R) t = nd[t].L, hi = mid;
            else t = nd[t].R, lo = mid + 1;
        }
        return lo;
    }

    int firstIn(int t, int lo, int hi, int l, int r, bool left) const {  // the first (left) / last position in [l, r], or -1
        if (!t || r < lo || hi < l) return -1;
        if (lo == hi) return lo;
        int mid = (lo + hi) >> 1;
        int res = left ? firstIn(nd[t].L, lo, mid, l, r, left) : firstIn(nd[t].R, mid + 1, hi, l, r, left);
        if (res != -1) return res;
        return left ? firstIn(nd[t].R, mid + 1, hi, l, r, left) : firstIn(nd[t].L, lo, mid, l, r, left);
    }

    int owner(int i) const {  // the index into vals of a[i]'s value: up from i's leaf to its tree's root
        int t = leaf[i];
        while (nd[t].P) t = nd[t].P;
        return nd[t].W;
    }
};
