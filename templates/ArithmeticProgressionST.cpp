#include <vector>
#include <algorithm>

// Iterative segment tree: range arithmetic-progression add, range sum.
//
// Lazy tag: (constPart, idxPart) means "add constPart + idxPart * i to every
// underlying position i". Tags compose by addition, so no pushdown-before-
// compose dance is needed.
//
// Per-node metadata (length_, sumIdx_) is precomputed at construction to
// avoid any range arithmetic in the hot path.
//
// Public operations:
//   APSegTree(int n)                    O(n)
//   APSegTree(vector<long long>& a)     O(n)
//   rangeAddAP(l, r, start, step)       O(log n)
//   rangeSum(l, r)                      O(log n)
//   pointQuery(i)                       O(log n)
//   pushAllDown()                       O(n)  -- call before batch leafValue reads
//   leafValue(i)                        O(1)  -- only valid after pushAllDown
class APSegTree {
public:
    explicit APSegTree(int n) { build(n, nullptr); }
    explicit APSegTree(const std::vector<long long>& a) { build((int)a.size(), &a); }

    void rangeAddAP(int l, int r, long long start, long long step) {
        if (l > r) return;
        long long constPart = start - step * (long long)l;
        long long idxPart = step;
        int l0 = l + size_, r0 = r + size_;
        pushToRoot(l0);
        pushToRoot(r0);
        int lIdx = l0, rIdx = r0 + 1;
        while (lIdx < rIdx) {
            if (lIdx & 1) { applyNode(lIdx, constPart, idxPart); lIdx++; }
            if (rIdx & 1) { rIdx--; applyNode(rIdx, constPart, idxPart); }
            lIdx >>= 1;
            rIdx >>= 1;
        }
        recomputeToRoot(l0);
        recomputeToRoot(r0);
    }

    long long rangeSum(int l, int r) {
        if (l > r) return 0;
        int l0 = l + size_, r0 = r + size_;
        pushToRoot(l0);
        pushToRoot(r0);
        long long result = 0;
        int lIdx = l0, rIdx = r0 + 1;
        while (lIdx < rIdx) {
            if (lIdx & 1) { result += sum_[lIdx]; lIdx++; }
            if (rIdx & 1) { rIdx--; result += sum_[rIdx]; }
            lIdx >>= 1;
            rIdx >>= 1;
        }
        return result;
    }

    long long pointQuery(int i) { return rangeSum(i, i); }

    void pushAllDown() {
        for (int node = 1; node < size_; node++) {
            long long c = lazyConst_[node], d = lazyIdx_[node];
            if (c | d) {
                applyNode(2 * node, c, d);
                applyNode(2 * node + 1, c, d);
                lazyConst_[node] = 0;
                lazyIdx_[node] = 0;
            }
        }
    }

    long long leafValue(int i) const { return sum_[i + size_]; }

private:
    int n_, size_, H_;
    std::vector<long long> sum_, lazyConst_, lazyIdx_;
    std::vector<long long> length_, sumIdx_;

    void build(int n, const std::vector<long long>* init) {
        n_ = n;
        size_ = 1;
        while (size_ < std::max(n, 1)) size_ *= 2;
        H_ = 0;
        for (int s = size_; s > 1; s >>= 1) H_++;
        sum_.assign(2 * size_, 0);
        lazyConst_.assign(2 * size_, 0);
        lazyIdx_.assign(2 * size_, 0);
        length_.assign(2 * size_, 0);
        sumIdx_.assign(2 * size_, 0);

        for (int i = 0; i < size_; i++) {
            length_[size_ + i] = 1;
            sumIdx_[size_ + i] = i;
        }
        for (int node = size_ - 1; node >= 1; node--) {
            length_[node] = length_[2 * node] + length_[2 * node + 1];
            sumIdx_[node] = sumIdx_[2 * node] + sumIdx_[2 * node + 1];
        }

        if (init) {
            for (int i = 0; i < n_; i++) sum_[size_ + i] = (*init)[i];
            for (int i = size_ - 1; i >= 1; i--) sum_[i] = sum_[2 * i] + sum_[2 * i + 1];
        }
    }

    inline void applyNode(int node, long long constPart, long long idxPart) {
        sum_[node] += constPart * length_[node] + idxPart * sumIdx_[node];
        lazyConst_[node] += constPart;
        lazyIdx_[node] += idxPart;
    }

    inline void pushDown(int node) {
        long long c = lazyConst_[node], d = lazyIdx_[node];
        if (c | d) {
            applyNode(2 * node, c, d);
            applyNode(2 * node + 1, c, d);
            lazyConst_[node] = 0;
            lazyIdx_[node] = 0;
        }
    }

    inline void pushToRoot(int i) {
        for (int s = H_; s > 0; s--) pushDown(i >> s);
    }

    inline void recomputeToRoot(int i) {
        i >>= 1;
        while (i > 0) {
            long long c = lazyConst_[i], d = lazyIdx_[i];
            long long baseSum = sum_[2 * i] + sum_[2 * i + 1];
            sum_[i] = baseSum + c * length_[i] + d * sumIdx_[i];
            i >>= 1;
        }
    }
};