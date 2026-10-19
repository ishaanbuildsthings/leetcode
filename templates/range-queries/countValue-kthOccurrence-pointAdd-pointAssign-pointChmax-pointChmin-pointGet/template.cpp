// @operations: countValue kthOccurrence pointAdd pointAssign pointChmax pointChmin pointGet
// @data-structure-type: BIT
// @complexities:
//   countValue: log(N)
//   kthOccurrence: log(N)
//   pointAdd: log(N)
//   pointAssign: log(N)
//   pointChmax: log(N)
//   pointChmin: log(N)
//   pointGet: 1
//   build: N
// @memory:
//   layout: none
//   node: tree[1*N]
//   tags: none
//   other: vals[1*N]
//   note: a Fenwick tree over the 0/1 array [a[i] == number]; kthOccurrence binary-lifts over it

// Count / find the k-th occurrence of one value (fixed at build time) in a range, with point updates.
// All indices 0-based, ranges inclusive [l, r]. A Fenwick tree over ind[i] = (a[i] == number).
// kthOccurrence(l, r, k) = smallest i with ind[0] + ... + ind[i] >= (occurrences before l) + k, found by binary
// lifting down the tree in O(log N). T: any type with ==.
template <typename T>
struct CountValueBIT {
    int n, top;
    T number;
    vector<T> vals;
    vector<int> tree;  // 1-indexed Fenwick tree over the 0/1 indicator

    // O(N)
    CountValueBIT(const vector<T>& a, T number) : n((int)a.size()), top(0), number(number), vals(a), tree(a.size() + 1) {
        for (int i = 0; i < n; i++) tree[i + 1] = a[i] == number;
        for (int i = 1; i <= n; i++) {
            int j = i + (i & -i);
            if (j <= n) tree[j] += tree[i];
        }
        while (top * 2 <= n && n) top = top ? top * 2 : 1;
    }

    // O(logN) -- # of occurrences in a[0..i] (0 for i = -1)
    int prefix(int i) const {
        int s = 0;
        for (i++; i > 0; i &= i - 1) s += tree[i];
        return s;
    }

    // O(logN) -- how many i in [l, r] have a[i] == number
    int countValue(int l, int r) const { return l <= r ? prefix(r) - prefix(l - 1) : 0; }

    // O(logN) -- index of the k-th (1-indexed) i in [l, r] with a[i] == number, or -1
    int kthOccurrence(int l, int r, int k) const {
        if (k <= 0 || l > r) return -1;
        int target = prefix(l - 1) + k, pos = 0, acc = 0;
        for (int step = top; step; step >>= 1)
            if (pos + step <= n && acc + tree[pos + step] < target) pos += step, acc += tree[pos];
        return pos <= r ? pos : -1;  // pos is the 0-based index of the target-th occurrence (n if none)
    }

    // O(logN) -- a[i] = v
    void pointAssign(int i, T v) {
        int d = int(v == number) - int(vals[i] == number);
        vals[i] = v;
        if (d)
            for (i++; i <= n; i += i & -i) tree[i] += d;
    }

    // O(1) -- a[i]
    T pointGet(int i) const { return vals[i]; }

    // O(logN) -- a[i] += delta
    void pointAdd(int i, T delta) { pointAssign(i, vals[i] + delta); }

    // O(logN) -- a[i] = max(a[i], v)
    void pointChmax(int i, T v) { if (v > vals[i]) pointAssign(i, v); }

    // O(logN) -- a[i] = min(a[i], v)
    void pointChmin(int i, T v) { if (v < vals[i]) pointAssign(i, v); }
};
