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

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n, q; cin >> n >> q;
    vector<long long> vals(n);
    for (int i = 0; i < n; i++) cin >> vals[i];
    vector<vector<int>> adj(n);
    for (int i = 0; i < n - 1; i++) {
        int a, b; cin >> a >> b; a--; b--;
        adj[a].push_back(b);
        adj[b].push_back(a);
    }
    
    vector<vector<int>> children(n);
    auto makeChildren = [&](auto&& self, int node, int parent) -> void {
        for (auto adjN : adj[node]) {
            if (adjN == parent) continue;
            children[node].push_back(adjN);
            self(self, adjN, node);
        }
    };
    makeChildren(makeChildren, 0, -1);
    vector<int> tin(n);
    vector<int> tout(n);
    vector<int> dfsOrder(n); // [nodeX, nodeY, ...] in the dfs order we enumerate

    int timer = 0;
    auto getOrder = [&](auto&& self, int node) -> void {
        dfsOrder[timer] = node;
        tin[node] = timer++;
        for (auto child : children[node]) {
            self(self, child);
        }
        tout[node] = timer;
    };
    getOrder(getOrder, 0);

    vector<long long> arr(n, 0); // this is going to be the seg tree, based in dfs order of nodes
    SumSegTree<long long> st(arr);
    for (int node = 0; node < n; node++) {
        int inPos = tin[node];
        int outPos = tout[node];
        st.pointAdd(inPos, vals[node]);
        if (outPos < n) {
            st.pointAdd(outPos, -1 * vals[node]);
        }
    }
    for (int i = 0; i < q; i++) {
        int qtype; cin >> qtype;
        if (qtype == 1) {
            int node, newVal; cin >> node >> newVal; node--;
            int oldVal = vals[node];
            vals[node] = newVal;
            int diff = newVal - oldVal;
            st.pointAdd(tin[node], diff);
            if (tout[node] < n) {
                st.pointAdd(tout[node], -1 * diff);
            }
        } else {
            int node; cin >> node; node--;
            cout << st.querySum(0, tin[node]) << '\n';
        }
    }


}