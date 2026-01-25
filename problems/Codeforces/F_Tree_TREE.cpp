#include <bits/stdc++.h>
using namespace std;

struct Fenwick {
    int n;
    vector<int> bit;

    Fenwick(int n=0) { init(n); }

    // O(M)
    void init(int n_) {
        n = n_;
        bit.assign(n + 1, 0);
    }

    // O(log M)
    void add(int i, int delta) {
        for (; i <= n; i += i & -i) bit[i] += delta;
    }

    // O(log M): sum of freq[1..i] (internal indices)
    int sumPrefix(int i) const {
        int s = 0;
        for (; i > 0; i -= i & -i) s += bit[i];
        return s;
    }

    // O(log M): sum of freq[l..r]
    int sumRange(int l, int r) const {
        if (r < l) return 0;
        return sumPrefix(r) - sumPrefix(l - 1);
    }

    // O(log M): smallest idx in [1..M] with sumPrefix(idx) >= k
    // REQUIRE: 1 <= k <= totalCount
    int lowerBoundByPrefix(int k) const {
        int idx = 0;
        int step = 1;
        while ((step << 1) <= n) step <<= 1;

        for (; step > 0; step >>= 1) {
            int next = idx + step;
            if (next <= n && bit[next] < k) {
                idx = next;
                k -= bit[next];
            }
        }
        return idx + 1;
    }
};

struct OrderStatisticMultiset {
    vector<long long> values;
    Fenwick fw;
    vector<int> freq;

    // O(M log M): constructor builds compression
    OrderStatisticMultiset(const vector<long long>& allValues) {
        values = allValues; // duplicates allowed
        sort(values.begin(), values.end());
        values.erase(unique(values.begin(), values.end()), values.end());
        fw.init((int)values.size());
        freq.assign((int)values.size(), 0);
    }

    // O(log M): internal helper: map real value -> 0-based compressed index
    int _indexOf(long long x) const {
        auto it = lower_bound(values.begin(), values.end(), x);
        if (it == values.end() || *it != x) return -1;
        return (int)(it - values.begin());
    }

    // O(log M)
    int size() const {
        return fw.sumPrefix((int)values.size());
    }

    // O(log M): insert one occurrence (x must be in the provided universe)
    void insert(long long x) {
        int idx0 = _indexOf(x);
        assert(idx0 != -1);
        fw.add(idx0 + 1, +1);
        freq[idx0]++;
    }

    // O(log M): erase one occurrence; returns false if not present
    bool eraseOne(long long x) {
        int idx0 = _indexOf(x);
        if (idx0 == -1 || freq[idx0] == 0) return false;
        fw.add(idx0 + 1, -1);
        freq[idx0]--;
        return true;
    }

    // O(log M)
    int count(long long x) const {
        int idx0 = _indexOf(x);
        return (idx0 == -1) ? 0 : freq[idx0];
    }

    // O(log M)
    bool contains(long long x) const {
        return count(x) > 0;
    }

    // O(log M): 1-indexed kth smallest; crashes if invalid
    long long kthSmallest(int k) const {
        int total = size();
        assert(1 <= k && k <= total);
        int fenwickIdx = fw.lowerBoundByPrefix(k);
        return values[fenwickIdx - 1];
    }

    // O(log M): 1-indexed kth largest; crashes if invalid
    long long kthLargest(int k) const {
        int total = size();
        assert(1 <= k && k <= total);
        return kthSmallest(total - k + 1);
    }

    // O(log M): # <= x
    int countLTE(long long x) const {
        int r0 = upper_bound(values.begin(), values.end(), x) - values.begin(); // 0..M
        return fw.sumPrefix(r0);
    }

    // O(log M): # < x
    int countLT(long long x) const {
        int r0 = lower_bound(values.begin(), values.end(), x) - values.begin(); // 0..M
        return fw.sumPrefix(r0);
    }

    // O(log M): # >= x
    int countGTE(long long x) const {
        return size() - countLT(x);
    }

    // O(log M): # in [L..R]
    int countInRange(long long L, long long R) const {
        int l0 = lower_bound(values.begin(), values.end(), L) - values.begin();
        int r0 = upper_bound(values.begin(), values.end(), R) - values.begin();
        return fw.sumRange(l0 + 1, r0);
    }
};


void solve() {
    int n, k; cin >> n >> k;
    vector<vector<int>> adj(n + 1);
    for (int i = 0; i < n - 1; i++) {
        int a, b; cin >> a >> b;
        adj[a].push_back(b);
        adj[b].push_back(a);
    }

    // Populate the subtreeSizes vector
    vector<long long> sz(n + 1, 1);
    auto dfs1 = [&](auto&& self, int node, int parent) -> void {
        for (auto adjN : adj[node]) {
            if (adjN == parent) continue;
            self(self, adjN, node);
            sz[node] += sz[adjN];
        }
    };
    dfs1(dfs1, 1, -1);

    vector<long long> possibleSizes; for (long long size = 0; size <= n; size++) possibleSizes.push_back(size);
    OrderStatisticMultiset os(possibleSizes);
    for (int node = 1; node <= n; node++) {
        os.insert(sz[node]);
    }

    long long out = os.countGTE(k);

    auto reroot = [&](auto&& self, int node, int parent) -> void {
        for (auto adjN : adj[node]) {
            if (adjN == parent) continue;
            // we reroot from node->adjN
            // old node subtree size: N
            // old adjN subtree size: sz[adjN]
            // new adjN subtree size: N
            // new old node subtree size: N - sz[adjN]
            // so we remove sz[adjN] and add N - sz[adjN]
            os.eraseOne(sz[adjN]);
            os.insert(n - sz[adjN]);
            out += os.countGTE(k);
            self(self, adjN, node);
            os.eraseOne(n - sz[adjN]);
            os.insert(sz[adjN]);
        }
    };
    reroot(reroot, 1, -1);

    cout << out << endl;
}

int main() {
    cin.tie(nullptr);
    ios::sync_with_stdio(false);
    int t; cin >> t;
    while (t--) solve();
}