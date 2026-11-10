// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries/sqrt-movable-order-stats/fast.cpp
#include <bits/stdc++.h>
using namespace std;
using ll = long long;

// @operations: append appendLeft copy countGtX countGteX countInValRange countLtX countLteX countOccurrences cut eraseRange getAll insertAt kthLargest kthSmallest largestLtX largestLteX medianHigh medianLow merge paste pointAdd pointAssign pointGet pop popLeft rangeAdd rangeAssign rangeMax rangeMin rangeReverse rangeRotateLeft rangeRotateRight rangeSum size smallestGtX smallestGteX split trisect
// @data-structure-type: sqrt
// @complexities:
//   append: sqrt(NlogN) amortized
//   appendLeft: sqrt(NlogN) amortized
//   copy: K+sqrt(NlogN)
//   countGtX: sqrt(NlogN)
//   countGteX: sqrt(NlogN)
//   countInValRange: sqrt(NlogN)
//   countLtX: sqrt(NlogN)
//   countLteX: sqrt(NlogN)
//   countOccurrences: sqrt(NlogN)
//   cut: sqrt(NlogN) amortized
//   eraseRange: sqrt(NlogN) amortized
//   getAll: N
//   insertAt: sqrt(NlogN) amortized
//   kthLargest: sqrt(NlogN)*log(U)
//   kthSmallest: sqrt(NlogN)*log(U)
//   largestLtX: sqrt(NlogN)
//   largestLteX: sqrt(NlogN)
//   medianHigh: sqrt(NlogN)*log(U)
//   medianLow: sqrt(NlogN)*log(U)
//   merge: sqrt(NlogN) amortized
//   paste: sqrt(NlogN) amortized
//   pointAdd: sqrt(NlogN)
//   pointAssign: sqrt(NlogN)
//   pointGet: sqrt(N/logN)
//   pop: sqrt(NlogN) amortized
//   popLeft: sqrt(NlogN) amortized
//   rangeAdd: sqrt(NlogN) amortized
//   rangeAssign: sqrt(NlogN) amortized
//   rangeMax: sqrt(NlogN)
//   rangeMin: sqrt(NlogN)
//   rangeReverse: sqrt(NlogN) amortized
//   rangeRotateLeft: sqrt(NlogN) amortized
//   rangeRotateRight: sqrt(NlogN) amortized
//   rangeSum: sqrt(NlogN)
//   size: 1
//   smallestGtX: sqrt(NlogN)
//   smallestGteX: sqrt(NlogN)
//   split: sqrt(NlogN) amortized
//   trisect: sqrt(NlogN) amortized
//   build: N*log(N)
// @memory:
//   layout: none
//   node: vals[1*N] srt[1*N] pos[1*N]
//   tags: add[1*sqrt(N/logN)] asg[1*sqrt(N/logN)] rev[1*sqrt(N/logN)]
//   other: blocks[1*sqrt(N/logN)]
//   note: blocks of about sqrt(N log N) values that move around as whole pieces; each keeps its values, a sorted copy, and where each sorted value sits, so cutting a block needs no re-sort; U = the largest absolute value (kth binary searches on values)

// Sqrt decomposition with movable blocks: an array you can insert into anywhere, erase a range from, reverse, rotate,
// range assign and range add, while asking value questions about any subarray (how many are < x, in [low, high],
// equal to x; the k-th smallest, medians; the nearest value above / below x; sum, min, max), and cut pieces out and
// paste them back in, into this array or any other. A treap can do the moving but
// not these counts; a merge sort tree can do the counts but not the moving.
// How: every edit first cuts blocks so the range starts and ends on block edges, then acts on whole blocks with
// tags (reverse just flips a flag and reverses the block order, assign / add are pending tags). Afterwards
// neighbors whose sizes add up to at most the block size are merged back, so there are never more than about
// 2N / blockSize blocks. Queries read partial blocks directly and binary search whole ones.
// All indices 0-based, ranges inclusive [l, r], an index always the position in the CURRENT array.
// T: int, long long (integers: kthSmallest binary searches on values); sums accumulate in S (long long for small T).
// FAST MODE drawbacks compared with template.cpp:
//   - sanitizers are skipped inside this template, so a bad access in it goes unreported
// Same public operations and answers, same limits; it needs GCC or Clang and C++17.
#ifdef __SSE2__
#include <immintrin.h>
#endif

// LEETCODE_NO_SANITIZE skips sanitizers in a function. It only changes anything where sanitizers run, like LeetCode: on
// Codeforces it compiles and does nothing.
// This template already uses it. To go further, put it on the one function with your hot loop:
//   LEETCODE_NO_SANITIZE long long maxSum(vector<int>& nums, int k) {
// A lambda needs its own: [&](int x) LEETCODE_NO_SANITIZE { ... }. It does not carry into anything that function calls.
// Inside a marked function use raw pointers and plain comparisons, not vector[] and min / max, or it can get slower.
// Bad memory accesses in a marked function go unreported.
#ifndef LEETCODE_NO_SANITIZE
#define LEETCODE_NO_SANITIZE __attribute__((no_sanitize("address"), no_sanitize("undefined")))
#endif
#define LEETCODE_NO_SANITIZE_INLINE LEETCODE_NO_SANITIZE __attribute__((always_inline)) inline

// A vector whose [] and size() always inline, even with sanitizers skipped (libstdc++ only; elsewhere a plain vector)
template <typename U>
struct HotVector : vector<U> {
    using vector<U>::vector;
    HotVector() = default;
    HotVector(const vector<U>& other) : vector<U>(other) {}
    HotVector(vector<U>&& other) : vector<U>(move(other)) {}
#ifdef __GLIBCXX__
    LEETCODE_NO_SANITIZE_INLINE typename vector<U>::reference operator[](size_t i) { return this->_M_impl._M_start[i]; }
    LEETCODE_NO_SANITIZE_INLINE typename vector<U>::const_reference operator[](size_t i) const {
        return this->_M_impl._M_start[i];
    }
    LEETCODE_NO_SANITIZE_INLINE size_t size() const { return size_t(this->_M_impl._M_finish - this->_M_impl._M_start); }
#endif
};

template <typename T>
struct SqrtSequence {
    using S = conditional_t<(sizeof(T) < sizeof(long long)), long long, T>;
    struct Block {
        vector<T> vals;   // stored values in block order (backwards while rev), before the tag; empty while assigned
        vector<T> srt;    // the stored values, sorted
        vector<int> pos;  // pos[k] = where srt[k] sits in vals
        int sz = 0;
        S sum = 0;        // sum of the stored values
        T add = 0;        // each value reads stored + add ...
        T asg = 0;        // ... or asg, while assigned
        bool assigned = false, rev = false;
    };
    HotVector<Block> blocks;
    int n = 0, B = 1, nAtTidy = 0;
    static constexpr int TIDY = 2;  // tidy once there are more than TIDY * N / blockSize blocks

    SqrtSequence() {}  // (an empty one)

    // O(N log N) -- arr: the initial array
    explicit SqrtSequence(const vector<T>& arr) : n((int)arr.size()) {
        B = targetBlockSize(n), nAtTidy = n;
        for (int i = 0; i < n;
            i += B) blocks.push_back(makeBlock(vector<T>(arr.begin() + i, arr.begin() + min(n, i + B))));
    }

    LEETCODE_NO_SANITIZE static int targetBlockSize(int len) {
        return max(1, (int)(0.7 * sqrt(len * log2(len + 2.0))));
    }

    LEETCODE_NO_SANITIZE static Block makeBlock(vector<T> vals) {
        Block b;
        int sz = (int)vals.size();
        b.pos.resize(sz);
        iota(b.pos.begin(), b.pos.end(), 0);
        sort(b.pos.begin(), b.pos.end(),
            [&](int x, int y) { return vals[x] < vals[y] || (vals[x] == vals[y] && x < y); });
        b.srt.resize(sz);
        for (int k = 0; k < sz; k++) b.srt[k] = vals[b.pos[k]], b.sum += vals[b.pos[k]];
        b.vals = move(vals);
        b.sz = sz;
        return b;
    }

    // the value at index i of block b (i in the block's current order)
    LEETCODE_NO_SANITIZE static T valueAt(const Block& b, int i) {
        if (b.assigned) return b.asg;
        return b.vals[b.rev ? b.sz - 1 - i : i] + b.add;
    }

    LEETCODE_NO_SANITIZE static S blockSum(const Block& b) {
        return b.assigned ? S(b.asg) * b.sz : b.sum + S(b.add) * b.sz;
    }

    // how many values in a whole block are < x / <= x
    LEETCODE_NO_SANITIZE static int cntLess(const Block& b, T x) {
        if (b.assigned) return b.asg < x ? b.sz : 0;
        return int(lower_bound(b.srt.begin(), b.srt.end(), x, [&](T v, T y) { return v + b.add < y; }) - b.srt.begin());
    }
    LEETCODE_NO_SANITIZE static int cntLessEq(const Block& b, T x) {
        if (b.assigned) return b.asg <= x ? b.sz : 0;
        return int(upper_bound(b.srt.begin(), b.srt.end(), x, [&](T y, T v) { return y < v + b.add; }) - b.srt.begin());
    }

    // O(blockSize) -- bake the tag and the reversal into the stored values
    LEETCODE_NO_SANITIZE static void push(Block& b) {
        int sz = b.sz;
        if (b.assigned) {
            b.vals.assign(sz, b.asg);
            b.srt.assign(sz, b.asg);
            b.pos.resize(sz);
            iota(b.pos.begin(), b.pos.end(), 0);
            b.sum = S(b.asg) * sz;
            b.assigned = false, b.add = 0, b.rev = false;
            return;
        }
        if (b.add != 0) {
            for (T& v : b.vals) v += b.add;
            for (T& v : b.srt) v += b.add;
            b.sum += S(b.add) * sz;
            b.add = 0;
        }
        if (b.rev) {
            reverse(b.vals.begin(), b.vals.end());
            for (int& p : b.pos) p = sz - 1 - p;
            b.rev = false;
        }
    }

    // O(blockSize) -- block j keeps its first k values, a new block j + 1 gets the rest; both keep the tags (an
    // assigned block is cut in O(1)), and the sorted copy is split by position, so neither half is re-sorted
    LEETCODE_NO_SANITIZE void cutBlock(int j, int k) {
        Block right;
        {
            Block& b = blocks[j];
            int sz = b.sz;
            right.sz = sz - k, b.sz = k;
            right.add = b.add, right.asg = b.asg, right.assigned = b.assigned, right.rev = b.rev;
            if (!b.assigned) {
                // stored positions [0, cutAt) vs [cutAt, sz); reversed, the high part comes first
                int cutAt = b.rev ? sz - k : k;
                vector<T> lowSrt, highSrt;
                vector<int> lowPos, highPos;
                lowSrt.reserve(cutAt), lowPos.reserve(cutAt), highSrt.reserve(sz - cutAt), highPos.reserve(sz - cutAt);
                S lowSum = 0;
                for (int t = 0; t < sz; t++) {
                    if (b.pos[t] < cutAt) {
                        lowSrt.push_back(b.srt[t]), lowPos.push_back(b.pos[t]);
                        lowSum += b.srt[t];
                    } else {
                        highSrt.push_back(b.srt[t]), highPos.push_back(b.pos[t] - cutAt);
                    }
                }
                vector<T> highVals(b.vals.begin() + cutAt, b.vals.end());
                b.vals.resize(cutAt);
                S highSum = b.sum - lowSum;
                if (!b.rev) {
                    right.vals = move(highVals), right.srt = move(highSrt), right.pos = move(highPos),
                        right.sum = highSum;
                    b.srt = move(lowSrt), b.pos = move(lowPos), b.sum = lowSum;
                } else {
                    right.vals = move(b.vals), right.srt = move(lowSrt), right.pos = move(lowPos), right.sum = lowSum;
                    b.vals = move(highVals), b.srt = move(highSrt), b.pos = move(highPos), b.sum = highSum;
                }
            }
        }
        blocks.insert(blocks.begin() + j + 1, move(right));
    }

    // O(blockSize) -- blocks j and j + 1 become one; the sorted copies are merged, not re-sorted
    LEETCODE_NO_SANITIZE void mergeNext(int j) {
        Block& a = blocks[j];
        Block& b = blocks[j + 1];
        if (a.assigned && b.assigned && a.asg == b.asg) {  // (same value everywhere: O(1))
            a.sz += b.sz;
            blocks.erase(blocks.begin() + j + 1);
            return;
        }
        push(a), push(b);
        int na = a.sz, nb = b.sz;
        vector<T> srt(na + nb);
        vector<int> pos(na + nb);
        for (int x = 0, y = 0, t = 0; t < na + nb; t++) {
            if (y == nb || (x < na && !(b.srt[y] < a.srt[x]))) srt[t] = a.srt[x], pos[t] = a.pos[x++];
            else srt[t] = b.srt[y], pos[t] = b.pos[y++] + na;
        }
        a.vals.insert(a.vals.end(), b.vals.begin(), b.vals.end());
        a.srt = move(srt), a.pos = move(pos);
        a.sum += b.sum, a.sz += nb;
        blocks.erase(blocks.begin() + j + 1);
    }

    // after an edit: once there are more than about 2N / blockSize blocks (or the array halved since the last tidy),
    // cut blocks past twice the block size and merge neighbors that fit in one. A tidy walks the blocks once; each
    // merge costs O(blockSize) and removes a block some edit made, so it is paid for by that edit
    LEETCODE_NO_SANITIZE void normalize() {
        if ((int)blocks.size() <= TIDY * (n / B) + 8 && 2 * n >= nAtTidy) return;
        B = targetBlockSize(n), nAtTidy = n;
        for (int j = 0; j < (int)blocks.size(); j++) {
            if (blocks[j].sz > 2 * B) cutBlock(j, B);
            while (j + 1 < (int)blocks.size() && blocks[j].sz + blocks[j + 1].sz <= B) mergeNext(j);
        }
    }

    // O(N / blockSize + blockSize) -- the index of the block that starts at position p (cutting one if needed); the
    // number of blocks when p == n
    LEETCODE_NO_SANITIZE int splitAt(int p) {
        int start = 0;
        for (int j = 0; j < (int)blocks.size(); j++) {
            int sz = blocks[j].sz;
            if (p == start) return j;
            if (p < start + sz) {
                cutBlock(j, p - start);
                return j + 1;
            }
            start += sz;
        }
        return (int)blocks.size();
    }

    // the block holding index i, and i's place inside it
    LEETCODE_NO_SANITIZE pair<int, int> locate(int i) const {
        int start = 0;
        for (int j = 0;; j++) {
            if (i < start + blocks[j].sz) return {j, i - start};
            start += blocks[j].sz;
        }
    }

    // whole blocks inside [l, r] go to whole(block), the values of partly covered ones to part(value)
    template <class Whole, class Part>
    LEETCODE_NO_SANITIZE void visit(int l, int r, const Whole& whole, const Part& part) const {
        int start = 0;
        for (const Block& b : blocks) {
            int end = start + b.sz - 1;
            if (start > r) break;
            if (end >= l) {
                if (l <= start && end <= r) whole(b);
                else for (int i = max(l, start); i <= min(r, end); i++) part(valueAt(b, i - start));
            }
            start = end + 1;
        }
    }

    LEETCODE_NO_SANITIZE void checkRange(const char* op, int l, int r) const {
        if (l < 0 || l > r || r >= n) throw out_of_range(string(op) + ": needs 0 <= l <= r < size()");
    }

    // O(1) -- the current length of the array
    LEETCODE_NO_SANITIZE int size() const { return n; }

    // O(N) -- the whole array
    LEETCODE_NO_SANITIZE vector<T> getAll() const {
        vector<T> out;
        out.reserve(n);
        for (const Block& b : blocks)
            for (int i = 0; i < b.sz; i++) out.push_back(valueAt(b, i));
        return out;
    }

    // O(sqrt(N / log N)) -- a[i]; needs 0 <= i < size(), else throws out_of_range
    LEETCODE_NO_SANITIZE T pointGet(int i) const {
        if (i < 0 || i >= n) throw out_of_range("pointGet: needs 0 <= i < size()");
        auto [j, o] = locate(i);
        return valueAt(blocks[j], o);
    }

    // O(sqrt(N log N)) -- a[i] = v (overwrite); needs 0 <= i < size(), else throws out_of_range
    LEETCODE_NO_SANITIZE void pointAssign(int i, T v) {
        if (i < 0 || i >= n) throw out_of_range("pointAssign: needs 0 <= i < size()");
        auto [j, o] = locate(i);
        Block& b = blocks[j];
        push(b);
        T old = b.vals[o];
        if (old == v) return;
        b.vals[o] = v;
        b.sum += S(v) - S(old);
        int t = int(find(b.pos.begin(), b.pos.end(), o) - b.pos.begin());
        b.srt.erase(b.srt.begin() + t), b.pos.erase(b.pos.begin() + t);
        int u = int(upper_bound(b.srt.begin(), b.srt.end(), v) - b.srt.begin());
        b.srt.insert(b.srt.begin() + u, v), b.pos.insert(b.pos.begin() + u, o);
    }

    // O(sqrt(N log N)) -- a[i] += delta; needs 0 <= i < size(), else throws out_of_range
    LEETCODE_NO_SANITIZE void pointAdd(int i, T delta) {
        if (i < 0 || i >= n) throw out_of_range("pointAdd: needs 0 <= i < size()");
        pointAssign(i, pointGet(i) + delta);
    }

    // O(sqrt(N log N)) amortized -- insert v so it becomes a[i] (i == size() appends); needs 0 <= i <= size(), else
    // throws out_of_range
    LEETCODE_NO_SANITIZE void insertAt(int i, T v) {
        if (i < 0 || i > n) throw out_of_range("insertAt: needs 0 <= i <= size()");
        int j = splitAt(i);
        blocks.insert(blocks.begin() + j, makeBlock({v}));
        n++;
        normalize();
    }

    // O(sqrt(N log N)) amortized -- add v to the end
    LEETCODE_NO_SANITIZE void append(T v) { insertAt(n, v); }

    // O(sqrt(N log N)) amortized -- add v to the front (it becomes a[0])
    LEETCODE_NO_SANITIZE void appendLeft(T v) { insertAt(0, v); }

    // O(sqrt(N log N)) amortized -- remove a[l..r]; needs 0 <= l <= r < size(), else throws out_of_range
    LEETCODE_NO_SANITIZE void eraseRange(int l, int r) {
        checkRange("eraseRange", l, r);
        int a = splitAt(l), b = splitAt(r + 1);
        blocks.erase(blocks.begin() + a, blocks.begin() + b);
        n -= r - l + 1;
        normalize();
    }

    // O(sqrt(N log N)) amortized -- remove and return the last value; needs size() >= 1, else throws out_of_range
    LEETCODE_NO_SANITIZE T pop() {
        if (n < 1) throw out_of_range("pop: needs size() >= 1");
        T v = pointGet(n - 1);
        eraseRange(n - 1, n - 1);
        return v;
    }

    // O(sqrt(N log N)) amortized -- remove and return the first value; needs size() >= 1, else throws out_of_range
    LEETCODE_NO_SANITIZE T popLeft() {
        if (n < 1) throw out_of_range("popLeft: needs size() >= 1");
        T v = pointGet(0);
        eraseRange(0, 0);
        return v;
    }

    // O(sqrt(N log N)) amortized -- reverse a[l..r]; needs 0 <= l <= r < size(), else throws out_of_range
    LEETCODE_NO_SANITIZE void rangeReverse(int l, int r) {
        checkRange("rangeReverse", l, r);
        int a = splitAt(l), b = splitAt(r + 1);
        reverse(blocks.begin() + a, blocks.begin() + b);
        for (int j = a; j < b; j++) blocks[j].rev ^= true;
        normalize();
    }

    // O(sqrt(N log N)) amortized -- cyclic shift a[l..r] left by k (a[l + k] moves to l); k can be huge or negative:
    // it is taken mod the length (negative shifts right); needs 0 <= l <= r < size(), else throws out_of_range
    LEETCODE_NO_SANITIZE void rangeRotateLeft(int l, int r, ll k) {
        checkRange("rangeRotateLeft", l, r);
        int len = r - l + 1;
        k %= len;
        if (k < 0) k += len;
        if (k == 0) return;
        int a = splitAt(l), m = splitAt(l + (int)k), b = splitAt(r + 1);
        rotate(blocks.begin() + a, blocks.begin() + m, blocks.begin() + b);
        normalize();
    }

    // O(sqrt(N log N)) amortized -- cyclic shift a[l..r] right by k; k can be huge or negative: it is taken mod the
    // length (negative shifts left); needs 0 <= l <= r < size(), else throws out_of_range
    LEETCODE_NO_SANITIZE void rangeRotateRight(int l, int r, ll k) {
        checkRange("rangeRotateRight", l, r);
        int len = r - l + 1;
        k %= len;
        rangeRotateLeft(l, r, len - k);
    }

    // O(sqrt(N log N)) amortized -- a[i] = x for i in [l, r]; needs 0 <= l <= r < size(), else throws out_of_range
    LEETCODE_NO_SANITIZE void rangeAssign(int l, int r, T x) {
        checkRange("rangeAssign", l, r);
        int a = splitAt(l), b = splitAt(r + 1);
        for (int j = a; j < b; j++) {
            Block& blk = blocks[j];
            blk.assigned = true, blk.asg = x, blk.add = 0;
            blk.vals.clear(), blk.srt.clear(), blk.pos.clear();
        }
        normalize();
    }

    // O(sqrt(N log N)) amortized -- a[i] += x for i in [l, r]; needs 0 <= l <= r < size(), else throws out_of_range
    LEETCODE_NO_SANITIZE void rangeAdd(int l, int r, T x) {
        checkRange("rangeAdd", l, r);
        int a = splitAt(l), b = splitAt(r + 1);
        for (int j = a; j < b; j++) {
            if (blocks[j].assigned) blocks[j].asg += x;
            else blocks[j].add += x;
        }
        normalize();
    }

    // O(sqrt(N log N)) -- a[l] + ... + a[r]; needs 0 <= l <= r < size(), else throws out_of_range
    LEETCODE_NO_SANITIZE S rangeSum(int l, int r) const {
        checkRange("rangeSum", l, r);
        S res = 0;
        visit(l, r, [&](const Block& b) { res += blockSum(b); }, [&](T v) { res += v; });
        return res;
    }

    // O(sqrt(N log N)) -- min of a[l..r]; needs 0 <= l <= r < size(), else throws out_of_range
    LEETCODE_NO_SANITIZE T rangeMin(int l, int r) const {
        checkRange("rangeMin", l, r);
        T res = numeric_limits<T>::max();
        visit(l, r, [&](const Block& b) { res = min(res, b.assigned ? b.asg : T(b.srt.front() + b.add)); },
              [&](T v) { res = min(res, v); });
        return res;
    }

    // O(sqrt(N log N)) -- max of a[l..r]; needs 0 <= l <= r < size(), else throws out_of_range
    LEETCODE_NO_SANITIZE T rangeMax(int l, int r) const {
        checkRange("rangeMax", l, r);
        T res = numeric_limits<T>::lowest();
        visit(l, r, [&](const Block& b) { res = max(res, b.assigned ? b.asg : T(b.srt.back() + b.add)); },
              [&](T v) { res = max(res, v); });
        return res;
    }

    // O(sqrt(N log N)) -- how many i in [l, r] have a[i] < x; needs 0 <= l <= r < size(), else throws out_of_range
    LEETCODE_NO_SANITIZE int countLtX(int l, int r, T x) const {
        checkRange("countLtX", l, r);
        int res = 0;
        visit(l, r, [&](const Block& b) { res += cntLess(b, x); }, [&](T v) { res += v < x; });
        return res;
    }

    // O(sqrt(N log N)) -- how many i in [l, r] have a[i] <= x; needs 0 <= l <= r < size(), else throws out_of_range
    LEETCODE_NO_SANITIZE int countLteX(int l, int r, T x) const {
        checkRange("countLteX", l, r);
        int res = 0;
        visit(l, r, [&](const Block& b) { res += cntLessEq(b, x); }, [&](T v) { res += v <= x; });
        return res;
    }

    // O(sqrt(N log N)) -- how many i in [l, r] have a[i] > x; needs 0 <= l <= r < size(), else throws out_of_range
    LEETCODE_NO_SANITIZE int countGtX(int l, int r, T x) const {
        checkRange("countGtX", l, r);
        return r - l + 1 - countLteX(l, r, x);
    }

    // O(sqrt(N log N)) -- how many i in [l, r] have a[i] >= x; needs 0 <= l <= r < size(), else throws out_of_range
    LEETCODE_NO_SANITIZE int countGteX(int l, int r, T x) const {
        checkRange("countGteX", l, r);
        return r - l + 1 - countLtX(l, r, x);
    }

    // O(sqrt(N log N)) -- how many i in [l, r] have low <= a[i] <= high (0 when high < low); needs 0 <= l <= r <
    // size(), else throws out_of_range
    LEETCODE_NO_SANITIZE int countInValRange(int l, int r, T low, T high) const {
        checkRange("countInValRange", l, r);
        if (high < low) return 0;
        int res = 0;
        visit(l, r, [&](const Block& b) { res += cntLessEq(b, high) - cntLess(b, low); },
              [&](T v) { res += low <= v && v <= high; });
        return res;
    }

    // O(sqrt(N log N)) -- how many i in [l, r] have a[i] == x; needs 0 <= l <= r < size(), else throws out_of_range
    LEETCODE_NO_SANITIZE int countOccurrences(int l, int r, T x) const {
        checkRange("countOccurrences", l, r);
        return countInValRange(l, r, x, x);
    }

    // O(sqrt(N log N)) -- smallest value >= x in a[l..r], or nullopt; needs 0 <= l <= r < size(), else throws
    // out_of_range
    LEETCODE_NO_SANITIZE optional<T> smallestGteX(int l, int r, T x) const {
        checkRange("smallestGteX", l, r);
        return nearest(l, r, x, true, true);
    }

    // O(sqrt(N log N)) -- smallest value > x in a[l..r], or nullopt; needs 0 <= l <= r < size(), else throws
    // out_of_range
    LEETCODE_NO_SANITIZE optional<T> smallestGtX(int l, int r, T x) const {
        checkRange("smallestGtX", l, r);
        return nearest(l, r, x, true, false);
    }

    // O(sqrt(N log N)) -- largest value <= x in a[l..r], or nullopt; needs 0 <= l <= r < size(), else throws
    // out_of_range
    LEETCODE_NO_SANITIZE optional<T> largestLteX(int l, int r, T x) const {
        checkRange("largestLteX", l, r);
        return nearest(l, r, x, false, true);
    }

    // O(sqrt(N log N)) -- largest value < x in a[l..r], or nullopt; needs 0 <= l <= r < size(), else throws
    // out_of_range
    LEETCODE_NO_SANITIZE optional<T> largestLtX(int l, int r, T x) const {
        checkRange("largestLtX", l, r);
        return nearest(l, r, x, false, false);
    }

    // above: the smallest value above x (or equal, when orEqual); else the largest value below x (or equal)
    LEETCODE_NO_SANITIZE optional<T> nearest(int l, int r, T x, bool above, bool orEqual) const {
        optional<T> best;
        auto offer = [&](T v) {
            bool ok = above ? (orEqual ? v >= x : v > x) : (orEqual ? v <= x : v < x);
            if (ok && (!best || (above ? v < *best : v > *best))) best = v;
        };
        visit(l, r, [&](const Block& b) {
            if (b.assigned) return offer(b.asg);
            int k = (above == orEqual) ? cntLess(b, x) : cntLessEq(b, x);  // values before index k are below the cut
            if (above && k < b.sz) offer(b.srt[k] + b.add);
            if (!above && k > 0) offer(b.srt[k - 1] + b.add);
        }, offer);
        return best;
    }

    // O(sqrt(N log N) * log(U)) -- the k-th smallest of a[l..r] (k = 1 is the min); needs 0 <= l <= r < size() and
    // 1 <= k <= r - l + 1, else throws out_of_range
    LEETCODE_NO_SANITIZE T kthSmallest(int l, int r, int k) const {
        checkRange("kthSmallest", l, r);
        if (k < 1 || k > r - l + 1) throw out_of_range("kthSmallest: needs 1 <= k <= r - l + 1");
        vector<const Block*> whole;
        vector<T> part;
        visit(l, r, [&](const Block& b) { whole.push_back(&b); }, [&](T v) { part.push_back(v); });
        sort(part.begin(), part.end());
        T lo = rangeMin(l, r), hi = rangeMax(l, r);
        using UT = make_unsigned_t<T>;
        while (lo < hi) {  // the smallest value with at least k values <= it
            T mid = T(lo + T((UT(hi) - UT(lo)) / 2));
            int cnt = int(upper_bound(part.begin(), part.end(), mid) - part.begin());
            for (const Block* b : whole) cnt += cntLessEq(*b, mid);
            if (cnt >= k) hi = mid;
            else lo = mid + 1;
        }
        return lo;
    }

    // O(sqrt(N log N) * log(U)) -- the k-th largest of a[l..r] (k = 1 is the max); needs 0 <= l <= r < size() and
    // 1 <= k <= r - l + 1, else throws out_of_range
    LEETCODE_NO_SANITIZE T kthLargest(int l, int r, int k) const {
        checkRange("kthLargest", l, r);
        if (k < 1 || k > r - l + 1) throw out_of_range("kthLargest: needs 1 <= k <= r - l + 1");
        return kthSmallest(l, r, r - l + 2 - k);
    }

    // O(sqrt(N log N) * log(U)) -- the lower median of a[l..r] (with an even count, the smaller of the two middle
    // values); needs 0 <= l <= r < size(), else throws out_of_range
    LEETCODE_NO_SANITIZE T medianLow(int l, int r) const {
        checkRange("medianLow", l, r);
        return kthSmallest(l, r, (r - l + 2) / 2);
    }

    // O(sqrt(N log N) * log(U)) -- the upper median of a[l..r] (with an even count, the larger of the two middle
    // values); needs 0 <= l <= r < size(), else throws out_of_range
    LEETCODE_NO_SANITIZE T medianHigh(int l, int r) const {
        checkRange("medianHigh", l, r);
        return kthSmallest(l, r, (r - l + 1) / 2 + 1);
    }

    // a new SqrtSequence made of these blocks
    LEETCODE_NO_SANITIZE static SqrtSequence fromBlocks(vector<Block> bs) {
        SqrtSequence s;
        for (const Block& b : bs) s.n += b.sz;
        s.blocks = move(bs);
        s.B = targetBlockSize(s.n), s.nAtTidy = s.n;
        s.normalize();
        return s;
    }

    // O(sqrt(N log N)) amortized -- remove a[l..r] and return it as a SqrtSequence of its own (indices from 0);
    // needs 0 <= l <= r < size(), else throws out_of_range
    SqrtSequence cut(int l, int r) {
        checkRange("cut", l, r);
        int a = splitAt(l), b = splitAt(r + 1);
        vector<Block> piece(make_move_iterator(blocks.begin() + a), make_move_iterator(blocks.begin() + b));
        blocks.erase(blocks.begin() + a, blocks.begin() + b);
        n -= r - l + 1;
        normalize();
        return fromBlocks(move(piece));
    }

    // O(N) -- the whole array as a SqrtSequence of its own; this one is unchanged
    SqrtSequence copy() const { return *this; }

    // O(r - l + 1 + sqrt(N log N)) -- a[l..r] as a SqrtSequence of its own; this one is unchanged; needs
    // 0 <= l <= r < size(), else throws out_of_range
    SqrtSequence copy(int l, int r) {
        checkRange("copy", l, r);
        int a = splitAt(l), b = splitAt(r + 1);
        vector<Block> piece(blocks.begin() + a, blocks.begin() + b);
        normalize();
        return fromBlocks(move(piece));
    }

    // O(sqrt(N log N)) amortized -- insert all of other (any SqrtSequence, e.g. a cut piece) so it starts at a[i];
    // other is left empty; needs 0 <= i <= size(), else throws out_of_range
    LEETCODE_NO_SANITIZE void paste(int i, SqrtSequence& other) {
        if (i < 0 || i > n) throw out_of_range("paste: needs 0 <= i <= size()");
        int j = splitAt(i);
        blocks.insert(blocks.begin() + j, make_move_iterator(other.blocks.begin()),
            make_move_iterator(other.blocks.end()));
        n += other.n;
        other.blocks.clear(), other.n = 0;
        normalize();
    }

    // O(sqrt(N log N)) amortized -- append all of other at the end; other is left empty
    LEETCODE_NO_SANITIZE void merge(SqrtSequence& other) { paste(n, other); }

    // O(sqrt(N log N)) amortized -- (a[0..k-1], a[k..]) as two SqrtSequences of their own; this one is left empty;
    // needs 0 <= k <= size(), else throws out_of_range
    LEETCODE_NO_SANITIZE pair<SqrtSequence, SqrtSequence> split(int k) {
        if (k < 0 || k > n) throw out_of_range("split: needs 0 <= k <= size()");
        int j = splitAt(k);
        vector<Block> left(make_move_iterator(blocks.begin()), make_move_iterator(blocks.begin() + j));
        vector<Block> right(make_move_iterator(blocks.begin() + j), make_move_iterator(blocks.end()));
        blocks.clear(), n = 0;
        return {fromBlocks(move(left)), fromBlocks(move(right))};
    }

    // O(sqrt(N log N)) amortized -- (a[0..l-1], a[l..r], a[r+1..]) as three SqrtSequences of their own; this one is
    // left empty; needs 0 <= l <= r < size(), else throws out_of_range
    LEETCODE_NO_SANITIZE tuple<SqrtSequence, SqrtSequence, SqrtSequence> trisect(int l, int r) {
        checkRange("trisect", l, r);
        int a = splitAt(l), b = splitAt(r + 1);
        auto it = [&](int j) { return make_move_iterator(blocks.begin() + j); };
        vector<Block> x(it(0), it(a)), y(it(a), it(b)), z(it(b), it((int)blocks.size()));
        blocks.clear(), n = 0;
        return {fromBlocks(move(x)), fromBlocks(move(y)), fromBlocks(move(z))};
    }
};
