// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/persistent-online-order-stats-mex/template.cpp
// @operations: append countGtX countGteX countInValRange countLtX countLteX countOccurrences getAll kthSmallest largestLtX largestLteX maxAll minAll pointGet pop rangeMax rangeMex rangeMin size smallestGtX smallestGteX
// @data-structure-type: persistent
// @complexities:
//   append: log(U)
//   countGtX: log(U)
//   countGteX: log(U)
//   countInValRange: log(U)
//   countLtX: log(U)
//   countLteX: log(U)
//   countOccurrences: log(U)
//   getAll: N
//   kthSmallest: log(U)
//   largestLtX: log(U)
//   largestLteX: log(U)
//   pointGet: 1
//   pop: 1
//   rangeMax: log(U)
//   rangeMex: log(U)
//   rangeMin: log(U)
//   smallestGtX: log(U)
//   smallestGteX: log(U)
//   size: 1
//   minAll: log(U)
//   maxAll: log(U)
//   build: N*log(U)
// @memory:
//   layout: none
//   node: L[1*N*log(U)] R[1*N*log(U)] C[1*N*log(U)]
//   tags: none
//   other: root[1*N] arr[1*N] mexRoot[1*N] ML[1*N*log(U)] MR[1*N*log(U)] MN[1*N*log(U)]
//   note: N = every value ever added (initial array plus each append); each adds one root-to-leaf path of log U nodes over the value range [valLo, valHi] (and one in the mex tree)

// An array that grows: append(v) appends, and queries on any a[l..r] can come in between. Nothing is known up
// front, so the persistent seg tree is over the value range [valLo, valHi]: version p holds a[0..p-1], a[l..r] is
// version r + 1 minus version l, and each append adds one version. Values are integers; query arguments (x, lowVal,
// ...) can be anything. 0-indexed, inclusive.
// rangeMex: a second persistent tree, over the values 0..min(valHi, 2^30) + 1, holding each value's last index.
// T: int, long long, ....
template <typename T>
struct PersistentOnlineOrderStats {
    int n = 0;
    long long klo, khi;            // the tree is over the values valLo..valHi
    vector<T> arr;
    vector<int> root;     // node 0 = the empty tree
    struct Node {  // a node's fields side by side: a walk reads them together (faster than one array per field)
        int L = 0;
        int R = 0;
        int C = 0;
    };
    vector<Node> nd;  // node 0 = the empty tree
    int mexHi;                     // mex <= this: no value here is ever added
    vector<int> mexRoot;
    struct MexNode {  // a node's fields side by side: a walk reads them together (faster than one array per field)
        int ML = 0;
        int MR = 0;
        int MN = -1;
    };
    vector<MexNode> mnd;  // node 0 = the empty tree

    // O(N log U) -- arr: the initial array (may be empty), 0-indexed; every value ever added must lie in [valLo, valHi]
    // (any integers, negative is fine; U = valHi - valLo + 1)
    PersistentOnlineOrderStats(const vector<T>& a, long long valLo, long long valHi)
        : klo(valLo), khi(valHi), root(1, 0), nd(1), mexHi(int(min(max(valHi, 0LL), 1LL << 30) + 1)), mexRoot(1, 0),
            mnd(1) {
        for (const T& v : a) append(v);
    }

    // O(logU) -- append v (valLo <= v <= valHi): it becomes a[n], and n grows by 1
    void append(T v) {
        root.push_back(ins(root.back(), (long long)v, v));
        int prev = mexRoot.back();
        mexRoot.push_back(T(0) <= v && (long long)v <= mexHi ? mexSet(prev, 0, mexHi, int(v), n) : prev);
        arr.push_back(v), n++;
    }

    // O(1) -- remove a[n-1] and return it: the newest version is dropped (its nodes stay allocated); needs n >= 1,
    // else throws out_of_range
    T pop() {
        if (n < 1) throw out_of_range("pop: needs n >= 1");
        root.pop_back();
        mexRoot.pop_back();
        T v = arr.back();
        arr.pop_back(), n--;
        return v;
    }

    // O(1) -- a[i]; needs 0 <= i < size(), else throws out_of_range
    T pointGet(int i) const {
        if (i < 0 || i >= size()) throw out_of_range("pointGet: needs 0 <= i < size()");
        return arr[i];
    }

    // O(N) -- the whole array (a copy)
    vector<T> getAll() const { return arr; }

    // O(1) -- the current length of the array
    int size() const { return (int)arr.size(); }

    // O(logN) -- # of i in [l, r] with a[i] == x; needs 0 <= l <= r < size(), else throws out_of_range
    long long countOccurrences(long long l, long long r, T x) const {
        if (l < 0 || l > r || r >= size()) throw out_of_range("countOccurrences: needs 0 <= l <= r < size()");
        return countInValRange(l, r, x, x);
    }

    // O(logN) -- # of i in [l, r] with lowVal <= a[i] <= highVal; needs 0 <= l <= r < size(), else throws
    // out_of_range
    long long countInValRange(long long l, long long r, T lowVal, T highVal) const {
        if (l < 0 || l > r || r >= size()) throw out_of_range("countInValRange: needs 0 <= l <= r < size()");
        if (highVal < lowVal) return 0;
        return countBelow(l, r, ub(highVal)) - countBelow(l, r, lb(lowVal));
    }

    // O(logN) -- # of values < x in a[l..r]; needs 0 <= l <= r < size(), else throws out_of_range
    long long countLtX(long long l, long long r, T x) const {
        if (l < 0 || l > r || r >= size()) throw out_of_range("countLtX: needs 0 <= l <= r < size()");
        return countBelow(l, r, lb(x));
    }

    // O(logN) -- # of values <= x in a[l..r]; needs 0 <= l <= r < size(), else throws out_of_range
    long long countLteX(long long l, long long r, T x) const {
        if (l < 0 || l > r || r >= size()) throw out_of_range("countLteX: needs 0 <= l <= r < size()");
        return countBelow(l, r, ub(x));
    }

    // O(logN) -- # of values > x in a[l..r]; needs 0 <= l <= r < size(), else throws out_of_range
    long long countGtX(long long l, long long r, T x) const {
        if (l < 0 || l > r || r >= size()) throw out_of_range("countGtX: needs 0 <= l <= r < size()");
        return r - l + 1 - countBelow(l, r, ub(x));
    }

    // O(logN) -- # of values >= x in a[l..r]; needs 0 <= l <= r < size(), else throws out_of_range
    long long countGteX(long long l, long long r, T x) const {
        if (l < 0 || l > r || r >= size()) throw out_of_range("countGteX: needs 0 <= l <= r < size()");
        return r - l + 1 - countBelow(l, r, lb(x));
    }

    // O(logN) -- the k-th smallest of a[l..r] (k = 1 is the min); needs 0 <= l <= r < size() and 1 <= k <= r - l + 1,
    // else throws out_of_range
    T kthSmallest(long long l, long long r, long long k) const {
        if (l < 0 || l > r || r >= size()) throw out_of_range("kthSmallest: needs 0 <= l <= r < size()");
        if (k < 1 || k > r - l + 1) throw out_of_range("kthSmallest: needs 1 <= k <= r - l + 1");
        return kth(l, r, k);
    }

    // O(logN) -- min of a[l..r]; needs 0 <= l <= r < size(), else throws out_of_range
    T rangeMin(long long l, long long r) const {
        if (l < 0 || l > r || r >= size()) throw out_of_range("rangeMin: needs 0 <= l <= r < size()");
        return kth(l, r, 1);
    }

    // O(logN) -- max of a[l..r]; needs 0 <= l <= r < size(), else throws out_of_range
    T rangeMax(long long l, long long r) const {
        if (l < 0 || l > r || r >= size()) throw out_of_range("rangeMax: needs 0 <= l <= r < size()");
        return kth(l, r, r - l + 1);
    }

    // O(logN) -- smallest value >= x in a[l..r], or nullopt; needs 0 <= l <= r < size(), else throws out_of_range
    optional<T> smallestGteX(long long l, long long r, T x) const {
        if (l < 0 || l > r || r >= size()) throw out_of_range("smallestGteX: needs 0 <= l <= r < size()");
        long long c = countBelow(l, r, lb(x));
        if (c == r - l + 1) return nullopt;
        return kth(l, r, c + 1);
    }

    // O(logN) -- smallest value > x in a[l..r], or nullopt; needs 0 <= l <= r < size(), else throws out_of_range
    optional<T> smallestGtX(long long l, long long r, T x) const {
        if (l < 0 || l > r || r >= size()) throw out_of_range("smallestGtX: needs 0 <= l <= r < size()");
        long long c = countBelow(l, r, ub(x));
        if (c == r - l + 1) return nullopt;
        return kth(l, r, c + 1);
    }

    // O(logN) -- largest value <= x in a[l..r], or nullopt; needs 0 <= l <= r < size(), else throws out_of_range
    optional<T> largestLteX(long long l, long long r, T x) const {
        if (l < 0 || l > r || r >= size()) throw out_of_range("largestLteX: needs 0 <= l <= r < size()");
        long long c = countBelow(l, r, ub(x));
        if (c == 0) return nullopt;
        return kth(l, r, c);
    }

    // O(logN) -- largest value < x in a[l..r], or nullopt; needs 0 <= l <= r < size(), else throws out_of_range
    optional<T> largestLtX(long long l, long long r, T x) const {
        if (l < 0 || l > r || r >= size()) throw out_of_range("largestLtX: needs 0 <= l <= r < size()");
        long long c = countBelow(l, r, lb(x));
        if (c == 0) return nullopt;
        return kth(l, r, c);
    }

    // O(logN) -- smallest integer >= 0 that is not in a[l..r]; needs 0 <= l <= r < size(), else throws out_of_range
    int rangeMex(int l, int r) const {
        if (l < 0 || l > r || r >= size()) throw out_of_range("rangeMex: needs 0 <= l <= r < size()");
        return mexFrom(l, r, 0);
    }

    static long long lb(T x) { return (long long)x; }       // "values < this" for < x
    static long long ub(T x) { return (long long)x + 1; }   // "values < this" for <= x (integers)

    // O(log(U)) -- min of the whole array a[0..n-1] (rangeMin(0, n - 1)); needs n >= 1, else throws out_of_range
    auto minAll() {
        if (size() < 1) throw out_of_range("minAll: needs n >= 1");
        return rangeMin(0, size() - 1);
    }

    // O(log(U)) -- max of the whole array a[0..n-1] (rangeMax(0, n - 1)); needs n >= 1, else throws out_of_range
    auto maxAll() {
        if (size() < 1) throw out_of_range("maxAll: needs n >= 1");
        return rangeMax(0, size() - 1);
    }

    // ---- internals ----

    // copy of version node with one more value (key = its value)
    int ins(int node, long long key, T v) {
        vector<pair<int, bool>> path;
        long long nl = klo, nh = khi;
        while (nl != nh) {
            long long mid = nl + (nh - nl) / 2;
            if (key <= mid) path.push_back({node, true}), node = nd[node].L, nh = mid;
            else path.push_back({node, false}), node = nd[node].R, nl = mid + 1;
        }
        Node n;
        n.L = 0, n.R = 0, n.C = nd[node].C + 1;
        nd.push_back(n);
        int cur = (int)nd.size() - 1;
        for (int k = (int)path.size() - 1; k >= 0; k--) {
            auto [old, left] = path[k];
            int lc = left ? cur : nd[old].L, rc = left ? nd[old].R : cur;
            Node n;
            n.L = lc, n.R = rc, n.C = nd[lc].C + nd[rc].C;
            nd.push_back(n);
            cur = (int)nd.size() - 1;
        }
        return cur;
    }

    // the k-th smallest of a[l..r], 1 <= k <= r - l + 1: walk version r + 1 minus version l
    T kth(long long l, long long r, long long k) const {
        int a = root[r + 1], b = root[l];
        long long nl = klo, nh = khi;
        while (nl != nh) {
            long long mid = nl + (nh - nl) / 2, c = nd[nd[a].L].C - nd[nd[b].L].C;
            if (k <= c) a = nd[a].L, b = nd[b].L, nh = mid;
            else k -= c, a = nd[a].R, b = nd[b].R, nl = mid + 1;
        }
        return T(nl);
    }

    // # of i in [l, r] whose value is < x
    long long countBelow(long long l, long long r, long long x) const {
        if (x <= klo) return 0;
        if (x > khi) return r - l + 1;
        int a = root[r + 1], b = root[l];
        long long nl = klo, nh = khi, res = 0;
        while (nl != nh) {
            long long mid = nl + (nh - nl) / 2;
            if (x <= mid) a = nd[a].L, b = nd[b].L, nh = mid;
            // the whole left half is below x
            else res += nd[nd[a].L].C - nd[nd[b].L].C, a = nd[a].R, b = nd[b].R, nl = mid + 1;
        }
        return res;
    }

    // copy of node with value v's last index set to i
    int mexSet(int node, int nl, int nh, int v, int i) {
        int l = mnd[node].ML, r = mnd[node].MR, x;
        if (nl == nh) x = i;
        else {
            int mid = (nl + nh) >> 1;
            if (v <= mid) l = mexSet(l, nl, mid, v, i);
            else r = mexSet(r, mid + 1, nh, v, i);
            x = min(mnd[l].MN, mnd[r].MN);
        }
        MexNode n;
        n.ML = nl == nh ? 0 : l, n.MR = nl == nh ? 0 : r, n.MN = x;
        mnd.push_back(n);
        return (int)mnd.size() - 1;
    }

    // smallest value >= s that is not in a[l..r]: the leftmost value >= s whose last index (as of r) is < l
    int mexFrom(int l, int r, int s) const {
        auto go = [&](auto&& self, int t, int nl, int nh) -> int {
            if (nh < s || mnd[t].MN >= l) return -1;  // nothing allowed here, or every value here is in a[l..r]
            if (!t) return max(nl, s);            // no value here was ever seen
            if (nl == nh) return nl;
            int mid = (nl + nh) >> 1, res = self(self, mnd[t].ML, nl, mid);
            return res >= 0 ? res : self(self, mnd[t].MR, mid + 1, nh);
        };
        return go(go, mexRoot[r + 1], 0, mexHi);
    }
};
