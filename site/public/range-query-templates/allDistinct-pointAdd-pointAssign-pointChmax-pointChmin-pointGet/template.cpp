// @operations: allDistinct pointAdd pointAssign pointChmax pointChmin pointGet
// @data-structure-type: seg-tree
// @complexities:
//   allDistinct: log(N)
//   pointAdd: log(N)
//   pointAssign: log(N)
//   pointChmax: log(N)
//   pointChmin: log(N)
//   pointGet: 1
//   build: N
// @memory:
//   layout: 2n-iterative
//   node: tree[2*N]
//   tags: none
//   other: a[1*N] chains[1*N]
//   note: tree is a min tree over nxt[i]; chains maps each value to its sorted positions (Python: plain lists, so an insert is a memmove over that value's occurrences)

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

    // O(N log N)
    explicit DistinctTree(const vector<T>& arr) : n((int)arr.size()), a(arr), tree(2 * arr.size()) {
        for (int i = 0; i < n; i++) chains[arr[i]].insert(i);
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

    // O(logN) -- true iff no value repeats inside a[l..r]
    bool allDistinct(int l, int r) const {
        for (int lo = l + n, hi = r + n + 1; lo < hi; lo >>= 1, hi >>= 1) {
            if ((lo & 1) && tree[lo++] <= r) return false;
            if ((hi & 1) && tree[--hi] <= r) return false;
        }
        return true;
    }

    // O(logN) -- a[i] = v
    void pointAssign(int i, const T& v) {
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

    // O(1) -- a[i]
    T pointGet(int i) const { return a[i]; }

    // O(logN) -- a[i] += delta
    void pointAdd(int i, const T& delta) { pointAssign(i, a[i] + delta); }

    // O(logN) -- a[i] = max(a[i], v)
    void pointChmax(int i, const T& v) { if (v > a[i]) pointAssign(i, v); }

    // O(logN) -- a[i] = min(a[i], v)
    void pointChmin(int i, const T& v) { if (v < a[i]) pointAssign(i, v); }
};
