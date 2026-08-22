#include <bits/stdc++.h>
using namespace std;
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
// nearest index to the left that is strictly smaller than arr[i]
// -1 if none, pop while arr[st.back()] >= arr[i]
template <typename T>
vector<int> rightmostOnLeftLtNum(const vector<T>& arr) {
    int n = arr.size();
    vector<int> st, res(n, -1);
    for (int i = 0; i < n; i++) {
        while (!st.empty() && arr[st.back()] >= arr[i]) st.pop_back();
        res[i] = st.empty() ? -1 : st.back();
        st.push_back(i);
    }
    return res;
}

// nearest index to the left that is smaller than or equal to arr[i]
// -1 if none, pop while arr[st.back()] > arr[i]
template <typename T>
vector<int> rightmostOnLeftLteNum(const vector<T>& arr) {
    int n = arr.size();
    vector<int> st, res(n, -1);
    for (int i = 0; i < n; i++) {
        while (!st.empty() && arr[st.back()] > arr[i]) st.pop_back();
        res[i] = st.empty() ? -1 : st.back();
        st.push_back(i);
    }
    return res;
}

// nearest index to the left that is strictly greater than arr[i]
// -1 if none, pop while arr[st.back()] <= arr[i]
template <typename T>
vector<int> rightmostOnLeftGtNum(const vector<T>& arr) {
    int n = arr.size();
    vector<int> st, res(n, -1);
    for (int i = 0; i < n; i++) {
        while (!st.empty() && arr[st.back()] <= arr[i]) st.pop_back();
        res[i] = st.empty() ? -1 : st.back();
        st.push_back(i);
    }
    return res;
}

// nearest index to the left that is greater than or equal to arr[i]
// -1 if none, pop while arr[st.back()] < arr[i]
template <typename T>
vector<int> rightmostOnLeftGteNum(const vector<T>& arr) {
    int n = arr.size();
    vector<int> st, res(n, -1);
    for (int i = 0; i < n; i++) {
        while (!st.empty() && arr[st.back()] < arr[i]) st.pop_back();
        res[i] = st.empty() ? -1 : st.back();
        st.push_back(i);
    }
    return res;
}

// nearest index to the right that is strictly smaller than arr[i]
// n if none, pop while arr[st.back()] >= arr[i]
template <typename T>
vector<int> leftmostOnRightLtNum(const vector<T>& arr) {
    int n = arr.size();
    vector<int> st, res(n, n);
    for (int i = n - 1; i >= 0; i--) {
        while (!st.empty() && arr[st.back()] >= arr[i]) st.pop_back();
        res[i] = st.empty() ? n : st.back();
        st.push_back(i);
    }
    return res;
}

// nearest index to the right that is smaller than or equal to arr[i]
// n if none, pop while arr[st.back()] > arr[i]
template <typename T>
vector<int> leftmostOnRightLteNum(const vector<T>& arr) {
    int n = arr.size();
    vector<int> st, res(n, n);
    for (int i = n - 1; i >= 0; i--) {
        while (!st.empty() && arr[st.back()] > arr[i]) st.pop_back();
        res[i] = st.empty() ? n : st.back();
        st.push_back(i);
    }
    return res;
}

// nearest index to the right that is strictly greater than arr[i]
// n if none, pop while arr[st.back()] <= arr[i]
template <typename T>
vector<int> leftmostOnRightGtNum(const vector<T>& arr) {
    int n = arr.size();
    vector<int> st, res(n, n);
    for (int i = n - 1; i >= 0; i--) {
        while (!st.empty() && arr[st.back()] <= arr[i]) st.pop_back();
        res[i] = st.empty() ? n : st.back();
        st.push_back(i);
    }
    return res;
}

// nearest index to the right that is greater than or equal to arr[i]
// n if none, pop while arr[st.back()] < arr[i]
template <typename T>
vector<int> leftmostOnRightGteNum(const vector<T>& arr) {
    int n = arr.size();
    vector<int> st, res(n, n);
    for (int i = n - 1; i >= 0; i--) {
        while (!st.empty() && arr[st.back()] < arr[i]) st.pop_back();
        res[i] = st.empty() ? n : st.back();
        st.push_back(i);
    }
    return res;
}

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n; cin >> n;
    vector<int> A(n); for (int i = 0; i < n; i++) cin >> A[i];
    vector<int> firstOnRightGte = leftmostOnRightGteNum(A);
    vector<int> firstOnLeftGte = rightmostOnLeftGteNum(A);
    vector<int> B = A;
    sort(B.begin(), B.end());
    B.erase(unique(B.begin(), B.end()), B.end());
    unordered_map<int, vector<int>> numToIdxs;
    for (int i = 0; i < n; i++) {
        numToIdxs[A[i]].push_back(i);
    }
    vector<int> dp(n, 0);
    MaxSegTree seg(dp);
    for (auto v : B) {
        for (auto idx : numToIdxs[v]) {
            int leftGte = firstOnLeftGte[idx];
            int rightGte = firstOnRightGte[idx];
            int L = leftGte + 1;
            int R = rightGte - 1;
            int mx = seg.queryMax(L, R);
            seg.pointAssign(idx, mx + 1);
        }
    }
    cout << seg.queryMax(0, n - 1);
}