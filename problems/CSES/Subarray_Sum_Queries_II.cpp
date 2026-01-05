#include <bits/stdc++.h>
using namespace std;

struct SegmentTree {
    int n;
    int N;
    vector<array<long long, 4>> tree;
    function<array<long long, 4>(long long)> baseFn;
    function<array<long long, 4>(const array<long long, 4>&, const array<long long, 4>&)> combineFn;

    SegmentTree(const vector<long long>& arr,
                function<array<long long, 4>(long long)> baseFn,
                function<array<long long, 4>(const array<long long, 4>&, const array<long long, 4>&)> combineFn)
        : n((int)arr.size()), baseFn(baseFn), combineFn(combineFn) {

        // Allocate exactly 2*n slots
        N = n;
        tree.assign(2 * N, array<long long, 4>{0, 0, 0, 0});

        // Build leaves at indices [N..2N-1]
        for (int i = 0; i < N; i++) {
            tree[N + i] = baseFn(arr[i]);
        }

        // Build internal nodes at [1..N-1]
        for (int i = N - 1; i > 0; i--) {
            auto leftVal = tree[i << 1];
            auto rightVal = tree[(i << 1) | 1];
            tree[i] = combineFn(leftVal, rightVal);
        }
    }

    // O(log n) update time: set arr[index] = newVal and rebuild up the tree
    void updateAndMutateArray(int index, long long newVal) {
        // Update the leaf
        int pos = N + index;
        tree[pos] = baseFn(newVal);

        // Recompute internals up to the root
        pos >>= 1;
        while (pos) {
            auto leftVal = tree[pos << 1];
            auto rightVal = tree[(pos << 1) | 1];
            tree[pos] = combineFn(leftVal, rightVal);
            pos >>= 1;
        }
    }

    // O(log n) query over range [l..r] inclusive
    // Returns combine( baseFn(arr[i]) for i in [l..r] )
    array<long long, 4> query(int l, int r) {
        l += N;
        r += N;
        bool hasLeft = false;
        bool hasRight = false;
        array<long long, 4> leftRes{0, 0, 0, 0};
        array<long long, 4> rightRes{0, 0, 0, 0};

        while (l <= r) {
            // If l is a right child, use tree[l] and move to next
            if ((l & 1) == 1) {
                if (!hasLeft) {
                    leftRes = tree[l];
                    hasLeft = true;
                } else {
                    leftRes = combineFn(leftRes, tree[l]);
                }
                l++;
            }

            // If r is a left child, use tree[r] and move to previous
            if ((r & 1) == 0) {
                if (!hasRight) {
                    rightRes = tree[r];
                    hasRight = true;
                } else {
                    rightRes = combineFn(tree[r], rightRes);
                }
                r--;
            }

            l >>= 1;
            r >>= 1;
        }

        if (!hasLeft) return rightRes;
        if (!hasRight) return leftRes;
        return combineFn(leftRes, rightRes);
    }
};

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int n, m;
    cin >> n >> m;
    vector<long long> arr(n);
    for (int i = 0; i < n; i++) cin >> arr[i];

    // Iterative tree with 2*N memory, left child = 2*i, right child = 2*i + 1
    //
    // Complexities:
    //   Build: O(n)
    //   Space: O(n)
    //   Query/Update: O(log n)
    //
    // baseFn:    function(value) -> nodeValue
    // combineFn: function(leftVal, rightVal) -> newValue
    //
    // This version does NOT pad to a power of two; it uses exactly 2*n slots.
    // It supports standard range‐combine queries (no need for “walk‐down” operations).

    auto baseFn = [&](long long val) -> array<long long, 4> {
        long long v = (val > 0 ? val : 0);
        return {v, v, v, val}; // max prefix, max suffix, max subarray, total sum
    };

    auto combine = [&](const array<long long, 4>& leftV, const array<long long, 4>& rightV) -> array<long long, 4> {
        long long leftP = leftV[0], leftS = leftV[1], leftMx = leftV[2], leftTot = leftV[3];
        long long rightP = rightV[0], rightS = rightV[1], rightMx = rightV[2], rightTot = rightV[3];
        long long newMx = max({leftMx, rightMx, leftS + rightP});
        long long newLeft = max(leftP, leftTot + rightP);
        long long newRight = max(rightS, rightTot + leftS);
        long long newTot = leftTot + rightTot;
        return {newLeft, newRight, newMx, newTot};
    };

    SegmentTree st(arr, baseFn, combine);

    for (int _ = 0; _ < m; _++) {
        int i;
        int j;
        cin >> i >> j;
        i -= 1;
        j -= 1;
        cout << st.query(i, j)[2] << "\n";
    }

    return 0;
}