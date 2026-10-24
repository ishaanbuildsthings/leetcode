// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/pointGet-rangeMex/template.cpp
// @operations: pointGet rangeMex
// @data-structure-type: persistent
// @complexities:
//   pointGet: 1
//   rangeMex: log(N)
//   build: N*log(N)
// @memory:
//   layout: none
//   node: ML[1*N*log(N)] MR[1*N*log(N)] MN[1*N*log(N)]
//   tags: none
//   other: root[1*N] arr[1*N]
//   note: persistent seg tree over the values 0..N+1; version p holds each value's last index before p, and the mex of a[l..r] is the first value whose last index is < l

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
