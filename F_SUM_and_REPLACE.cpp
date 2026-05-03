// SOLUTION 0, sorted container + seg tree
#include <bits/stdc++.h>
using namespace std;
using ll = long long;

constexpr int MAX_V = 1000000;
int divCounts[MAX_V + 1];

#include <vector>

// Usage:
//   std::vector<int> a = {6, 4, 1, 10, 3, 2, 4};
//   SumSegTree seg(a);
//   seg.querySum(0, 6);              // returns long long -> 30
//   seg.pointUpdate(2, 100);         // sets a[2] = 100
template <typename T>
class SumSegTree {
public:
    SumSegTree(const std::vector<T>& arr) : n_(arr.size()) {
        size_ = 1;
        while (size_ < n_) size_ <<= 1;

        tree_.assign(2 * size_, 0);
        for (size_t i = 0; i < n_; ++i) tree_[size_ + i] = arr[i];
        for (size_t idx = size_ - 1; idx >= 1; --idx)
            tree_[idx] = tree_[idx << 1] + tree_[(idx << 1) | 1];
    }

    long long querySum(size_t l, size_t r) {
        return queryHalfOpen_(l, r + 1);
    }

    void pointUpdate(size_t index, long long newVal) {
        size_t pos = size_ + index;
        tree_[pos] = newVal;
        for (pos >>= 1; pos; pos >>= 1)
            tree_[pos] = tree_[pos << 1] + tree_[(pos << 1) | 1];
    }

private:
    size_t n_;
    size_t size_;
    std::vector<long long> tree_;

    long long queryHalfOpen_(size_t l, size_t r) {
        long long ans = 0;
        l += size_;
        r += size_;
        while (l < r) {
            if (l & 1) { ans += tree_[l]; ++l; }
            if (r & 1) { --r; ans += tree_[r]; }
            l >>= 1;
            r >>= 1;
        }
        return ans;
    }
};

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n, m; cin >> n >> m;
    for (int fac = 1; fac <= MAX_V; fac++) {
        for (int mult = 1; fac * mult <= MAX_V; mult++) {
            divCounts[fac * mult]++;
        }
    }
    vector<int> A(n); for (int i = 0; i < n; i++) cin >> A[i];
    set<int> alive;
    SumSegTree seg(A);
    for (int i = 0; i < n; i++) alive.insert(i);
    for (int i = 0; i < m; i++) {
        int qtype, l, r; cin >> qtype >> l >> r; l--; r--;
        if (qtype == 1) {
            auto it = alive.lower_bound(l); // smallest index >= l
            while (it != alive.end() and *it <= r) {
                int oldVal = A[*it];
                int newVal = divCounts[oldVal];
                A[*it] = newVal;
                seg.pointUpdate(*it, newVal);
                if (newVal <= 2) {
                    it = alive.erase(it);
                } else {
                    it++;
                }
            }
        } else {
            cout << seg.querySum(l, r) << '\n';
        }
    }
}

// SOLUTION 1, LAZY SEG TREE BEATS
// #include <bits/stdc++.h>
// using namespace std;
// using ll = long long;

// constexpr int MAX_V = 1000000;
// int divCounts[MAX_V + 1];

// struct D {
//     ll tot = 0;
//     int mx = 0;
// };

// struct Seg {
//     int n;
//     vector<D> tree;

//     Seg(const vector<int>& A) {
//         n = A.size();
//         tree.resize(4 * n);
//         _build(1, 0, n - 1, A);
//     }

//     D _combine(D& left, D& right) {
//         return {left.tot + right.tot, max(left.mx, right.mx)};
//     }

//     void _pull(int nodeI) {
//         D& left = tree[2*nodeI];
//         D& right = tree[2*nodeI + 1];
//         tree[nodeI] = _combine(left, right);
//     }

//     void _build(int nodeI, int tl, int tr, const vector<int>& A) {
//         if (tl == tr) { tree[nodeI] = {A[tl], A[tl]}; return; }
//         int tm = (tl + tr) / 2;
//         _build(2*nodeI, tl, tm, A);
//         _build(2*nodeI + 1, tm + 1, tr, A);
//         _pull(nodeI);
//     }

//     D _query(int nodeI, int tl, int tr, int ql, int qr) {
//         if (tl == tr) return tree[nodeI];
//         if (ql <= tl and qr >= tr) return tree[nodeI];
//         int tm = (tl + tr) / 2;
//         if (qr <= tm) return _query(2*nodeI, tl, tm, ql, qr);
//         if (ql >= tm + 1) return _query(2*nodeI + 1, tm + 1, tr, ql, qr);
//         D left = _query(2*nodeI, tl, tm, ql, qr);
//         D right = _query(2*nodeI + 1, tm + 1, tr, ql, qr);
//         return _combine(left, right);
//     }

//     D query(int l, int r) { return _query(1, 0, n - 1, l, r); }

//     void _rangeUpdate(int nodeI, int tl, int tr, int ql, int qr) {
//         if (tree[nodeI].mx <= 2) return;
//         if (tl == tr) {
//             tree[nodeI] = {divCounts[tree[nodeI].mx], divCounts[tree[nodeI].mx]};
//             return;
//         }
//         int tm = (tl + tr) / 2;
//         if (qr <= tm) {
//             _rangeUpdate(2*nodeI, tl, tm, ql, qr);
//         } else if (ql >= tm + 1) {
//             _rangeUpdate(2*nodeI + 1, tm + 1, tr, ql, qr);
//         } else {
//             _rangeUpdate(2*nodeI, tl, tm, ql, qr);
//             _rangeUpdate(2*nodeI + 1, tm + 1, tr, ql, qr);
//         }
//         _pull(nodeI);
//     }

//     void rangeUpdate(int l, int r) { _rangeUpdate(1, 0, n - 1, l, r); }
// };

// int main() {
//     ios::sync_with_stdio(false);
//     cin.tie(nullptr);
    // for (int fac = 1; fac <= MAX_V; fac++) {
    //     for (int mult = 1; fac * mult <= MAX_V; mult++) {
    //         divCounts[fac * mult]++;
    //     }
    // }
//     int n, m; cin >> n >> m;
//     vector<int>A(n); for (int i = 0; i < n; i++) cin >> A[i];
//     Seg seg(A);
//     for (int i = 0; i < m; i++) {
//         int qtype, l, r; cin >> qtype >> l >> r; l--; r--;
//         if (qtype == 1) seg.rangeUpdate(l, r);
//         else cout << seg.query(l, r).tot << '\n';
//     }
// }