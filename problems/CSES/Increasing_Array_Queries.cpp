// TEMPLATE BY ISHAAN AGRAWAL: https://github.com/ishaanbuildsthings
//
// EXAMPLE
//   SparseTable st(nums, [](int a, int b){ return min(a, b); });
//   int m = st.query(l, r);                       // inclusive [l, r]
//
//   // want the position too? feed a mapped array of pairs:
//   vector<pair<int,int>> vi(n);
//   for (int i = 0; i < n; i++) vi[i] = {nums[i], i};
//   SparseTable st2(vi, [](pair<int,int> a, pair<int,int> b){ return min(a, b); });
//   auto [val, idx] = st2.query(l, r);            // leftmost min on ties
//
// Element type and functor type are both deduced from the constructor
// arguments (C++17 CTAD), so you never write template arguments -- whatever
// vector you pass in decides T, and the lambda decides F.
//
// Static array, no updates. Build O(n log n) time and memory; query is two
// table lookups plus one combineFn call, so O(1) for cheap ops.
//
// COMBINEFN MUST BE IDEMPOTENT: f(a, a) == a. The query overlaps two windows
// that cover [l, r] between them, so anything counted twice is wrong. Min, max,
// gcd, bitwise and/or, and (value, index) pairs under min/max are all fine.
// SUM IS NOT -- use a prefix-sum array for that.
//
// T can be any copyable type: int, long long, pair, or a small struct with its
// own merge. Elements are stored by value, so keep T small.
#include <bits/stdc++.h>
using namespace std;
template <typename T, typename F>
class SparseTable {
public:
    // O(n log n) -- combineFn must be idempotent and associative
    SparseTable(const vector<T>& nums, F combineFn) : combineFn(combineFn) {
        int n = (int)nums.size();
        log2v.assign(n + 1, 0);
        for (int i = 2; i <= n; i++) log2v[i] = log2v[i >> 1] + 1;
        if (n == 0) return;
        int levels = log2v[n] + 1;
        sparse.assign(levels, vector<T>());
        sparse[0] = nums;
        for (int lvl = 1; lvl < levels; lvl++) {
            int half = 1 << (lvl - 1);
            int limit = n - (1 << lvl) + 1;
            sparse[lvl].resize(limit);
            for (int left = 0; left < limit; left++)
                sparse[lvl][left] = combineFn(sparse[lvl - 1][left],
                                              sparse[lvl - 1][left + half]);
        }
    }
    // O(combineFn) -- combine over the inclusive range [l, r].
    // Caller must ensure 0 <= l <= r < n; there is no identity element to
    // return for an empty range.
    T query(int l, int r) const {
        assert(0 <= l && l <= r && r < (int)sparse[0].size());
        int power = log2v[r - l + 1];
        int windowWidth = 1 << power;
        return combineFn(sparse[power][l], sparse[power][r - windowWidth + 1]);
    }
private:
    vector<vector<T>> sparse;
    vector<int> log2v;
    F combineFn;
};

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n, q; cin >> n >> q;
    vector<pair<int,int>> A; // holds (val, i)
    for (int i = 0; i < n; i++) {
        int v; cin >> v;
        A.push_back({v, i});
    }

    auto agg = [&](auto a, auto b) -> pair<int,int> {
        if (a.first >= b.first) {
            return a;
        }
        return b;
    };

    vector<long long> pf;
    long long curr = 0;
    for (auto tup : A) {
        curr += tup.first;
        pf.push_back(curr);
    }

    auto sumQuery = [&](int l, int r) -> long long {
        return pf[r] - (l > 0 ? pf[l - 1] : 0);
    };

    vector<int> nextI(n); // nextI[i] tells us the next point that is greater than us
    vector<int> stack; // holds incies
    for (auto [v, i] : A) {
        if (stack.size() == 0) {
            stack.push_back(i);
            continue;
        }
        while (stack.size() && v > A[stack.back()].first) {
            int poppedI = stack.back(); stack.pop_back();
            nextI[poppedI] = i;
        }
        stack.push_back(i);
    }
    for (auto i : stack) {
        nextI[i] = A.size();
    }

    vector<long long> suffIncreasingTotal(n, 0);
    for (int i = A.size() - 2; i >= 0; i--) {
        int v = A[i].first;
        int nextBigger = nextI[i];
        long long totalRight = nextBigger < n ? suffIncreasingTotal[nextBigger] : 0;
        long long width = nextBigger - i;
        long long areaLeft = width * v;
        long long newTotal = totalRight + areaLeft;
        suffIncreasingTotal[i] = newTotal;
    }

    SparseTable st(A, agg);
    for (int i = 0; i < q; i++) {
        int ql, qr; cin >> ql >> qr; ql--; qr--;
        auto [mx, mxI] = st.query(ql, qr);
        // first part, going from mxI...qr
        long long widthRight = qr - mxI + 1;
        long long areaRight = widthRight * mx;
        long long areaLeft = suffIncreasingTotal[ql] - suffIncreasingTotal[mxI];
        long long area = areaLeft + areaRight;
        long long initial = sumQuery(ql, qr);
        long long cost = area - initial;
        cout << cost << '\n';
    }
}