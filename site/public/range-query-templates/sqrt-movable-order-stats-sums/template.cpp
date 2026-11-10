// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries/sqrt-movable-order-stats-sums/template.cpp
#include <bits/stdc++.h>
using namespace std;
using ll = long long;

// @operations: append appendLeft copy countGtX countGteX countInValRange countLtX countLteX countOccurrences cut eraseRange getAll insertAt kthLargest kthSmallest largestLtX largestLteX medianHigh medianLow merge paste pointAdd pointAssign pointGet pop popLeft rangeAdd rangeAssign rangeChmax rangeChmin rangeMax rangeMin rangeReverse rangeRotateLeft rangeRotateRight rangeSum size smallestGtX smallestGteX split sumAbsDiffToMedian sumAbsDiffToX sumGtX sumGteX sumInValRange sumKthLargestRange sumKthSmallestRange sumLargestK sumLtX sumLteX sumSmallestK trisect
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
//   rangeChmax: sqrt(NlogN) amortized
//   rangeChmin: sqrt(NlogN) amortized
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
//   sumAbsDiffToMedian: sqrt(NlogN)*log(U)
//   sumAbsDiffToX: sqrt(NlogN)
//   sumGtX: sqrt(NlogN)
//   sumGteX: sqrt(NlogN)
//   sumInValRange: sqrt(NlogN)
//   sumKthLargestRange: sqrt(NlogN)*log(U)
//   sumKthSmallestRange: sqrt(NlogN)*log(U)
//   sumLargestK: sqrt(NlogN)*log(U)
//   sumLtX: sqrt(NlogN)
//   sumLteX: sqrt(NlogN)
//   sumSmallestK: sqrt(NlogN)*log(U)
//   trisect: sqrt(NlogN) amortized
//   build: N*log(N)
// @memory:
//   layout: none
//   node: vals[1*N] srt[1*N] pos[1*N] pf[1*N]
//   tags: add[1*sqrt(N/logN)] floor[1*sqrt(N/logN)] ceil[1*sqrt(N/logN)] rev[1*sqrt(N/logN)]
//   other: blocks[1*sqrt(N/logN)]
//   note: blocks of about sqrt(N log N) values that move around as whole pieces; each keeps its values, a sorted copy, where each sorted value sits, and prefix sums of the sorted copy, so cutting a block needs no re-sort; U = the largest absolute value (kth binary searches on values)

// Sqrt decomposition with movable blocks, plus sums by value and range chmin / chmax: an array you can insert into
// anywhere, erase a range from, reverse, rotate, range assign / add / chmin / chmax, cut pieces out and paste them
// back in, while asking value questions about any subarray: how many values are < x, in [low, high], equal to x;
// the sum of those values; the k-th smallest, medians, the sum of the k smallest; the nearest value above / below
// x; total distance to x or to the median; sum, min, max. (Without the sums and chmin / chmax, the plain
// sqrt-movable-order-stats template is a bit faster.)
// How: every edit first cuts blocks so the range starts and ends on block edges, then acts on whole blocks with
// tags (reverse flips a flag and reverses the block order; assign / add / chmin / chmax are one pending tag
// "v -> clamp(v + add, floor, ceil)", which never changes the sorted order, so a whole block still answers with
// binary searches and its prefix sums). Neighbors whose sizes add up to at most the block size are merged back once
// there are too many blocks. Queries read partial blocks directly and binary search whole ones.
// All indices 0-based, ranges inclusive [l, r], an index always the position in the CURRENT array.
// T: int, long long (integers: kthSmallest binary searches on values); sums accumulate in S (long long for small T).
template <typename T>
struct SqrtSequence {
    using S = conditional_t<(sizeof(T) < sizeof(long long)), long long, T>;
    static constexpr T INF = numeric_limits<T>::max(), NINF = numeric_limits<T>::lowest();
    struct Block {
        vector<T> vals;   // stored values in block order (backwards while rev), before the tag; empty while assigned
        vector<T> srt;    // the stored values, sorted
        vector<int> pos;  // pos[k] = where srt[k] sits in vals
        vector<S> pf;     // pf[k] = srt[0] + ... + srt[k - 1]
        int sz = 0;
        // each value reads clamp(stored + add, floor, ceil); floor == ceil: assigned
        T add = 0, floor = NINF, ceil = INF;
        bool rev = false;
    };
    vector<Block> blocks;
    int n = 0, B = 1, nAtTidy = 0;
    static constexpr int TIDY = 2;  // tidy once there are more than TIDY * N / blockSize blocks

    SqrtSequence() {}  // (an empty one)

    // O(N log N) -- arr: the initial array
    explicit SqrtSequence(const vector<T>& arr) : n((int)arr.size()) {
        B = targetBlockSize(n), nAtTidy = n;
        for (int i = 0; i < n;
            i += B) blocks.push_back(makeBlock(vector<T>(arr.begin() + i, arr.begin() + min(n, i + B))));
    }

    static int targetBlockSize(int len) { return max(1, (int)(0.7 * sqrt(len * log2(len + 2.0)))); }

    static void buildPf(Block& b) {
        b.pf.resize(b.srt.size() + 1);
        b.pf[0] = 0;
        for (size_t k = 0; k < b.srt.size(); k++) b.pf[k + 1] = b.pf[k] + b.srt[k];
    }

    static Block makeBlock(vector<T> vals) {
        Block b;
        int sz = (int)vals.size();
        b.pos.resize(sz);
        iota(b.pos.begin(), b.pos.end(), 0);
        sort(b.pos.begin(), b.pos.end(),
            [&](int x, int y) { return vals[x] < vals[y] || (vals[x] == vals[y] && x < y); });
        b.srt.resize(sz);
        for (int k = 0; k < sz; k++) b.srt[k] = vals[b.pos[k]];
        b.vals = move(vals);
        b.sz = sz;
        buildPf(b);
        return b;
    }

    static bool assigned(const Block& b) { return b.floor == b.ceil; }

    static T tagged(const Block& b, T v) {
        v += b.add;
        if (v < b.floor) return b.floor;
        if (v > b.ceil) return b.ceil;
        return v;
    }

    // the value at index i of block b (i in the block's current order)
    static T valueAt(const Block& b, int i) {
        if (assigned(b)) return b.floor;
        return tagged(b, b.vals[b.rev ? b.sz - 1 - i : i]);
    }

    // a block that became assigned drops its stored values (its cuts and merges are then O(1))
    static void settle(Block& b) {
        if (!assigned(b)) return;
        b.add = 0;
        b.vals.clear(), b.srt.clear(), b.pos.clear(), b.pf.assign(1, 0);
    }

    // how many values in a whole block are < x / <= x. The tag is monotone: below the floor nothing is < x, above the
    // ceiling everything is, and in between "clamp(v + add) < x" is just "v + add < x"
    static int cntLess(const Block& b, T x) {
        if (x <= b.floor) return 0;
        if (x > b.ceil) return b.sz;
        return int(lower_bound(b.srt.begin(), b.srt.end(), x, [&](T v, T y) { return v + b.add < y; }) - b.srt.begin());
    }
    static int cntLessEq(const Block& b, T x) {
        if (x < b.floor) return 0;
        if (x >= b.ceil) return b.sz;
        return int(upper_bound(b.srt.begin(), b.srt.end(), x, [&](T y, T v) { return y < v + b.add; }) - b.srt.begin());
    }

    // the sum of the k smallest values of a whole block
    static S prefixSum(const Block& b, int k) {
        if (k <= 0) return 0;
        if (assigned(b)) return S(b.floor) * k;
        // lt stored values read as the floor, those from keep on read as the ceiling
        int lt = b.floor == NINF ? 0 : int(lower_bound(b.srt.begin(), b.srt.end(), b.floor,
            [&](T v, T y) { return v + b.add < y; }) - b.srt.begin());
        int keep = b.ceil == INF ? b.sz : int(upper_bound(b.srt.begin(), b.srt.end(), b.ceil,
            [&](T y, T v) { return y < v + b.add; }) - b.srt.begin());
        S res = 0;
        int fl = min(k, lt);
        res += S(b.floor) * fl;  // (fl is 0 when there is no floor)
        int mid = min(k, keep) - lt;
        if (mid > 0) res += b.pf[lt + mid] - b.pf[lt] + S(b.add) * mid;
        int cl = k - max(keep, lt);
        if (cl > 0) res += S(b.ceil) * cl;
        return res;
    }

    // O(blockSize) -- bake the tag and the reversal into the stored values
    static void push(Block& b) {
        int sz = b.sz;
        if (assigned(b)) {
            b.vals.assign(sz, b.floor);
            b.srt.assign(sz, b.floor);
            b.pos.resize(sz);
            iota(b.pos.begin(), b.pos.end(), 0);
            b.add = 0, b.floor = NINF, b.ceil = INF, b.rev = false;
            buildPf(b);
            return;
        }
        if (b.add != 0 || b.floor != NINF || b.ceil != INF) {
            for (T& v : b.vals) v = tagged(b, v);
            for (T& v : b.srt) v = tagged(b, v);  // (the tag is monotone: still sorted)
            b.add = 0, b.floor = NINF, b.ceil = INF;
            buildPf(b);
        }
        if (b.rev) {
            reverse(b.vals.begin(), b.vals.end());
            for (int& p : b.pos) p = sz - 1 - p;
            b.rev = false;
        }
    }

    // O(blockSize) -- block j keeps its first k values, a new block j + 1 gets the rest; both keep the tags (an
    // assigned block is cut in O(1)), and the sorted copy is split by position, so neither half is re-sorted
    void cutBlock(int j, int k) {
        Block right;
        {
            Block& b = blocks[j];
            int sz = b.sz;
            right.sz = sz - k, b.sz = k;
            right.add = b.add, right.floor = b.floor, right.ceil = b.ceil, right.rev = b.rev;
            if (assigned(b)) {
                right.pf.assign(1, 0);
            } else {
                // stored positions [0, cutAt) vs [cutAt, sz); reversed, the high part comes first
                int cutAt = b.rev ? sz - k : k;
                vector<T> lowSrt, highSrt;
                vector<int> lowPos, highPos;
                lowSrt.reserve(cutAt), lowPos.reserve(cutAt), highSrt.reserve(sz - cutAt), highPos.reserve(sz - cutAt);
                for (int t = 0; t < sz; t++) {
                    if (b.pos[t] < cutAt) lowSrt.push_back(b.srt[t]), lowPos.push_back(b.pos[t]);
                    else highSrt.push_back(b.srt[t]), highPos.push_back(b.pos[t] - cutAt);
                }
                vector<T> highVals(b.vals.begin() + cutAt, b.vals.end());
                b.vals.resize(cutAt);
                if (!b.rev) {
                    right.vals = move(highVals), right.srt = move(highSrt), right.pos = move(highPos);
                    b.srt = move(lowSrt), b.pos = move(lowPos);
                } else {
                    right.vals = move(b.vals), right.srt = move(lowSrt), right.pos = move(lowPos);
                    b.vals = move(highVals), b.srt = move(highSrt), b.pos = move(highPos);
                }
                buildPf(b), buildPf(right);
            }
        }
        blocks.insert(blocks.begin() + j + 1, move(right));
    }

    // O(blockSize) -- blocks j and j + 1 become one; the sorted copies are merged, not re-sorted
    void mergeNext(int j) {
        Block& a = blocks[j];
        Block& b = blocks[j + 1];
        if (assigned(a) && assigned(b) && a.floor == b.floor) {  // (same value everywhere: O(1))
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
        a.sz += nb;
        buildPf(a);
        blocks.erase(blocks.begin() + j + 1);
    }

    // after an edit: once there are more than about 2N / blockSize blocks (or the array halved since the last tidy),
    // cut blocks past twice the block size and merge neighbors that fit in one. A tidy walks the blocks once; each
    // merge costs O(blockSize) and removes a block some edit made, so it is paid for by that edit
    void normalize() {
        if ((int)blocks.size() <= TIDY * (n / B) + 8 && 2 * n >= nAtTidy) return;
        B = targetBlockSize(n), nAtTidy = n;
        for (int j = 0; j < (int)blocks.size(); j++) {
            if (blocks[j].sz > 2 * B) cutBlock(j, B);
            while (j + 1 < (int)blocks.size() && blocks[j].sz + blocks[j + 1].sz <= B) mergeNext(j);
        }
    }

    // O(N / blockSize + blockSize) -- the index of the block that starts at position p (cutting one if needed); the
    // number of blocks when p == n
    int splitAt(int p) {
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
    pair<int, int> locate(int i) const {
        int start = 0;
        for (int j = 0;; j++) {
            if (i < start + blocks[j].sz) return {j, i - start};
            start += blocks[j].sz;
        }
    }

    // whole blocks inside [l, r] go to whole(block), the values of partly covered ones to part(value)
    template <class Whole, class Part>
    void visit(int l, int r, const Whole& whole, const Part& part) const {
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

    // applies tag(block) to every block inside [l, r], after cutting so the range starts and ends on block edges
    template <class Tag>
    void rangeTag(int l, int r, const Tag& tag) {
        int a = splitAt(l), b = splitAt(r + 1);
        for (int j = a; j < b; j++) {
            tag(blocks[j]);
            settle(blocks[j]);
        }
        normalize();
    }

    void checkRange(const char* op, int l, int r) const {
        if (l < 0 || l > r || r >= n) throw out_of_range(string(op) + ": needs 0 <= l <= r < size()");
    }

    // O(1) -- the current length of the array
    int size() const { return n; }

    // O(N) -- the whole array
    vector<T> getAll() const {
        vector<T> out;
        out.reserve(n);
        for (const Block& b : blocks)
            for (int i = 0; i < b.sz; i++) out.push_back(valueAt(b, i));
        return out;
    }

    // O(sqrt(N / log N)) -- a[i]; needs 0 <= i < size(), else throws out_of_range
    T pointGet(int i) const {
        if (i < 0 || i >= n) throw out_of_range("pointGet: needs 0 <= i < size()");
        auto [j, o] = locate(i);
        return valueAt(blocks[j], o);
    }

    // O(sqrt(N log N)) -- a[i] = v (overwrite); needs 0 <= i < size(), else throws out_of_range
    void pointAssign(int i, T v) {
        if (i < 0 || i >= n) throw out_of_range("pointAssign: needs 0 <= i < size()");
        auto [j, o] = locate(i);
        Block& b = blocks[j];
        push(b);
        T old = b.vals[o];
        if (old == v) return;
        b.vals[o] = v;
        int t = int(find(b.pos.begin(), b.pos.end(), o) - b.pos.begin());
        b.srt.erase(b.srt.begin() + t), b.pos.erase(b.pos.begin() + t);
        int u = int(upper_bound(b.srt.begin(), b.srt.end(), v) - b.srt.begin());
        b.srt.insert(b.srt.begin() + u, v), b.pos.insert(b.pos.begin() + u, o);
        buildPf(b);
    }

    // O(sqrt(N log N)) -- a[i] += delta; needs 0 <= i < size(), else throws out_of_range
    void pointAdd(int i, T delta) {
        if (i < 0 || i >= n) throw out_of_range("pointAdd: needs 0 <= i < size()");
        pointAssign(i, pointGet(i) + delta);
    }

    // O(sqrt(N log N)) amortized -- insert v so it becomes a[i] (i == size() appends); needs 0 <= i <= size(), else
    // throws out_of_range
    void insertAt(int i, T v) {
        if (i < 0 || i > n) throw out_of_range("insertAt: needs 0 <= i <= size()");
        int j = splitAt(i);
        blocks.insert(blocks.begin() + j, makeBlock({v}));
        n++;
        normalize();
    }

    // O(sqrt(N log N)) amortized -- add v to the end
    void append(T v) { insertAt(n, v); }

    // O(sqrt(N log N)) amortized -- add v to the front (it becomes a[0])
    void appendLeft(T v) { insertAt(0, v); }

    // O(sqrt(N log N)) amortized -- remove a[l..r]; needs 0 <= l <= r < size(), else throws out_of_range
    void eraseRange(int l, int r) {
        checkRange("eraseRange", l, r);
        int a = splitAt(l), b = splitAt(r + 1);
        blocks.erase(blocks.begin() + a, blocks.begin() + b);
        n -= r - l + 1;
        normalize();
    }

    // O(sqrt(N log N)) amortized -- remove and return the last value; needs size() >= 1, else throws out_of_range
    T pop() {
        if (n < 1) throw out_of_range("pop: needs size() >= 1");
        T v = pointGet(n - 1);
        eraseRange(n - 1, n - 1);
        return v;
    }

    // O(sqrt(N log N)) amortized -- remove and return the first value; needs size() >= 1, else throws out_of_range
    T popLeft() {
        if (n < 1) throw out_of_range("popLeft: needs size() >= 1");
        T v = pointGet(0);
        eraseRange(0, 0);
        return v;
    }

    // O(sqrt(N log N)) amortized -- reverse a[l..r]; needs 0 <= l <= r < size(), else throws out_of_range
    void rangeReverse(int l, int r) {
        checkRange("rangeReverse", l, r);
        int a = splitAt(l), b = splitAt(r + 1);
        reverse(blocks.begin() + a, blocks.begin() + b);
        for (int j = a; j < b; j++) blocks[j].rev ^= true;
        normalize();
    }

    // O(sqrt(N log N)) amortized -- cyclic shift a[l..r] left by k (a[l + k] moves to l); k can be huge or negative:
    // it is taken mod the length (negative shifts right); needs 0 <= l <= r < size(), else throws out_of_range
    void rangeRotateLeft(int l, int r, ll k) {
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
    void rangeRotateRight(int l, int r, ll k) {
        checkRange("rangeRotateRight", l, r);
        int len = r - l + 1;
        k %= len;
        rangeRotateLeft(l, r, len - k);
    }

    // O(sqrt(N log N)) amortized -- a[i] = x for i in [l, r]; needs 0 <= l <= r < size(), else throws out_of_range
    void rangeAssign(int l, int r, T x) {
        checkRange("rangeAssign", l, r);
        rangeTag(l, r, [&](Block& b) { b.add = 0, b.floor = b.ceil = x; });
    }

    // O(sqrt(N log N)) amortized -- a[i] += x for i in [l, r]; needs 0 <= l <= r < size(), else throws out_of_range
    void rangeAdd(int l, int r, T x) {
        checkRange("rangeAdd", l, r);
        rangeTag(l, r, [&](Block& b) {
            if (!assigned(b)) b.add += x;
            if (b.floor != NINF) b.floor += x;
            if (b.ceil != INF) b.ceil += x;
        });
    }

    // O(sqrt(N log N)) amortized -- a[i] = min(a[i], x) for i in [l, r]; needs 0 <= l <= r < size(), else throws
    // out_of_range
    void rangeChmin(int l, int r, T x) {
        checkRange("rangeChmin", l, r);
        rangeTag(l, r, [&](Block& b) {
            b.ceil = min(b.ceil, x);    // lower the ceiling
            b.floor = min(b.floor, x);  // and the floor, if the ceiling went below it
        });
    }

    // O(sqrt(N log N)) amortized -- a[i] = max(a[i], x) for i in [l, r]; needs 0 <= l <= r < size(), else throws
    // out_of_range
    void rangeChmax(int l, int r, T x) {
        checkRange("rangeChmax", l, r);
        rangeTag(l, r, [&](Block& b) {
            b.floor = max(b.floor, x);  // raise the floor
            b.ceil = max(b.ceil, x);    // and the ceiling, if the floor went above it
        });
    }

    // O(sqrt(N log N)) -- a[l] + ... + a[r]; needs 0 <= l <= r < size(), else throws out_of_range
    S rangeSum(int l, int r) const {
        checkRange("rangeSum", l, r);
        S res = 0;
        visit(l, r, [&](const Block& b) { res += prefixSum(b, b.sz); }, [&](T v) { res += v; });
        return res;
    }

    // O(sqrt(N log N)) -- min of a[l..r]; needs 0 <= l <= r < size(), else throws out_of_range
    T rangeMin(int l, int r) const {
        checkRange("rangeMin", l, r);
        T res = numeric_limits<T>::max();
        visit(l, r, [&](const Block& b) { res = min(res, assigned(b) ? b.floor : tagged(b, b.srt.front())); },
              [&](T v) { res = min(res, v); });
        return res;
    }

    // O(sqrt(N log N)) -- max of a[l..r]; needs 0 <= l <= r < size(), else throws out_of_range
    T rangeMax(int l, int r) const {
        checkRange("rangeMax", l, r);
        T res = numeric_limits<T>::lowest();
        visit(l, r, [&](const Block& b) { res = max(res, assigned(b) ? b.floor : tagged(b, b.srt.back())); },
              [&](T v) { res = max(res, v); });
        return res;
    }

    // O(sqrt(N log N)) -- how many i in [l, r] have a[i] < x; needs 0 <= l <= r < size(), else throws out_of_range
    int countLtX(int l, int r, T x) const {
        checkRange("countLtX", l, r);
        int res = 0;
        visit(l, r, [&](const Block& b) { res += cntLess(b, x); }, [&](T v) { res += v < x; });
        return res;
    }

    // O(sqrt(N log N)) -- how many i in [l, r] have a[i] <= x; needs 0 <= l <= r < size(), else throws out_of_range
    int countLteX(int l, int r, T x) const {
        checkRange("countLteX", l, r);
        int res = 0;
        visit(l, r, [&](const Block& b) { res += cntLessEq(b, x); }, [&](T v) { res += v <= x; });
        return res;
    }

    // O(sqrt(N log N)) -- how many i in [l, r] have a[i] > x; needs 0 <= l <= r < size(), else throws out_of_range
    int countGtX(int l, int r, T x) const {
        checkRange("countGtX", l, r);
        return r - l + 1 - countLteX(l, r, x);
    }

    // O(sqrt(N log N)) -- how many i in [l, r] have a[i] >= x; needs 0 <= l <= r < size(), else throws out_of_range
    int countGteX(int l, int r, T x) const {
        checkRange("countGteX", l, r);
        return r - l + 1 - countLtX(l, r, x);
    }

    // O(sqrt(N log N)) -- how many i in [l, r] have low <= a[i] <= high (0 when high < low); needs 0 <= l <= r <
    // size(), else throws out_of_range
    int countInValRange(int l, int r, T low, T high) const {
        checkRange("countInValRange", l, r);
        if (high < low) return 0;
        int res = 0;
        visit(l, r, [&](const Block& b) { res += cntLessEq(b, high) - cntLess(b, low); },
              [&](T v) { res += low <= v && v <= high; });
        return res;
    }

    // O(sqrt(N log N)) -- how many i in [l, r] have a[i] == x; needs 0 <= l <= r < size(), else throws out_of_range
    int countOccurrences(int l, int r, T x) const {
        checkRange("countOccurrences", l, r);
        return countInValRange(l, r, x, x);
    }

    // O(sqrt(N log N)) -- smallest value >= x in a[l..r], or nullopt; needs 0 <= l <= r < size(), else throws
    // out_of_range
    optional<T> smallestGteX(int l, int r, T x) const {
        checkRange("smallestGteX", l, r);
        return nearest(l, r, x, true, true);
    }

    // O(sqrt(N log N)) -- smallest value > x in a[l..r], or nullopt; needs 0 <= l <= r < size(), else throws
    // out_of_range
    optional<T> smallestGtX(int l, int r, T x) const {
        checkRange("smallestGtX", l, r);
        return nearest(l, r, x, true, false);
    }

    // O(sqrt(N log N)) -- largest value <= x in a[l..r], or nullopt; needs 0 <= l <= r < size(), else throws
    // out_of_range
    optional<T> largestLteX(int l, int r, T x) const {
        checkRange("largestLteX", l, r);
        return nearest(l, r, x, false, true);
    }

    // O(sqrt(N log N)) -- largest value < x in a[l..r], or nullopt; needs 0 <= l <= r < size(), else throws
    // out_of_range
    optional<T> largestLtX(int l, int r, T x) const {
        checkRange("largestLtX", l, r);
        return nearest(l, r, x, false, false);
    }

    // above: the smallest value above x (or equal, when orEqual); else the largest value below x (or equal)
    optional<T> nearest(int l, int r, T x, bool above, bool orEqual) const {
        optional<T> best;
        auto offer = [&](T v) {
            bool ok = above ? (orEqual ? v >= x : v > x) : (orEqual ? v <= x : v < x);
            if (ok && (!best || (above ? v < *best : v > *best))) best = v;
        };
        visit(l, r, [&](const Block& b) {
            if (assigned(b)) return offer(b.floor);
            int k = (above == orEqual) ? cntLess(b, x) : cntLessEq(b, x);  // values before index k are below the cut
            if (above && k < b.sz) offer(tagged(b, b.srt[k]));
            if (!above && k > 0) offer(tagged(b, b.srt[k - 1]));
        }, offer);
        return best;
    }

    // O(sqrt(N log N) * log(U)) -- the k-th smallest of a[l..r] (k = 1 is the min); needs 0 <= l <= r < size() and
    // 1 <= k <= r - l + 1, else throws out_of_range
    T kthSmallest(int l, int r, int k) const {
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
    T kthLargest(int l, int r, int k) const {
        checkRange("kthLargest", l, r);
        if (k < 1 || k > r - l + 1) throw out_of_range("kthLargest: needs 1 <= k <= r - l + 1");
        return kthSmallest(l, r, r - l + 2 - k);
    }

    // O(sqrt(N log N) * log(U)) -- the lower median of a[l..r] (with an even count, the smaller of the two middle
    // values); needs 0 <= l <= r < size(), else throws out_of_range
    T medianLow(int l, int r) const {
        checkRange("medianLow", l, r);
        return kthSmallest(l, r, (r - l + 2) / 2);
    }

    // O(sqrt(N log N) * log(U)) -- the upper median of a[l..r] (with an even count, the larger of the two middle
    // values); needs 0 <= l <= r < size(), else throws out_of_range
    T medianHigh(int l, int r) const {
        checkRange("medianHigh", l, r);
        return kthSmallest(l, r, (r - l + 1) / 2 + 1);
    }

    // O(sqrt(N log N)) -- the sum of the values < x in a[l..r]; needs 0 <= l <= r < size(), else throws out_of_range
    S sumLtX(int l, int r, T x) const {
        checkRange("sumLtX", l, r);
        S res = 0;
        visit(l, r, [&](const Block& b) { res += prefixSum(b, cntLess(b, x)); }, [&](T v) { if (v < x) res += v; });
        return res;
    }

    // O(sqrt(N log N)) -- the sum of the values <= x in a[l..r]; needs 0 <= l <= r < size(), else throws out_of_range
    S sumLteX(int l, int r, T x) const {
        checkRange("sumLteX", l, r);
        S res = 0;
        visit(l, r, [&](const Block& b) { res += prefixSum(b, cntLessEq(b, x)); }, [&](T v) { if (v <= x) res += v; });
        return res;
    }

    // O(sqrt(N log N)) -- the sum of the values > x in a[l..r]; needs 0 <= l <= r < size(), else throws out_of_range
    S sumGtX(int l, int r, T x) const {
        checkRange("sumGtX", l, r);
        return rangeSum(l, r) - sumLteX(l, r, x);
    }

    // O(sqrt(N log N)) -- the sum of the values >= x in a[l..r]; needs 0 <= l <= r < size(), else throws out_of_range
    S sumGteX(int l, int r, T x) const {
        checkRange("sumGteX", l, r);
        return rangeSum(l, r) - sumLtX(l, r, x);
    }

    // O(sqrt(N log N)) -- the sum of the values in [low, high] in a[l..r] (0 when high < low); needs
    // 0 <= l <= r < size(), else throws out_of_range
    S sumInValRange(int l, int r, T low, T high) const {
        checkRange("sumInValRange", l, r);
        if (high < low) return 0;
        return sumLteX(l, r, high) - sumLtX(l, r, low);
    }

    // O(sqrt(N log N) * log(U)) -- the sum of the k smallest values of a[l..r] (0 when k == 0); needs
    // 0 <= l <= r < size() and 0 <= k <= r - l + 1, else throws out_of_range
    S sumSmallestK(int l, int r, int k) const {
        checkRange("sumSmallestK", l, r);
        if (k < 0 || k > r - l + 1) throw out_of_range("sumSmallestK: needs 0 <= k <= r - l + 1");
        if (k == 0) return 0;
        T t = kthSmallest(l, r, k);  // every value < t is in, and as many copies of t as are left
        return sumLtX(l, r, t) + S(t) * (k - countLtX(l, r, t));
    }

    // O(sqrt(N log N) * log(U)) -- the sum of the k largest values of a[l..r] (0 when k == 0); needs
    // 0 <= l <= r < size() and 0 <= k <= r - l + 1, else throws out_of_range
    S sumLargestK(int l, int r, int k) const {
        checkRange("sumLargestK", l, r);
        if (k < 0 || k > r - l + 1) throw out_of_range("sumLargestK: needs 0 <= k <= r - l + 1");
        return rangeSum(l, r) - sumSmallestK(l, r, r - l + 1 - k);
    }

    // O(sqrt(N log N) * log(U)) -- the sum of the i-th through j-th smallest values of a[l..r] (1-based ranks); needs
    // 0 <= l <= r < size() and 1 <= i <= j <= r - l + 1, else throws out_of_range
    S sumKthSmallestRange(int l, int r, int i, int j) const {
        checkRange("sumKthSmallestRange", l, r);
        if (i < 1 || i > j || j > r - l + 1) throw out_of_range("sumKthSmallestRange: needs 1 <= i <= j <= r - l + 1");
        return sumSmallestK(l, r, j) - sumSmallestK(l, r, i - 1);
    }

    // O(sqrt(N log N) * log(U)) -- the sum of the i-th through j-th largest values of a[l..r] (1-based ranks); needs
    // 0 <= l <= r < size() and 1 <= i <= j <= r - l + 1, else throws out_of_range
    S sumKthLargestRange(int l, int r, int i, int j) const {
        checkRange("sumKthLargestRange", l, r);
        if (i < 1 || i > j || j > r - l + 1) throw out_of_range("sumKthLargestRange: needs 1 <= i <= j <= r - l + 1");
        int len = r - l + 1;
        return sumSmallestK(l, r, len - i + 1) - sumSmallestK(l, r, len - j);
    }

    // O(sqrt(N log N)) -- |a[l] - x| + ... + |a[r] - x|; needs 0 <= l <= r < size(), else throws out_of_range
    S sumAbsDiffToX(int l, int r, T x) const {
        checkRange("sumAbsDiffToX", l, r);
        S below = sumLtX(l, r, x), total = rangeSum(l, r);
        int cnt = countLtX(l, r, x);
        return (S(x) * cnt - below) + (total - below - S(x) * (r - l + 1 - cnt));
    }

    // O(sqrt(N log N) * log(U)) -- the total distance from a[l..r] to its lower median (the smallest total distance
    // to any one value); needs 0 <= l <= r < size(), else throws out_of_range
    S sumAbsDiffToMedian(int l, int r) const {
        checkRange("sumAbsDiffToMedian", l, r);
        return sumAbsDiffToX(l, r, medianLow(l, r));
    }

    // a new SqrtSequence made of these blocks
    static SqrtSequence fromBlocks(vector<Block> bs) {
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
    void paste(int i, SqrtSequence& other) {
        if (i < 0 || i > n) throw out_of_range("paste: needs 0 <= i <= size()");
        int j = splitAt(i);
        blocks.insert(blocks.begin() + j, make_move_iterator(other.blocks.begin()),
            make_move_iterator(other.blocks.end()));
        n += other.n;
        other.blocks.clear(), other.n = 0;
        normalize();
    }

    // O(sqrt(N log N)) amortized -- append all of other at the end; other is left empty
    void merge(SqrtSequence& other) { paste(n, other); }

    // O(sqrt(N log N)) amortized -- (a[0..k-1], a[k..]) as two SqrtSequences of their own; this one is left empty;
    // needs 0 <= k <= size(), else throws out_of_range
    pair<SqrtSequence, SqrtSequence> split(int k) {
        if (k < 0 || k > n) throw out_of_range("split: needs 0 <= k <= size()");
        int j = splitAt(k);
        vector<Block> left(make_move_iterator(blocks.begin()), make_move_iterator(blocks.begin() + j));
        vector<Block> right(make_move_iterator(blocks.begin() + j), make_move_iterator(blocks.end()));
        blocks.clear(), n = 0;
        return {fromBlocks(move(left)), fromBlocks(move(right))};
    }

    // O(sqrt(N log N)) amortized -- (a[0..l-1], a[l..r], a[r+1..]) as three SqrtSequences of their own; this one is
    // left empty; needs 0 <= l <= r < size(), else throws out_of_range
    tuple<SqrtSequence, SqrtSequence, SqrtSequence> trisect(int l, int r) {
        checkRange("trisect", l, r);
        int a = splitAt(l), b = splitAt(r + 1);
        auto it = [&](int j) { return make_move_iterator(blocks.begin() + j); };
        vector<Block> x(it(0), it(a)), y(it(a), it(b)), z(it(b), it((int)blocks.size()));
        blocks.clear(), n = 0;
        return {fromBlocks(move(x)), fromBlocks(move(y)), fromBlocks(move(z))};
    }
};
