// TEMPLATE BY ISHAANBUILDSTHINGS
#include <bits/stdc++.h>
using namespace std;
template <typename T>
struct MaxSegTree {
    static constexpr T NEG = numeric_limits<T>::min();
    int n, size;
    vector<T> arr, tree;

    // O(n) time, O(n) space
    MaxSegTree(const vector<T>& a) : n(a.size()), arr(a) {
        size = 1;
        while (size < n) size <<= 1;
        tree.assign(2 * size, NEG);
        for (int i = 0; i < n; i++) tree[size + i] = a[i];
        for (int i = size - 1; i >= 1; i--)
            tree[i] = max(tree[i << 1], tree[i << 1 | 1]);
    }

    // O(log n). max over [l, r), NEG if empty
    T _queryHalfOpen(int l, int r) const {
        T ans = NEG;
        for (l += size, r += size; l < r; l >>= 1, r >>= 1) {
            if (l & 1) ans = max(ans, tree[l++]);
            if (r & 1) ans = max(ans, tree[--r]);
        }
        return ans;
    }

    // O(log n). recompute ancestors of leaf index, stopping once nothing changes
    void _pullUp(int index) {
        for (int pos = (size + index) >> 1; pos; pos >>= 1) {
            T v = max(tree[pos << 1], tree[pos << 1 | 1]);
            if (tree[pos] == v) break;
            tree[pos] = v;
        }
    }

    // O(log n). max over [l, r] inclusive, 0 if l > r
    T queryMax(int l, int r) const {
        if (l > r) return 0;
        return _queryHalfOpen(l, r + 1);
    }

    // O(1)
    T pointGet(int index) const { return tree[size + index]; }

    // O(log n)
    void pointAssign(int index, T newVal) {
        tree[size + index] = newVal;
        _pullUp(index);
    }

    // O(log n)
    void pointAssignAndMutateArray(int index, T newVal) {
        arr[index] = newVal;
        pointAssign(index, newVal);
    }

    // O(log n)
    void pointChmax(int index, T val) {
        if (val <= tree[size + index]) return;
        pointAssign(index, val);
    }

    // O(log n)
    void pointChmin(int index, T val) {
        if (val >= tree[size + index]) return;
        pointAssign(index, val);
    }
};