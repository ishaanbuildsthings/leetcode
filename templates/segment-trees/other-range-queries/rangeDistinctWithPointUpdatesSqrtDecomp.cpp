#include <bits/stdc++.h>
using namespace std;
// Point assign + range count distinct.
// nxt[i] = next index j > i with a[j] == a[i], else n.
// A value is counted once per window, at its LAST occurrence: nxt[i] > r.
// blocks[b] is the sorted multiset of nxt values whose index lies in block b.
// chains[v] is the sorted vector of indices holding value v (pred/succ lookup).
// nxt holds indices, so T may be any hashable type — no coordinate compression.
// O(n log n) build, O(sqrt n) update, O(sqrt n) query.
// All indices 0-based, all ranges inclusive.
template <typename T>
struct DynamicDistinct {
    int n, blockSize;
    vector<T> a;
    vector<int> nxt;
    vector<vector<int>> blocks;
    unordered_map<T, vector<int>> chains;

    DynamicDistinct() {}
    DynamicDistinct(const vector<T>& arr) {
        n = arr.size();
        a = arr;
        nxt.assign(n, n);
        chains.reserve(2 * n);
        unordered_map<T, int> last;
        last.reserve(2 * n);
        for (int i = n - 1; i >= 0; i--) {
            auto it = last.find(arr[i]);
            nxt[i] = (it == last.end()) ? n : it->second;
            last[arr[i]] = i;
        }
        for (int i = 0; i < n; i++) chains[arr[i]].push_back(i);
        blockSize = max(1, (int)sqrt((double)n));
        for (int b = 0; b < n; b += blockSize) {
            vector<int> blk(nxt.begin() + b, nxt.begin() + min(n, b + blockSize));
            sort(blk.begin(), blk.end());
            blocks.push_back(move(blk));
        }
    }

    // O(sqrt n) — overwrite nxt[i] with v, repairing i's block
    void _setNxt(int i, int v) {
        auto& blk = blocks[i / blockSize];
        blk.erase(upper_bound(blk.begin(), blk.end(), nxt[i]) - 1);
        blk.insert(upper_bound(blk.begin(), blk.end(), v), v);
        nxt[i] = v;
    }

    // O(sqrt n) — assign a[i] = val (overwrite, not add)
    // Touches at most 3 nxt entries: i's old predecessor, i's new predecessor, i.
    void pointSet(int i, const T& val) {
        T old = a[i];
        if (old == val) return;
        auto& S = chains[old];
        int k = lower_bound(S.begin(), S.end(), i) - S.begin();
        if (k > 0) _setNxt(S[k - 1], (k + 1 < (int)S.size()) ? S[k + 1] : n);
        S.erase(S.begin() + k);
        auto& T2 = chains[val];
        k = lower_bound(T2.begin(), T2.end(), i) - T2.begin();
        T2.insert(T2.begin() + k, i);
        int succ = (k + 1 < (int)T2.size()) ? T2[k + 1] : n;
        if (k > 0) _setNxt(T2[k - 1], i);
        _setNxt(i, succ);
        a[i] = val;
    }

    // O(sqrt n) — # of distinct values in a[l..r]
    int countDistinct(int l, int r) {
        int lb = l / blockSize, rb = r / blockSize, total = 0;
        if (lb == rb) {
            for (int i = l; i <= r; i++) total += (nxt[i] > r);
            return total;
        }
        for (int i = l; i < (lb + 1) * blockSize; i++) total += (nxt[i] > r);
        for (int b = lb + 1; b < rb; b++) {
            auto& blk = blocks[b];
            total += (int)blk.size() - (int)(upper_bound(blk.begin(), blk.end(), r) - blk.begin());
        }
        for (int i = rb * blockSize; i <= r; i++) total += (nxt[i] > r);
        return total;
    }

    // O(sqrt n) — true iff a[l..r] has no repeated value
    bool allDistinct(int l, int r) {
        return countDistinct(l, r) == r - l + 1;
    }
};