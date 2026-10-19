// @operations: countDistinct pointAdd pointAssign pointChmax pointChmin pointGet
// @data-structure-type: sqrt
// @complexities:
//   countDistinct: sqrt(N)*log(N)
//   pointAdd: sqrt(N)
//   pointAssign: sqrt(N)
//   pointChmax: sqrt(N)
//   pointChmin: sqrt(N)
//   pointGet: 1
//   build: N*log(N)
// @memory:
//   layout: none
//   node: blocks[1*N]
//   tags: none
//   other: a[1*N] nxt[1*N] chains[1*N]
//   note: blocks are sqrt(N) sorted lists of next-occurrence indices (a query binary-searches each whole block); chains maps each value to its sorted positions (C++: std::set; Python: plain lists, so an assign is a memmove over that value's occurrences)

// Range count distinct with point updates, sqrt decomposition. All indices 0-based, ranges inclusive.
// nxt[i] = next j > i with a[j] == a[i], else n. A value is counted once per window, at its LAST occurrence:
// nxt[i] > r. blocks[b] = sorted nxt values of block b; chains[v] = positions holding v (pred / succ lookup).
// An assign touches at most 3 nxt entries. Build O(N log N), update O(sqrt N), query O(sqrt N log N).
// T: any type usable as a std::map key.
template <typename T>
struct DynamicDistinct {
    int n, B;
    vector<T> a;
    vector<int> nxt;
    vector<vector<int>> blocks;
    map<T, set<int>> chains;

    // O(N log N)
    explicit DynamicDistinct(const vector<T>& arr) : n((int)arr.size()), a(arr), nxt(n, n) {
        map<T, int> last;
        for (int i = n - 1; i >= 0; i--) {
            auto it = last.find(arr[i]);
            if (it != last.end()) nxt[i] = it->second;
            last[arr[i]] = i;
            chains[arr[i]].insert(i);
        }
        B = max(1, (int)sqrtl(n));
        while ((long long)(B + 1) * (B + 1) <= n) B++;
        for (int s = 0; s < n; s += B) {
            blocks.emplace_back(nxt.begin() + s, nxt.begin() + min(n, s + B));
            sort(blocks.back().begin(), blocks.back().end());
        }
    }

    // O(sqrt N) -- overwrite nxt[i] with v, repairing i's block
    void setNxt(int i, int v) {
        vector<int>& blk = blocks[i / B];
        blk.erase(lower_bound(blk.begin(), blk.end(), nxt[i]));
        blk.insert(upper_bound(blk.begin(), blk.end(), v), v);
        nxt[i] = v;
    }

    // O(sqrt N + log N) -- a[i] = v
    void pointAssign(int i, const T& v) {
        if (a[i] == v) return;
        auto oldIt = chains.find(a[i]);
        set<int>& S = oldIt->second;
        auto it = S.find(i);
        if (it != S.begin()) {
            auto nx = next(it);
            setNxt(*prev(it), nx == S.end() ? n : *nx);
        }
        S.erase(it);
        if (S.empty()) chains.erase(oldIt);
        set<int>& Tset = chains[v];
        auto jt = Tset.insert(i).first;
        auto nx = next(jt);
        int succ = nx == Tset.end() ? n : *nx;
        if (jt != Tset.begin()) setNxt(*prev(jt), i);
        setNxt(i, succ);
        a[i] = v;
    }

    // O(sqrt N log N) -- # of distinct values in a[l..r]
    int countDistinct(int l, int r) const {
        int lb = l / B, rb = r / B, total = 0;
        if (lb == rb) {
            for (int i = l; i <= r; i++) total += nxt[i] > r;
            return total;
        }
        for (int i = l; i < (lb + 1) * B; i++) total += nxt[i] > r;
        for (int b = lb + 1; b < rb; b++) total += int(blocks[b].end() - upper_bound(blocks[b].begin(), blocks[b].end(), r));
        for (int i = rb * B; i <= r; i++) total += nxt[i] > r;
        return total;
    }

    // O(1) -- a[i]
    T pointGet(int i) const { return a[i]; }

    // a[i] = max(a[i], v)
    void pointChmax(int i, const T& v) { if (v > a[i]) pointAssign(i, v); }

    // a[i] = min(a[i], v)
    void pointChmin(int i, const T& v) { if (v < a[i]) pointAssign(i, v); }

    // a[i] += delta
    void pointAdd(int i, const T& delta) { pointAssign(i, a[i] + delta); }
};
