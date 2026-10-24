// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/pointGet-rangeMex/sparse.cpp
// @operations: pointGet rangeMex
// @data-structure-type: persistent
// @complexities:
//   pointGet: log(N)
//   rangeMex: log(N)
//   build: N*log(N)
// @memory:
//   layout: sparse
//   node: ML[1*N*log(N)] MR[1*N*log(N)] MN[1*N*log(N)]
//   tags: none
//   other: idx[1*N] vals[1*N] root[1*N] arr[1*N]
//   note: built from N given values (index, value pairs) over any index range [lo, hi], every other index 0; costs are in N; persistent seg tree over the values 0..N+1; version p holds each value's last index before p, and the mex of a[l..r] is the first value whose last index is < l; the structure is over the given values only, and the zeros of [l, r] are added in closed form (they sit between the negatives and the positives)

// Static array; rangeMex(l, r) = smallest integer >= 0 not in a[l..r] (0-indexed, inclusive), online.
// rangeMex: a persistent seg tree over the values 0..N+1; version p holds, per value, its last index before p (-1 if
// none). The mex of a[l..r] is the first value whose last index in version r + 1 is < l.
// T: int, long long, ...
template <typename T>
struct PersistentMex {
    int n;
    vector<T> arr;
    vector<int> root, ML, MR, MN;

    // O(N log N) -- arr: the initial array, 0-indexed
    explicit PersistentMex(const vector<T>& a) : n((int)a.size()), arr(a) { buildMex(); }

    // O(1) -- a[i]
    T pointGet(int i) const { return arr[i]; }

    // O(logN) -- smallest integer >= 0 that is not in a[l..r]
    int rangeMex(int l, int r) const { return mexFrom(l, r, 0); }

    // persistent seg tree over the values 0..n+1: version p holds, per value, its last index before p (-1: none)
    void buildMex() {
        ML.assign(1, 0), MR.assign(1, 0), MN.assign(1, -1);  // node 0 = the empty tree (every last index -1)
        root.assign(n + 1, 0);
        for (int i = 0; i < n; i++)
            root[i + 1] = T(0) <= arr[i] && arr[i] <= T(n + 1) ? mexSet(root[i], 0, n + 1, int(arr[i]), i) : root[i];
    }

    // copy of node with value v's last index set to i
    int mexSet(int node, int nl, int nh, int v, int i) {
        int l = ML[node], r = MR[node], x;
        if (nl == nh) x = i;
        else {
            int mid = (nl + nh) >> 1;
            if (v <= mid) l = mexSet(l, nl, mid, v, i);
            else r = mexSet(r, mid + 1, nh, v, i);
            x = min(MN[l], MN[r]);
        }
        ML.push_back(nl == nh ? 0 : l), MR.push_back(nl == nh ? 0 : r), MN.push_back(x);
        return (int)MN.size() - 1;
    }

    // smallest value >= s that is not in a[l..r]: the leftmost value >= s whose last index (as of r) is < l
    int mexFrom(int l, int r, int s) const {
        auto go = [&](auto&& self, int t, int nl, int nh) -> int {
            if (nh < s || MN[t] >= l) return -1;  // nothing allowed here, or every value here is in a[l..r]
            if (!t) return max(nl, s);            // no value here was ever seen
            if (nl == nh) return nl;
            int mid = (nl + nh) >> 1, res = self(self, ML[t], nl, mid);
            return res >= 0 ? res : self(self, MR[t], mid + 1, nh);
        };
        return go(go, root[r + 1], 0, n + 1);
    }
};

// ======================================================================================== sparse wrapper

// The same queries over any index range [lo, hi], built from given values (index, value pairs); every other index is 0.
// The structure above runs on the given values alone (in index order). [l, r] covers given values i0..i1 and
// zeros = (r - l + 1) - (i1 - i0 + 1) zeros, and in sorted order those zeros sit right after the given negatives, so the
// k-th smallest of [l, r] is the given k-th while k <= neg, 0 while k <= neg + zeros, then the given (k - zeros)-th.
template <typename T>
struct SparsePersistentMex {
    long long lo, hi;
    vector<long long> idx;
    vector<T> vals;
    PersistentMex<T> inner;

    // O(N log N) -- [lo, hi] all 0 except the given values: (index, value) pairs with distinct indices; N = len(values)
    SparsePersistentMex(long long lo, long long hi, vector<pair<long long, T>> values) : lo(lo), hi(hi), inner(split(values)) {}

    vector<T> split(vector<pair<long long, T>>& pts) {
        sort(pts.begin(), pts.end());
        for (auto& [i, v] : pts) idx.push_back(i), vals.push_back(v);
        return vals.empty() ? vector<T>{T(0)} : vals;  // (a dummy element when there are no given values; never queried)
    }

    // {i0, i1, zeros}: the given values inside [l, r] are i0..i1, and the rest of [l, r] is that many zeros
    tuple<int, int, long long> span(long long l, long long r) const {
        int i0 = int(lower_bound(idx.begin(), idx.end(), l) - idx.begin());
        int i1 = int(upper_bound(idx.begin(), idx.end(), r) - idx.begin()) - 1;
        return {i0, i1, (r - l + 1) - (i1 - i0 + 1)};
    }

    // O(logN) -- a[i]
    T pointGet(long long i) const {
        auto it = lower_bound(idx.begin(), idx.end(), i);
        return it != idx.end() && *it == i ? vals[it - idx.begin()] : T(0);
    }

    // O(logN) -- smallest integer >= 0 that is not in a[l..r]
    long long rangeMex(long long l, long long r) const {
        auto [i0, i1, zeros] = span(l, r);
        if (i0 > i1) return 1;  // all zeros
        return zeros ? inner.mexFrom(i0, i1, 1) : inner.rangeMex(i0, i1);
    }
};
