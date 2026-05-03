#include <bits/stdc++.h>
using namespace std;

// =============================================================================
// SumSegTree<T>: iterative 2N segment tree for sum aggregate
// =============================================================================
// 0-indexed. Generic over numeric type T (int, long long, double, etc.).
// Identity is T{} (value-init, which is 0 for arithmetic types).
//
// CONSTRUCTION
//   Pass a vector<T> of initial values. Tree is built bottom-up in O(n).
//
// METHODS
//   querySum(l, r)         -> T   sum over inclusive range [l, r]
//   pointSet(index, val)         set position `index` to `val`
//   pointAdd(index, delta)       add `delta` to position `index`
//
// EXAMPLE
//   vector<long long> arr = {1, 2, 3, 4, 5};
//   SumSegTree<long long> st(arr);
// =============================================================================
template <typename T>
struct SumSegTree {
    int n, size;
    vector<T> tree;
    
    SumSegTree(const vector<T>& arr) {
        n = arr.size();
        size = 1;
        while (size < n) size <<= 1;
        tree.assign(2 * size, T{});
        for (int i = 0; i < n; i++) tree[size + i] = arr[i];
        for (int i = size - 1; i >= 1; i--) {
            tree[i] = tree[2*i] + tree[2*i+1];
        }
    }
    
    // half-open [l, r)
    T _queryHalfOpen(int l, int r) {
        T ans = T{};
        for (l += size, r += size; l < r; l >>= 1, r >>= 1) {
            if (l & 1) ans = ans + tree[l++];
            if (r & 1) ans = ans + tree[--r];
        }
        return ans;
    }
    
    // inclusive [l, r]
    T querySum(int l, int r) {
        return _queryHalfOpen(l, r + 1);
    }
    
    void pointSet(int index, T newVal) {
        int pos = size + index;
        tree[pos] = newVal;
        for (pos >>= 1; pos > 0; pos >>= 1) {
            tree[pos] = tree[2*pos] + tree[2*pos+1];
        }
    }
    
    void pointAdd(int index, T delta) {
        int pos = size + index;
        tree[pos] = tree[pos] + delta;
        for (pos >>= 1; pos > 0; pos >>= 1) {
            tree[pos] = tree[2*pos] + tree[2*pos+1];
        }
    }
};