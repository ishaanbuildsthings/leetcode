// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries/allDistinct-pointAdd-pointAssign-pointChmax-pointChmin-pointGet/template.cpp
#include <bits/stdc++.h>
using namespace std;
using ll = long long;

// @operations: allDistinct getAll pointAdd pointAssign pointChmax pointChmin pointGet
// @data-structure-type: seg-tree
// @letters: same
// @complexities:
//   allDistinct: log(N)
//   getAll: N
//   pointAdd: log(N)
//   pointAssign: log(N)
//   pointChmax: log(N)
//   pointChmin: log(N)
//   pointGet: 1
//   build: N*log(N)
// @memory:
//   layout: 2n-iterative
//   node: tree[2*N]
//   tags: none
//   other: a[1*N] chains[1*N]
//   note: tree is a min tree over nxt[i]; chains maps each value to its sorted positions (std::set); the build is O(N log N), one std::map lookup per element

// "Are all values in a[l..r] distinct?" with point updates. All indices 0-based, ranges inclusive [l, r].
// nxt[i] = next j > i with a[j] == a[i], else n. a[l..r] has a repeat iff some i in [l, r] has nxt[i] <= r,
// so it is all distinct iff min(nxt[l..r]) > r: one min query on an iterative 2N tree.
// An assign changes at most 3 nxt values: i's old predecessor, i's new predecessor, and i itself.
// T: any type usable as a std::map key.
template <typename T>
struct DistinctTree {
    int n;
    vector<T> a;
    vector<int> tree;          // min tree over nxt; leaves are tree[n + i] = nxt[i]
    map<T, set<int>> chains;   // value -> sorted positions holding it

    // O(N log N) -- one std::map lookup per element (positions arrive in increasing order, so each set insert is an
    // amortized O(1) hint insert at the end)
    explicit DistinctTree(const vector<T>& arr) : n((int)arr.size()), a(arr), tree(2 * arr.size()) {
        for (int i = 0; i < n; i++) {
            set<int>& s = chains[arr[i]];
            s.emplace_hint(s.end(), i);
        }
        for (auto& [v, s] : chains) {
            int prev = -1;
            for (int i : s) {
                if (prev != -1) tree[n + prev] = i;
                prev = i;
            }
            tree[n + prev] = n;
        }
        for (int x = n - 1; x > 0; x--) tree[x] = min(tree[2 * x], tree[2 * x + 1]);
    }

    // O(logN) -- nxt[i] = v
    void setNxt(int i, int v) {
        int p = i + n;
        tree[p] = v;
        for (p >>= 1; p; p >>= 1) tree[p] = min(tree[2 * p], tree[2 * p + 1]);
    }

    // O(logN) -- true iff no value repeats inside a[l..r]; needs 0 <= l <= r < n, else throws out_of_range
    bool allDistinct(int l, int r) const {
        if (l < 0 || l > r || r >= n) throw out_of_range("allDistinct: needs 0 <= l <= r < n");
        for (int lo = l + n, hi = r + n + 1; lo < hi; lo >>= 1, hi >>= 1) {
            if ((lo & 1) && tree[lo++] <= r) return false;
            if ((hi & 1) && tree[--hi] <= r) return false;
        }
        return true;
    }

    // O(logN) -- a[i] = v; needs 0 <= i < n, else throws out_of_range
    void pointAssign(int i, const T& v) {
        if (i < 0 || i >= n) throw out_of_range("pointAssign: needs 0 <= i < n");
        if (a[i] == v) return;
        auto oldIt = chains.find(a[i]);
        set<int>& from = oldIt->second;
        auto it = from.find(i);
        if (it != from.begin()) {
            auto nx = next(it);
            setNxt(*prev(it), nx == from.end() ? n : *nx);
        }
        from.erase(it);
        if (from.empty()) chains.erase(oldIt);
        set<int>& to = chains[v];
        auto jt = to.insert(i).first;
        auto nx = next(jt);
        setNxt(i, nx == to.end() ? n : *nx);
        if (jt != to.begin()) setNxt(*prev(jt), i);
        a[i] = v;
    }

    // O(1) -- a[i]; needs 0 <= i < n, else throws out_of_range
    T pointGet(int i) const {
        if (i < 0 || i >= n) throw out_of_range("pointGet: needs 0 <= i < n");
        return a[i];
    }

    // O(N) -- the whole array (a copy)
    vector<T> getAll() const { return a; }

    // O(logN) -- a[i] += delta; needs 0 <= i < n, else throws out_of_range
    void pointAdd(int i, const T& delta) {
        if (i < 0 || i >= n) throw out_of_range("pointAdd: needs 0 <= i < n");
        pointAssign(i, a[i] + delta);
    }

    // O(logN) -- a[i] = max(a[i], v); needs 0 <= i < n, else throws out_of_range
    void pointChmax(int i, const T& v) {
        if (i < 0 || i >= n) throw out_of_range("pointChmax: needs 0 <= i < n");
        if (v > a[i]) pointAssign(i, v);
    }

    // O(logN) -- a[i] = min(a[i], v); needs 0 <= i < n, else throws out_of_range
    void pointChmin(int i, const T& v) {
        if (i < 0 || i >= n) throw out_of_range("pointChmin: needs 0 <= i < n");
        if (v < a[i]) pointAssign(i, v);
    }
};
