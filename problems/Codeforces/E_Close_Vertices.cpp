// centroid decomposition -> O(n log n) work

// U = unweighted distance
// W = weighted distance

// example: A<>B might have an unweighted distance of 10, but weighted of 30

// support queries, how many pairs exist with a U <= ? AND a W <= ?

// sort by unweighted
// [(U_1, W_1), (U_2, W_2), ...]
// U is non-decreasing
// W is random

// range queries l...r how many values <= ?
// support the above with a persistent segment tree, OR
// merge sort tree with fractional cascading

// log n queries

// total work: O(n log^2 n)

#include <bits/stdc++.h>
using namespace std;
using ll = long long;

struct MergeSortTree {
    int n;
    vector<vector<int>> tree; // each node stores a sorted vector of its elements
    vector<vector<int>> cntL; // cntL[nodeI][j] = # of first j elements in tree[nodeI] from left child, meaning j=0 considers NO elements, so exclusive prefix

    MergeSortTree() {}
    MergeSortTree(const vector<int>& arr) {
        n = arr.size();
        tree.resize(4 * n);
        cntL.resize(4 * n);
        build(arr, 1, 0, n - 1);
    }

    void build(const vector<int>& arr, int nodeI, int tl, int tr) {
        if (tl == tr) {
            tree[nodeI] = {arr[tl]};
            cntL[nodeI] = {0, 1};
            return;
        }
        int mid = (tl + tr) / 2;
        build(arr, 2 * nodeI, tl, mid);
        build(arr, 2 * nodeI + 1, mid + 1, tr);

        // merging with two pointers
        auto& L = tree[2 * nodeI];
        auto& R = tree[2 * nodeI + 1];
        int sz = L.size() + R.size();
        tree[nodeI].resize(sz);
        cntL[nodeI].resize(sz + 1);
        cntL[nodeI][0] = 0;
        int li = 0, ri = 0, idx = 0;
        while (li < (int)L.size() && ri < (int)R.size()) {
            if (L[li] <= R[ri]) {
                tree[nodeI][idx] = L[li++];
                cntL[nodeI][idx + 1] = cntL[nodeI][idx] + 1;
            } else {
                tree[nodeI][idx] = R[ri++];
                cntL[nodeI][idx + 1] = cntL[nodeI][idx];
            }
            idx++;
        }
        while (li < (int)L.size()) {
            tree[nodeI][idx] = L[li++];
            cntL[nodeI][idx + 1] = cntL[nodeI][idx] + 1;
            idx++;
        }
        while (ri < (int)R.size()) {
            tree[nodeI][idx] = R[ri++];
            cntL[nodeI][idx + 1] = cntL[nodeI][idx];
            idx++;
        }
    }

    // --- count >= x ---

    // p = number of elements < x in this node (cascaded from parent)
    int _countGteX(int nodeI, int tl, int tr, int ql, int qr, int p) {
        if (ql > tr || qr < tl) return 0;
        if (ql <= tl && tr <= qr) return (int)tree[nodeI].size() - p;
        int mid = (tl + tr) / 2;
        int leftP = cntL[nodeI][p], rightP = p - leftP;
        return _countGteX(2 * nodeI, tl, mid, ql, qr, leftP) +
               _countGteX(2 * nodeI + 1, mid + 1, tr, ql, qr, rightP);
    }
    // O(log n) — count elements >= x in [ql, qr]
    // One binary search at the root for lower_bound(x), then fractional cascading passes p down in O(1) per level
    int countGteX(int ql, int qr, int x) {
        int p = (int)(lower_bound(tree[1].begin(), tree[1].end(), x) - tree[1].begin()); // # elements < x in entire tree
        return _countGteX(1, 0, n - 1, ql, qr, p);
    }

    // --- count <= x ---

    // p = number of elements <= x in this node (cascaded from parent)
    int _countLteX(int nodeI, int tl, int tr, int ql, int qr, int p) {
        if (ql > tr || qr < tl) return 0;
        if (ql <= tl && tr <= qr) return p;
        int mid = (tl + tr) / 2;
        int leftP = cntL[nodeI][p], rightP = p - leftP;
        return _countLteX(2 * nodeI, tl, mid, ql, qr, leftP) +
               _countLteX(2 * nodeI + 1, mid + 1, tr, ql, qr, rightP);
    }
    // O(log n) — count elements <= x in [ql, qr]
    // One binary search at the root for upper_bound(x), then fractional cascading passes p down in O(1) per level
    int countLteX(int ql, int qr, int x) {
        int p = (int)(upper_bound(tree[1].begin(), tree[1].end(), x) - tree[1].begin()); // # elements <= x in entire tree
        return _countLteX(1, 0, n - 1, ql, qr, p);
    }

    // O(log n) — count elements in value range [valLow, valHigh] (inclusive) in index range [ql, qr]
    // Computed as countLteX(valHigh) - countLteX(valLow - 1)
    int countInRange(int ql, int qr, int valLow, int valHigh) {
        return countLteX(ql, qr, valHigh) - countLteX(ql, qr, valLow - 1);
    }

    // --- find k-th element >= x by position ---

    // returns {position, gteCount} where:
    //   position = array index of the k-th element >= x found in this subtree's overlap with [ql,qr], or -1 if not enough
    //   gteCount = how many elements >= x were found in this subtree's overlap with [ql,qr] (only meaningful when position == -1, used to adjust kRemaining for the right subtree)
    // p = number of elements < x in this node (cascaded)
    // kRemaining = how many more elements >= x we still need to find (decreases as left subtrees contribute partial counts)
    pair<int, int> _findKthGteX(int nodeI, int tl, int tr, int ql, int qr, int kRemaining, int p) {
        if (ql > tr || qr < tl) return {-1, 0};
        int gteInNode = (int)tree[nodeI].size() - p;
        if (ql <= tl && tr <= qr) {
            if (gteInNode < kRemaining) return {-1, gteInNode}; // not enough in this entire subtree, pass count up
            // enough elements exist in this subtree, but we don't know the exact index yet — must recurse to a leaf
            if (tl == tr) return {tl, 1}; // reached a leaf, this is the exact position
        }
        int mid = (tl + tr) / 2;
        int leftP = cntL[nodeI][p], rightP = p - leftP;
        auto [leftPos, leftGteCount] = _findKthGteX(2 * nodeI, tl, mid, ql, qr, kRemaining, leftP);
        if (leftPos != -1) return {leftPos, 0}; // found answer in left subtree, 0 is a dummy — doesn't matter since position != -1
        auto [rightPos, rightGteCount] = _findKthGteX(2 * nodeI + 1, mid + 1, tr, ql, qr, kRemaining - leftGteCount, rightP);
        if (rightPos != -1) return {rightPos, 0}; // found answer in right subtree, 0 is a dummy
        return {-1, leftGteCount + rightGteCount}; // answer not in this subtree, pass total count up so parent can adjust
    }
    // O(log n) — find the array index (position) of the k-th element >= x in [ql, qr] (1-indexed k, scanning left to right)
    // Returns -1 if fewer than k elements >= x exist in range
    // Note: this returns a POSITION (array index), not a VALUE
    // One binary search at root, then walks down with fractional cascading, going left first to find the earliest position
    int findKthGteX(int ql, int qr, int k, int x) {
        int p = (int)(lower_bound(tree[1].begin(), tree[1].end(), x) - tree[1].begin()); // # elements < x in entire tree
        return _findKthGteX(1, 0, n - 1, ql, qr, k, p).first;
    }

    // --- find k-th element <= x by position ---

    // returns {position, lteCount} where:
    //   position = array index of the k-th element <= x found in this subtree's overlap with [ql,qr], or -1 if not enough
    //   lteCount = how many elements <= x were found in this subtree's overlap with [ql,qr] (only meaningful when position == -1, used to adjust kRemaining for the right subtree)
    // p = number of elements <= x in this node (cascaded)
    // kRemaining = how many more elements <= x we still need to find (decreases as left subtrees contribute partial counts)
    pair<int, int> _findKthLteX(int nodeI, int tl, int tr, int ql, int qr, int kRemaining, int p) {
        if (ql > tr || qr < tl) return {-1, 0};
        int lteInNode = p;
        if (ql <= tl && tr <= qr) {
            if (lteInNode < kRemaining) return {-1, lteInNode}; // not enough in this entire subtree, pass count up
            // enough elements exist in this subtree, but we don't know the exact index yet — must recurse to a leaf
            if (tl == tr) return {tl, 1}; // reached a leaf, this is the exact position
        }
        int mid = (tl + tr) / 2;
        int leftP = cntL[nodeI][p], rightP = p - leftP;
        auto [leftPos, leftLteCount] = _findKthLteX(2 * nodeI, tl, mid, ql, qr, kRemaining, leftP);
        if (leftPos != -1) return {leftPos, 0}; // found answer in left subtree, 0 is a dummy — doesn't matter since position != -1
        auto [rightPos, rightLteCount] = _findKthLteX(2 * nodeI + 1, mid + 1, tr, ql, qr, kRemaining - leftLteCount, rightP);
        if (rightPos != -1) return {rightPos, 0}; // found answer in right subtree, 0 is a dummy
        return {-1, leftLteCount + rightLteCount}; // answer not in this subtree, pass total count up so parent can adjust
    }
    // O(log n) — find the array index (position) of the k-th element <= x in [ql, qr] (1-indexed k, scanning left to right)
    // Returns -1 if fewer than k elements <= x exist in range
    // Note: this returns a POSITION (array index), not a VALUE
    // One binary search at root, then walks down with fractional cascading, going left first to find the earliest position
    int findKthLteX(int ql, int qr, int k, int x) {
        int p = (int)(upper_bound(tree[1].begin(), tree[1].end(), x) - tree[1].begin()); // # elements <= x in entire tree
        return _findKthLteX(1, 0, n - 1, ql, qr, k, p).first;
    }
};

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n, L, W; cin >> n >> L >> W;
    vector<vector<pair<int,ll>>> adj(n); // adj[node] -> [(adjN, w), (adjN, w),...]
    for (int v = 2; v <= n; v++) {
        int parent, w; cin >> parent >> w;
        adj[v - 1].push_back({parent - 1, w});
        adj[parent - 1].push_back({v - 1, w});
    }

    vector<char> removed(n, 0); // is centroid removed
    vector<int> sz(n); // sz of component

    auto subtreeSize = [&](auto&& self, int node, int parent) -> void {
        int szHere = 1;
        for (auto& [adjNode, edgeWeight] : adj[node]) {
            if (adjNode == parent || removed[adjNode]) continue;
            self(self, adjNode, node);
            szHere += sz[adjNode];
        }
        sz[node] = szHere;
    };

    auto findCentroid = [&](auto&& self, int node, int parent, int pieceSize) -> int {
        int mxSize = 0; // max child size found so far
        int heavy = -1; // heavy child
        for (auto& [adjNode, edgeWeight] : adj[node]) {
            if (adjNode == parent || removed[adjNode]) continue;
            if (sz[adjNode] > mxSize) {
                mxSize = sz[adjNode];
                heavy = adjNode;
            }
        }
        if (mxSize <= pieceSize / 2) return node;
        return self(self, heavy, node, pieceSize);
    };

    ll out = 0;

    auto gather = [&](auto&& self, int node, int parent, int dist, ll wdist, vector<pair<ll,int>>& pairs) -> void {
        pairs.push_back({wdist, dist});
        for (auto& [adjNode, edgeWeight] : adj[node]) {
            if (removed[adjNode]) continue;
            if (adjNode == parent) continue;
            self(self, adjNode, node, dist + 1, wdist + edgeWeight, pairs);
        }
    };

    // all values already in MST
    // walk and look up in mst to contribute to score
    auto scoreBranch = [&](auto&& self, int node, int parent, int dist, ll wdist, MergeSortTree& mst, vector<pair<ll,int>>& pairs, bool gain, ll& counter, int& centroidPathCount) -> void {
        int maxUnweightedDist = L - dist; // only nodes with 0...maxUnweightedDist are legal
        ll maxWeightedDist = W - wdist; // and nodes with 0...maxWeightedDist
        if (dist <= L && wdist <= W) centroidPathCount++;
        // cerr << "gain=" << (gain ? "true" : "false") << " scoring branch at node=" << node << " dist=" << dist << " wdist=" << wdist << '\n';
        // cerr << "max unweighted dist: " << maxUnweightedDist << " max weighted dist: " << maxWeightedDist << '\n';

        // DO SOME SCORING
        // need rightmost index with a WEIGHTED distance <= maxWeightedDist
        auto it = upper_bound(pairs.begin(), pairs.end(), maxWeightedDist, [](
            ll val, const pair<ll,int>& p) {
                return val < p.first;
            }
        );
        auto idx = (it == pairs.begin() ? -1 : (it - pairs.begin() - 1));

        // query from 0...idx, if idx != -1
        if (idx != -1) {
            ll count = mst.countLteX(0, idx, maxUnweightedDist);
            // cerr << "gained amount: " << count << '\n';
            if (gain) {
                counter += count;
            } else {
                counter -= count;
            }
        }

        for (auto& [adjNode, edgeWeight] : adj[node]) {
            if (adjNode == parent || removed[adjNode]) continue;
            self(self, adjNode, node, dist + 1, wdist + edgeWeight, mst, pairs, gain, counter, centroidPathCount);
        }
    };

    auto decompose  = [&](auto&& self, int entry) -> void {
        // cerr << "DECOMPOSE CALLED ON NODE: " << entry << '\n';
        // 1. get sizes
        subtreeSize(subtreeSize, entry, -1);
        int pieceSize = sz[entry];

        // 2. find the centroid
        int centroid = findCentroid(findCentroid, entry, -1, pieceSize);

        // cout << "centroid: " << centroid << '\n';

        // 3. do some work

        // walk entire tree, gather all (weighted, unweighted) pairs
        vector<pair<ll,int>> pairs; // TODO: reserve for speedup
        // pairs.push_back({0, 0});
        for (auto& [adjNode, edgeWeight] : adj[centroid]) {
            if (removed[adjNode]) continue;
            gather(gather, adjNode, centroid, 1, edgeWeight, pairs);
        }
        sort(pairs.begin(), pairs.end());

        // for (auto& [unw, wei] : pairs) {
        //     cout << "unw: " << unw << " wei: " << wei << '\n';
        // }

        // build merge sort tree on ALL values
        vector<int> unweighteds; // TODO: speedup
        for (auto& [wei, unwei] : pairs) {
            unweighteds.push_back(unwei);
        }
        if (pairs.size() == 0) return;
        MergeSortTree mst(unweighteds);

        ll counterAll = 0;

        // walk each branch again, find # of pairs in overall tree, score result
        for (auto& [adjNode, edgeWeight] : adj[centroid]) {
            if (removed[adjNode]) continue;
            int empty = 0;
            scoreBranch(scoreBranch, adjNode, centroid, 1, edgeWeight, mst, pairs, true, counterAll, empty);
        }
        for (auto& [wei, unwei] : pairs) {
            if (2 * wei <= W && 2 * unwei <= L) counterAll--;
        }
        counterAll /= 2;
        out += counterAll; // includes pairs from any 2 nodes, EXCLUDING centroid paths

        // NOW HAVE DEDUPED DUPLICATES
        // still counting branch-branch pairs
        // missing anything-centroid pairs

        // cerr << "INITIAL SCORE AFTER DECOMP, pre-dedupe: " << out << endl;
        // walk each branch again, build an MST on only those nodes
        // walk each branch one more time, dedupe via the mst
        for (auto& [adjNode, edgeWeight] : adj[centroid]) {
            if (removed[adjNode]) continue;
            vector<pair<ll,int>> branchPairs;
            // fill up the branch pairs
            gather(gather, adjNode, centroid, 1, edgeWeight, branchPairs);
            sort(branchPairs.begin(), branchPairs.end());
            vector<int> unweightedsBranch; // TODO: speedup
            for (auto& [wei, unwei] : branchPairs) {
                unweightedsBranch.push_back(unwei);
            }
            MergeSortTree mstBranch(unweightedsBranch);
            ll localCounter = 0;
            int centroidPathCount = 0;
            scoreBranch(scoreBranch, adjNode, centroid, 1, edgeWeight, mstBranch, branchPairs, true, localCounter, centroidPathCount);
            for (auto& [wei, unwei] : branchPairs) {
                if (2 * wei <= W && 2 * unwei <= L) {
                    localCounter--;
                }
            }
            localCounter /= 2;
            out -= localCounter;
            out += centroidPathCount;
        }
        
        // 4. remove centroid
        removed[centroid] = true;

    
        // 5. recurse
        for (auto& [adjNode, edgeWeight] : adj[centroid]) {
            if (removed[adjNode]) continue;
            self(self, adjNode);
        }
    };

    decompose(decompose, 0);
    cout << out << '\n';
}