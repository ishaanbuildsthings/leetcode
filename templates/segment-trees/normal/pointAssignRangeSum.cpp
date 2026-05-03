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