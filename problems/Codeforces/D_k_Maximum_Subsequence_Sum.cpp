#include <bits/stdc++.h>
using namespace std;

const int K = 20;
const int NINF = -1000000000;

struct Node {
    int bestL[K + 1];
    int bestR[K + 1];
    int bestLR[K + 1];
    int best0[K + 1];

    Node(int v = NINF) {
        for (int i = 0; i <= K; ++i)
            bestL[i] = bestR[i] = bestLR[i] = best0[i] = v;
    }
};

inline Node base(int v) {
    Node n;
    for (int i = 1; i <= K; ++i) {
        n.bestL[i] = v;
        n.bestR[i] = v;
        n.bestLR[i] = v;
        n.best0[i] = max(v, 0);
    }
    n.bestL[0] = NINF;
    n.bestR[0] = NINF;
    n.bestLR[0] = NINF;
    n.best0[0] = 0;
    return n;
}

inline Node agg(const Node& left, const Node& right) {
    Node res;
    for (int totalTaken = 0; totalTaken <= K; ++totalTaken)
        for (int takeFromLeft = 0; takeFromLeft <= totalTaken; ++takeFromLeft) {
            int takeFromRight = totalTaken - takeFromLeft;

            res.bestL[totalTaken] = max(res.bestL[totalTaken], left.bestL[takeFromLeft] + right.best0[takeFromRight]);
            res.bestR[totalTaken] = max(res.bestR[totalTaken], left.best0[takeFromLeft] + right.bestR[takeFromRight]);
            res.best0[totalTaken] = max(res.best0[totalTaken], left.best0[takeFromLeft] + right.best0[takeFromRight]);
            res.bestLR[totalTaken] = max(res.bestLR[totalTaken], left.bestL[takeFromLeft] + right.bestR[takeFromRight]);

            if (takeFromRight < K) {
                res.bestL[totalTaken] = max(res.bestL[totalTaken], left.bestLR[takeFromLeft] + right.bestL[takeFromRight + 1]);
                res.bestR[totalTaken] = max(res.bestR[totalTaken], left.bestR[takeFromLeft] + right.bestLR[takeFromRight + 1]);
                res.bestLR[totalTaken] = max(res.bestLR[totalTaken], left.bestLR[takeFromLeft] + right.bestLR[takeFromRight + 1]);
                res.best0[totalTaken] = max(res.best0[totalTaken], left.bestR[takeFromLeft] + right.bestL[takeFromRight + 1]);
            }
        }
    return res;
}

class SegmentTree {
public:
    int N;
    vector<Node> tree;

    SegmentTree(const vector<int>& arr) {
        N = (int)arr.size();
        tree.resize(2 * N);

        // Build leaves at indices [N..2N-1]
        for (int i = 0; i < N; ++i) tree[N + i] = base(arr[i]);

        // Build internal nodes at [1..N-1]
        for (int i = N - 1; i >= 1; --i)
            tree[i] = agg(tree[i << 1], tree[(i << 1) | 1]);
    }

    // O(log n)
    void updateAndMutateArray(int index, int newVal) {
        // Update the leaf
        int pos = N + index;
        tree[pos] = base(newVal);

        // Recompute internals up to the root
        for (pos >>= 1; pos; pos >>= 1)
            tree[pos] = agg(tree[pos << 1], tree[(pos << 1) | 1]);
    }

    // O(log n)
    Node query(int l, int r) { // inclusive
        l += N;
        r += N;
        bool hasLeft = false, hasRight = false;
        Node leftRes, rightRes;

        while (l <= r) {
            // If l is a right child, use tree[l] and move to next
            if (l & 1) {
                leftRes = hasLeft ? agg(leftRes, tree[l]) : tree[l];
                hasLeft = true;
                ++l;
            }

            // If r is a left child, use tree[r] and move to previous
            if ((r & 1) == 0) {
                rightRes = hasRight ? agg(tree[r], rightRes) : tree[r];
                hasRight = true;
                --r;
            }

            l >>= 1;
            r >>= 1;
        }

        if (!hasLeft)  return rightRes;
        if (!hasRight) return leftRes;
        return agg(leftRes, rightRes);
    }
};

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int n; cin >> n;
    vector<int> arr(n);
    for (int& v : arr) cin >> v;

    int numQueries; cin >> numQueries;
    vector<vector<int>> qs;
    qs.reserve(numQueries);
    for (int i = 0; i < numQueries; ++i) {
        int op; cin >> op;
        if (op == 0) {
            int idx, val; cin >> idx >> val;
            qs.push_back({op, idx, val});
        } else {
            int l, r, k; cin >> l >> r >> k;
            qs.push_back({op, l, r, k});
        }
    }

    SegmentTree st(arr);

    for (const auto& q : qs) {
        if (q.size() == 3) {
            int i = q[1] - 1;
            int newVal = q[2];
            st.updateAndMutateArray(i, newVal);
        } else {
            int l = q[1] - 1;
            int r = q[2] - 1;
            int k = q[3];
            cout << st.query(l, r).best0[k] << '\n';
        }
    }
    return 0;
}