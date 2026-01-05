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
        N = n;
        tree.assign(2 * N, array<long long, 4>{0, 0, 0, 0});
        for (int i = 0; i < N; i++) {
            tree[N + i] = baseFn(arr[i]);
        }
        for (int i = N - 1; i > 0; i--) {
            auto leftVal = tree[i << 1];
            auto rightVal = tree[(i << 1) | 1];
            tree[i] = combineFn(leftVal, rightVal);
        }
    }

    void updateAndMutateArray(int index, long long newVal) {
        int pos = N + index;
        tree[pos] = baseFn(newVal);
        pos >>= 1;
        while (pos) {
            auto leftVal = tree[pos << 1];
            auto rightVal = tree[(pos << 1) | 1];
            tree[pos] = combineFn(leftVal, rightVal);
            pos >>= 1;
        }
    }

    array<long long, 4> query(int l, int r) {
        l += N;
        r += N;
        bool hasLeft = false;
        bool hasRight = false;
        array<long long, 4> leftRes{0, 0, 0, 0};
        array<long long, 4> rightRes{0, 0, 0, 0};

        while (l <= r) {
            if ((l & 1) == 1) {
                if (!hasLeft) {
                    leftRes = tree[l];
                    hasLeft = true;
                } else {
                    leftRes = combineFn(leftRes, tree[l]);
                }
                l++;
            }
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

    int n, q;
    cin >> n >> q;
    vector<long long> arr(n);
    for (int i = 0; i < n; i++) cin >> arr[i];

    auto baseFn = [&](long long val) -> array<long long, 4> {
        return {0, 0, 0, val};
    };

    auto combine = [&](const array<long long, 4>& leftV, const array<long long, 4>& rightV) -> array<long long, 4> {
        return {0, 0, 0, leftV[3] + rightV[3]};
    };

    SegmentTree st(arr, baseFn, combine);

    for (int _ = 0; _ < q; _++) {
        int t;
        cin >> t;
        if (t == 1) {
            int k;
            long long u;
            cin >> k >> u;
            st.updateAndMutateArray(k - 1, u);
        } else {
            int a, b;
            cin >> a >> b;
            cout << st.query(a - 1, b - 1)[3] << "\n";
        }
    }

    return 0;
}
