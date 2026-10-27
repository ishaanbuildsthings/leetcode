// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/sets/trie-with-sums-xor-cachedmex-minmax/template.cpp
// @operations: add addCount clear count countDistinct countDistinctInValRange countGtX countGteX countInValRange countLtX countLteX countXorGtK countXorGteK countXorLtK countXorLteK firstIndex kth kthXor largestLtX largestLteX largestXorLtK largestXorLteK lastIndex max maxXor maxXorWithVGtM maxXorWithVGteM maxXorWithVInValRange maxXorWithVLtM maxXorWithVLteM medianHigh medianLow mex mexXor min minXor minXorWithVGtM minXorWithVGteM minXorWithVInValRange minXorWithVLtM minXorWithVLteM pop popMax popMin remove removeAll removeCount removeInValRange size smallestGtX smallestGteX smallestXorGtK smallestXorGteK sumAbsDiffToMedian sumAbsDiffToX sumAll sumGtX sumGteX sumInValRange sumKthLargestRange sumKthSmallestRange sumLargestK sumLtX sumLteX sumSmallestK xorOfAll xorOfGtX xorOfGteX xorOfInValRange xorOfKthLargestRange xorOfKthSmallestRange xorOfLargestK xorOfLtX xorOfLteX xorOfSmallestK
// @data-structure-type: trie
// @values: online-bits
// @keys: numbers
// @tracks: minmax mex
// @complexities:
//   add: log(U)
//   addCount: log(U)
//   clear: 1 amortized
//   count: log(U)
//   countDistinct: 1
//   countDistinctInValRange: log(U)
//   countGtX: log(U)
//   countGteX: log(U)
//   countInValRange: log(U)
//   countLtX: log(U)
//   countLteX: log(U)
//   countXorGtK: log(U)
//   countXorGteK: log(U)
//   countXorLtK: log(U)
//   countXorLteK: log(U)
//   firstIndex: log(U)
//   kth: log(U)
//   kthXor: log(U)
//   largestLtX: log(U)
//   largestLteX: log(U)
//   largestXorLtK: log(U)
//   largestXorLteK: log(U)
//   lastIndex: log(U)
//   max: 1
//   maxXor: log(U)
//   maxXorWithVGtM: log(U)*log(U)
//   maxXorWithVGteM: log(U)*log(U)
//   maxXorWithVInValRange: log(U)*log(U)
//   maxXorWithVLtM: log(U)*log(U)
//   maxXorWithVLteM: log(U)*log(U)
//   medianHigh: log(U)
//   medianLow: log(U)
//   mex: 1
//   mexXor: log(U)
//   min: 1
//   minXor: log(U)
//   minXorWithVGtM: log(U)*log(U)
//   minXorWithVGteM: log(U)*log(U)
//   minXorWithVInValRange: log(U)*log(U)
//   minXorWithVLtM: log(U)*log(U)
//   minXorWithVLteM: log(U)*log(U)
//   pop: log(U)
//   popMax: log(U)
//   popMin: log(U)
//   remove: log(U)
//   removeAll: log(U)
//   removeCount: log(U)
//   removeInValRange: log(U) amortized
//   size: 1
//   smallestGtX: log(U)
//   smallestGteX: log(U)
//   smallestXorGtK: log(U)
//   smallestXorGteK: log(U)
//   sumAbsDiffToMedian: log(U)
//   sumAbsDiffToX: log(U)
//   sumAll: 1
//   sumGtX: log(U)
//   sumGteX: log(U)
//   sumInValRange: log(U)
//   sumKthLargestRange: log(U)
//   sumKthSmallestRange: log(U)
//   sumLargestK: log(U)
//   sumLtX: log(U)
//   sumLteX: log(U)
//   sumSmallestK: log(U)
//   xorOfAll: 1
//   xorOfGtX: log(U)
//   xorOfGteX: log(U)
//   xorOfInValRange: log(U)
//   xorOfKthLargestRange: log(U)
//   xorOfKthSmallestRange: log(U)
//   xorOfLargestK: log(U)
//   xorOfLtX: log(U)
//   xorOfLteX: log(U)
//   xorOfSmallestK: log(U)
//   build: 1
// @memory:
//   layout: sparse
//   node: c[1*log(U)] s[1*log(U)] p[1*log(U)] xor[1*log(U)]
//   tags: none
//   other: children[2*log(U)]
//   note: per add of a new value, one node per bit of its path; U = 2^bits. Each multiset owns its nodes (clear() keeps the arrays' capacity)

// Ordered multiset of integers in [0, 2^bits) as a binary trie: one level per bit, highest bit first; each node keeps
// how many copies, their sum, how many distinct values, their xor are below it. Besides the usual ordered queries it answers questions
// about v ^ x over every value v (max / min / k-th / counts / closest to a bound / limits on v, mex) by walking one bit
// per level, so O(bits) each. Each multiset owns its node arrays (node 0 = empty, node 1 = the root); nodes are never
// removed. T: int, long long, ...; sums in S (long long for small T).
template <typename T>
struct TrieMultiset {
    using S = conditional_t<(sizeof(T) < sizeof(long long)), long long, T>;
    int B;
    long long top;  // the largest value it can hold
    vector<array<int, 2>> ch{{0, 0}, {0, 0}};  // child for bit 0 / bit 1; node 0 = empty, node 1 = the root
    vector<long long> c{0, 0};  // copies below
    vector<S> sm{0, 0};  // sum of the copies below
    vector<long long> p{0, 0};  // distinct values below
    vector<T> xr{0, 0};  // xor of the stored values below with an odd count
    long long n = 0, d = 0;
    struct Info { T v; long long before, c; S sb; };  // a value, copies before it, its copies, sum before it
    T mn{}, mx{};  // kept current by addRaw while n > 0
    long long mexV = 0;  // the mex, kept current (0 for the empty set)
    T xtotal = 0;  // xor of all values (copies count)
    S total = 0;

    // O(1) -- an empty multiset for integers in [0, 2^bits) (bits = 30 holds values up to 1073741823)
    TrieMultiset(int bits) : B(bits), top((1LL << bits) - 1) {}

    int newNode() {  // a new empty node
        ch.push_back({0, 0}), c.push_back(0);
        sm.push_back(0);
        p.push_back(0);
        xr.push_back(0);
        return int(c.size()) - 1;
    }

    void clearData() {  // back to just the root (the arrays keep their capacity)
        ch.assign(2, array<int, 2>{0, 0}), c.assign(2, 0);
        sm.assign(2, 0);
        p.assign(2, 0);
        xr.assign(2, 0);
    }

    long long insert(T x, long long k) {  // k copies of x; returns x's new count
        long long y = (long long)x;
        int t = 1;
        c[1] += k;
        sm[1] += S(k) * x;
        T xv = k & 1 ? T(y) : T(0);  // (with an odd k the stored value flips in or out of each xor on its path)
        xr[1] ^= xv;
        int path[66], dep = 0;
        path[dep++] = 1;
        for (int h = B - 1; h >= 0; h--) {
            int b = int(y >> h & 1);
            if (!ch[t][b]) {
                int u = newNode();
                ch[t][b] = u;
            }
            t = ch[t][b];
            c[t] += k;
            sm[t] += S(k) * x;
            xr[t] ^= xv;
            path[dep++] = t;
        }
        long long f = c[t];
        if (!f || f == k) {  // x appeared or disappeared
            d += f ? 1 : -1;
            for (int i = 0; i < dep; i++) p[path[i]] += f ? 1 : -1;
        }
        return f;
    }

    long long cntLt(long long b, long long key) const {  // copies whose stored value ^ key is < b
        if (b <= 0) return 0;
        if (b > top) return n;
        int t = 1;
        long long res = 0;
        for (int h = B - 1; h >= 0 && t; h--) {
            int kb = int(key >> h & 1);
            if (b >> h & 1) res += c[ch[t][kb]], t = ch[t][kb ^ 1];  // everything below the result-bit-0 child is < b
            else t = ch[t][kb];
        }
        return res;
    }

    long long kthX(long long k, long long key) const {  // the k-th smallest (1-indexed) stored value ^ key
        int t = 1;
        long long res = 0;
        for (int h = B - 1; h >= 0; h--) {
            int kb = int(key >> h & 1), z = ch[t][kb];
            if (k <= c[z]) t = z;
            else k -= c[z], t = ch[t][kb ^ 1], res |= 1LL << h;
        }
        return res;
    }

    long long extreme(int t, int h, long long key, bool big) const {  // bits h..0 of the largest (big) / smallest stored value ^ key below t
        long long res = 0;
        for (; h >= 0; h--) {
            int pb = int(key >> h & 1) ^ int(big);  // the child whose result bit is 1 (big) / 0
            if (c[ch[t][pb]]) {
                t = ch[t][pb];
                if (big) res |= 1LL << h;
            } else {
                t = ch[t][pb ^ 1];
                if (!big) res |= 1LL << h;
            }
        }
        return res;
    }

    long long lt(T x) const { return cntLt((long long)x, 0); }
    long long le(T x) const { return cntLt((long long)x + 1, 0); }

    long long countOf(T x) const {
        if ((long long)x < 0 || (long long)x > top) return 0;
        long long y = (long long)x;
        int t = 1;
        for (int h = B - 1; h >= 0 && t; h--) t = ch[t][y >> h & 1];
        return c[t];
    }

    T kthAt(long long k) const { return T(kthX(k, 0)); }

    Info kthInfo(long long k) const {  // the k-th smallest, copies before it, its copies, sum before it
        int t = 1;
        long long v = 0, before = 0;
        S acc = 0;
        for (int h = B - 1; h >= 0; h--) {
            int l = ch[t][0];
            if (before + c[l] < k) before += c[l], acc += sm[l], t = ch[t][1], v |= 1LL << h;
            else t = l;
        }
        return {T(v), before, c[t], acc};
    }

    S slt(T x) const {  // sum of the values < x
        long long b = (long long)x;
        if (b <= 0) return 0;
        if (b > top) return total;
        int t = 1;
        S res = 0;
        for (int h = B - 1; h >= 0 && t; h--) {
            if (b >> h & 1) res += sm[ch[t][0]], t = ch[t][1];
            else t = ch[t][0];
        }
        return res;
    }

    S sle(T x) const { return slt(T((long long)x + 1)); }

    long long mexX(long long key) const {  // smallest m >= 0 with no value stored as m ^ key
        if (p[1] > top) return top + 1;  // every value is present
        int t = 1;
        long long res = 0;
        for (int h = B - 1; h >= 0 && t; h--) {
            int kb = int(key >> h & 1), z = ch[t][kb];
            if (p[z] == 1LL << h) res |= 1LL << h, t = ch[t][kb ^ 1];  // that half is full: the answer has bit h set
            else t = z;
        }
        return res;
    }

    long long findMex() const { return mexX(0); }

    long long distinctLt(T x) const {  // distinct values < x
        long long b = (long long)x, key = 0;
        if (b <= 0) return 0;
        if (b > top) return d;
        int t = 1;
        long long res = 0;
        for (int h = B - 1; h >= 0 && t; h--) {
            int kb = int(key >> h & 1);
            if (b >> h & 1) res += p[ch[t][kb]], t = ch[t][kb ^ 1];
            else t = ch[t][kb];
        }
        return res;
    }

    optional<T> bestIn(long long x, long long lo, long long hi, bool big) const {  // the largest (big) / smallest v ^ x over the values v in [lo, hi]
        lo = std::max(lo, 0LL), hi = std::min(hi, top);
        if (lo > hi) return nullopt;
        long long mk = 0, key = x ^ mk;  // v ^ x = stored value ^ key
        bool found = false;
        long long best = 0;
        struct Part { int t; long long size, a; };  // a node, how many values it spans, the first of them
        Part st[140];
        int sp = 0;
        st[sp++] = {1, 1LL << B, 0};
        while (sp) {
            auto [t, size, a] = st[--sp];
            if (!c[t] || a > hi || a + size - 1 < lo) continue;
            if (lo <= a && a + size - 1 <= hi) {  // wholly inside: the best of this subtree
                long long v = size == 1 ? a ^ x : ((a ^ x) & -size) | extreme(t, 62 - __builtin_clzll(size), key, big);
                if (!found || (big ? v > best : v < best)) best = v, found = true;
                continue;
            }
            long long half = size >> 1;
            int h = 63 - __builtin_clzll(half), z = int(mk >> h & 1);  // the stored child for v's bit h = 0
            st[sp++] = {ch[t][z], half, a};
            st[sp++] = {ch[t][z ^ 1], half, a + half};
        }
        if (!found) return nullopt;
        return T(best);
    }

    void addRaw(T x, long long c) {  // c copies of x (c < 0 removes); keeps min / max, the mex current
        n += c;
        total += S(c) * x;
        if (c & 1) xtotal ^= x;  // an odd number of copies flips x in or out of the xor of everything
        long long f = insert(x, c);  // x's new count
        if (c > 0) {
            if constexpr (is_integral_v<T>) if (x == T(mexV)) mexV = findMex();  // x filled the mex
            if (n == c) {  // the set was empty
                mn = mx = x;
                return;
            }
            if (x < mn) mn = x;
            if (x > mx) mx = x;
        } else {
            if constexpr (is_integral_v<T>) if (x >= 0 && x < T(mexV) && !f) mexV = x;  // the last copy of a value below the mex
            if (!n) return;
            if (!f) {  // x is gone: it may have been the min / max
                if (x == mn) mn = kthAt(1);
                if (x == mx) mx = kthAt(n);
            }
        }
    }

    S sumFirst(long long k) {  // sum of the k smallest values
        if (k <= 0) return 0;
        Info f = kthInfo(k);
        return f.sb + S(k - f.before) * f.v;
    }

    void resetCached() {  // nothing counted: as newly built
        mexV = 0;
        n = d = 0;
        total = 0;
        xtotal = 0;
    }

    T xlt(T x) const {  // xor of the values < x (copies count)
        long long b = (long long)x;
        if (b <= 0) return 0;
        if (b > top) return xtotal;
        int t = 1;
        T res = 0;
        for (int h = B - 1; h >= 0 && t; h--) {
            if (b >> h & 1) res ^= xr[ch[t][0]], t = ch[t][1];
            else t = ch[t][0];
        }
        return res;
    }

    T xle(T x) const { return xlt(T((long long)x + 1)); }

    T xorFirst(long long k) const {  // xor of the k smallest values (copies count)
        if (k <= 0) return 0;
        int t = 1;
        long long y = 0;  // the stored value of the leaf reached
        T res = 0;
        for (int h = B - 1; h >= 0; h--) {
            int l = ch[t][0];
            if (k <= c[l]) t = l;
            else k -= c[l], res ^= xr[l], t = ch[t][1], y |= 1LL << h;
        }
        if (k & 1) res ^= T(y);  // k copies of the leaf's value left
        return res;
    }

    // O(logU) -- add one copy of x
    void add(T x) {
        addRaw(x, 1);
    }

    // O(logU) -- add cnt copies of val (nothing if cnt <= 0)
    void addCount(T val, long long cnt) {
        if (cnt > 0) addRaw(val, cnt);
    }

    // O(1 amortized) -- remove everything: afterwards it is as if newly built (same constructor arguments), so reuse it instead of building a new one
    void clear() {
        clearData();
        resetCached();
    }

    // O(logU) -- how many copies of x
    long long count(T x) {
        return countOf(x);
    }

    // O(1) -- how many distinct values
    long long countDistinct() {
        return d;
    }

    // O(logU) -- how many distinct values v with lo <= v <= hi (0 if lo > hi)
    long long countDistinctInValRange(T lo, T hi) {
        if (hi < lo) return 0;
        return distinctLt(hi) - distinctLt(lo) + (countOf(hi) ? 1 : 0);
    }

    // O(logU) -- how many values > x
    long long countGtX(T x) {
        return n - le(x);
    }

    // O(logU) -- how many values >= x
    long long countGteX(T x) {
        return n - lt(x);
    }

    // O(logU) -- how many values v with lo <= v <= hi (0 if lo > hi)
    long long countInValRange(T lo, T hi) {
        return lo <= hi ? le(hi) - lt(lo) : 0;
    }

    // O(logU) -- how many values < x
    long long countLtX(T x) {
        return lt(x);
    }

    // O(logU) -- how many values <= x
    long long countLteX(T x) {
        return le(x);
    }

    // O(logU) -- how many values v have v ^ x > k
    long long countXorGtK(T x, long long k) {
        return n - cntLt(k + 1, (long long)x);
    }

    // O(logU) -- how many values v have v ^ x >= k
    long long countXorGteK(T x, long long k) {
        return n - cntLt(k, (long long)x);
    }

    // O(logU) -- how many values v have v ^ x < k
    long long countXorLtK(T x, long long k) {
        return cntLt(k, (long long)x);
    }

    // O(logU) -- how many values v have v ^ x <= k
    long long countXorLteK(T x, long long k) {
        return cntLt(k + 1, (long long)x);
    }

    // O(logU) -- 0-indexed position of the first copy of x in sorted order (= how many values < x); -1 if x is not in the set
    long long firstIndex(T x) {
        return countOf(x) ? lt(x) : -1;
    }

    // O(logU) -- the value at sorted position i (0-indexed: kth(0) is the min); throws out_of_range unless 0 <= i < size
    T kth(long long i) {
        if (i < 0 || i >= n) throw out_of_range("kth: needs 0 <= i < size");
        return kthAt(i + 1);
    }

    // O(logU) -- the i-th smallest v ^ x over the values v (0-indexed, copies count); throws out_of_range unless 0 <= i < size
    T kthXor(T x, long long i) {
        if (i < 0 || i >= n) throw out_of_range("kthXor: needs 0 <= i < size");
        return T(kthX(i + 1, (long long)x));
    }

    // O(logU) -- largest value < x; nullopt if there is none
    optional<T> largestLtX(T x) {
        long long c = lt(x);
        if (!c) return nullopt;
        return kthAt(c);
    }

    // O(logU) -- largest value <= x; nullopt if there is none
    optional<T> largestLteX(T x) {
        long long c = le(x);
        if (!c) return nullopt;
        return kthAt(c);
    }

    // O(logU) -- largest v ^ x that is < k; nullopt if there is none
    optional<T> largestXorLtK(T x, long long k) {
        long long key = (long long)x, c0 = cntLt(k, key);
        if (!c0) return nullopt;
        return T(kthX(c0, key));
    }

    // O(logU) -- largest v ^ x that is <= k; nullopt if there is none
    optional<T> largestXorLteK(T x, long long k) {
        long long key = (long long)x, c0 = cntLt(k + 1, key);
        if (!c0) return nullopt;
        return T(kthX(c0, key));
    }

    // O(logU) -- 0-indexed position of the last copy of x in sorted order (= how many values <= x, minus 1); -1 if x is not in the set
    long long lastIndex(T x) {
        return countOf(x) ? le(x) - 1 : -1;
    }

    // O(1) -- largest value; nullopt if empty
    optional<T> max() {
        if (!n) return nullopt;
        return mx;
    }

    // O(logU) -- largest v ^ x over the values v; nullopt if empty (needs 0 <= x < 2^bits)
    optional<T> maxXor(T x) {
        if (!n) return nullopt;
        return T(extreme(1, B - 1, (long long)x, true));
    }

    // O(logU logU) -- largest v ^ x over the values v > m; nullopt if there is none
    optional<T> maxXorWithVGtM(T x, long long m) {
        return bestIn(x, m + 1, top, true);
    }

    // O(logU logU) -- largest v ^ x over the values v >= m; nullopt if there is none
    optional<T> maxXorWithVGteM(T x, long long m) {
        return bestIn(x, m, top, true);
    }

    // O(logU logU) -- largest v ^ x over the values v with lo <= v <= hi; nullopt if there is none
    optional<T> maxXorWithVInValRange(T x, long long lo, long long hi) {
        return bestIn(x, lo, hi, true);
    }

    // O(logU logU) -- largest v ^ x over the values v < m; nullopt if there is none
    optional<T> maxXorWithVLtM(T x, long long m) {
        return bestIn(x, 0, m - 1, true);
    }

    // O(logU logU) -- largest v ^ x over the values v <= m; nullopt if there is none
    optional<T> maxXorWithVLteM(T x, long long m) {
        return bestIn(x, 0, m, true);
    }

    // O(logU) -- upper median: the (floor(size/2) + 1)-th smallest value; nullopt if empty
    optional<T> medianHigh() {
        if (!n) return nullopt;
        return kthAt(n / 2 + 1);
    }

    // O(logU) -- lower median: the ceil(size/2)-th smallest value; nullopt if empty
    optional<T> medianLow() {
        if (!n) return nullopt;
        return kthAt((n + 1) / 2);
    }

    // O(1) -- smallest non-negative integer not in the set
    long long mex() {
        return mexV;
    }

    // O(logU) -- smallest non-negative integer that is not v ^ x for any value v
    long long mexXor(T x) {
        return mexX((long long)x);
    }

    // O(1) -- smallest value; nullopt if empty
    optional<T> min() {
        if (!n) return nullopt;
        return mn;
    }

    // O(logU) -- smallest v ^ x over the values v; nullopt if empty (needs 0 <= x < 2^bits)
    optional<T> minXor(T x) {
        if (!n) return nullopt;
        return T(extreme(1, B - 1, (long long)x, false));
    }

    // O(logU logU) -- smallest v ^ x over the values v > m; nullopt if there is none
    optional<T> minXorWithVGtM(T x, long long m) {
        return bestIn(x, m + 1, top, false);
    }

    // O(logU logU) -- smallest v ^ x over the values v >= m; nullopt if there is none
    optional<T> minXorWithVGteM(T x, long long m) {
        return bestIn(x, m, top, false);
    }

    // O(logU logU) -- smallest v ^ x over the values v with lo <= v <= hi; nullopt if there is none
    optional<T> minXorWithVInValRange(T x, long long lo, long long hi) {
        return bestIn(x, lo, hi, false);
    }

    // O(logU logU) -- smallest v ^ x over the values v < m; nullopt if there is none
    optional<T> minXorWithVLtM(T x, long long m) {
        return bestIn(x, 0, m - 1, false);
    }

    // O(logU logU) -- smallest v ^ x over the values v <= m; nullopt if there is none
    optional<T> minXorWithVLteM(T x, long long m) {
        return bestIn(x, 0, m, false);
    }

    // O(logU) -- remove and return the value at sorted position i (0-indexed: pop(0) is popMin()); throws out_of_range unless 0 <= i < size
    T pop(long long i) {
        if (i < 0 || i >= n) throw out_of_range("pop: needs 0 <= i < size");
        T v = kthAt(i + 1);
        addRaw(v, -1);
        return v;
    }

    // O(logU) -- remove and return the largest value; nullopt if empty
    optional<T> popMax() {
        if (!n) return nullopt;
        T v = mx;
        addRaw(v, -1);
        return v;
    }

    // O(logU) -- remove and return the smallest value; nullopt if empty
    optional<T> popMin() {
        if (!n) return nullopt;
        T v = mn;
        addRaw(v, -1);
        return v;
    }

    // O(logU) -- remove one copy of x if present; returns how many were removed (0 or 1)
    long long remove(T x) {
        if (!count(x)) return 0;
        addRaw(x, -1);
        return 1;
    }

    // O(logU) -- remove every copy of val; returns how many were removed
    long long removeAll(T val) {
        long long k = count(val);
        if (k) addRaw(val, -k);
        return k;
    }

    // O(logU) -- remove min(cnt, count(val)) copies of val; returns how many were removed
    long long removeCount(T val, long long cnt) {
        long long k = std::min(cnt, count(val));
        if (k <= 0) return 0;
        addRaw(val, -k);
        return k;
    }

    // O(logU amortized) -- remove every value v with lo <= v <= hi; returns how many copies were removed (0 if lo > hi)
    long long removeInValRange(T lo, T hi) {
        if (hi < lo) return 0;
        long long removed = 0;
        while (n) {  // the smallest value >= lo, while it is <= hi: drop all its copies
            long long c = lt(lo);
            if (c == n) break;
            T v = kthAt(c + 1);
            if (hi < v) break;
            long long k = countOf(v);
            addRaw(v, -k), removed += k;
        }
        return removed;
    }

    // O(1) -- how many values (copies count)
    long long size() {
        return n;
    }

    // O(logU) -- smallest value > x; nullopt if there is none
    optional<T> smallestGtX(T x) {
        long long c = le(x);
        if (c == n) return nullopt;
        return kthAt(c + 1);
    }

    // O(logU) -- smallest value >= x; nullopt if there is none
    optional<T> smallestGteX(T x) {
        long long c = lt(x);
        if (c == n) return nullopt;
        return kthAt(c + 1);
    }

    // O(logU) -- smallest v ^ x that is > k; nullopt if there is none
    optional<T> smallestXorGtK(T x, long long k) {
        long long key = (long long)x, c0 = cntLt(k + 1, key);
        if (c0 == n) return nullopt;
        return T(kthX(c0 + 1, key));
    }

    // O(logU) -- smallest v ^ x that is >= k; nullopt if there is none
    optional<T> smallestXorGteK(T x, long long k) {
        long long key = (long long)x, c0 = cntLt(k, key);
        if (c0 == n) return nullopt;
        return T(kthX(c0 + 1, key));
    }

    // O(logU) -- sum of |v - medianLow()| over all values (min total moves to make all equal); 0 if empty
    S sumAbsDiffToMedian() {
        if (!n) return 0;
        Info m = kthInfo((n + 1) / 2);
        return S(m.v) * m.before - m.sb + (total - m.sb - S(m.v) * m.c) - S(m.v) * (n - m.before - m.c);
    }

    // O(logU) -- sum of |v - x| over all values
    S sumAbsDiffToX(T x) {
        long long c = lt(x);
        S s = slt(x);
        return S(x) * c - s + (total - s) - S(x) * (n - c);
    }

    // O(1) -- sum of all values
    S sumAll() {
        return total;
    }

    // O(logU) -- sum of the values > x
    S sumGtX(T x) {
        return total - sle(x);
    }

    // O(logU) -- sum of the values >= x
    S sumGteX(T x) {
        return total - slt(x);
    }

    // O(logU) -- sum of the values v with lo <= v <= hi (0 if lo > hi)
    S sumInValRange(T lo, T hi) {
        return lo <= hi ? sle(hi) - slt(lo) : S(0);
    }

    // O(logU) -- sum of the kFrom-th..kTo-th largest values (1-indexed, inclusive; (5, 8) = 5th..8th biggest); throws out_of_range unless 1 <= kFrom <= kTo <= size
    S sumKthLargestRange(long long kFrom, long long kTo) {
        if (kFrom < 1 || kFrom > kTo || kTo > n) throw out_of_range("sumKthLargestRange: needs 1 <= kFrom <= kTo <= size");
        return sumFirst(n - kFrom + 1) - sumFirst(n - kTo);
    }

    // O(logU) -- sum of the kFrom-th..kTo-th smallest values (1-indexed, inclusive); throws out_of_range unless 1 <= kFrom <= kTo <= size
    S sumKthSmallestRange(long long kFrom, long long kTo) {
        if (kFrom < 1 || kFrom > kTo || kTo > n) throw out_of_range("sumKthSmallestRange: needs 1 <= kFrom <= kTo <= size");
        return sumFirst(kTo) - sumFirst(kFrom - 1);
    }

    // O(logU) -- sum of the k largest values; throws out_of_range unless 0 <= k <= size
    S sumLargestK(long long k) {
        if (k < 0 || k > n) throw out_of_range("sumLargestK: needs 0 <= k <= size");
        return total - sumFirst(n - k);
    }

    // O(logU) -- sum of the values < x
    S sumLtX(T x) {
        return slt(x);
    }

    // O(logU) -- sum of the values <= x
    S sumLteX(T x) {
        return sle(x);
    }

    // O(logU) -- sum of the k smallest values; throws out_of_range unless 0 <= k <= size
    S sumSmallestK(long long k) {
        if (k < 0 || k > n) throw out_of_range("sumSmallestK: needs 0 <= k <= size");
        return sumFirst(k);
    }

    // O(1) -- xor of all values (copies count: a value with an even count cancels out); 0 if empty
    T xorOfAll() {
        return xtotal;
    }

    // O(logU) -- xor of the values > x (copies count)
    T xorOfGtX(T x) {
        return xtotal ^ xle(x);
    }

    // O(logU) -- xor of the values >= x (copies count)
    T xorOfGteX(T x) {
        return xtotal ^ xlt(x);
    }

    // O(logU) -- xor of the values v with lo <= v <= hi (copies count; 0 if lo > hi)
    T xorOfInValRange(T lo, T hi) {
        return lo <= hi ? T(xle(hi) ^ xlt(lo)) : T(0);
    }

    // O(logU) -- xor of the kFrom-th..kTo-th largest values (1-indexed, inclusive); throws out_of_range unless 1 <= kFrom <= kTo <= size
    T xorOfKthLargestRange(long long kFrom, long long kTo) {
        if (kFrom < 1 || kFrom > kTo || kTo > n) throw out_of_range("xorOfKthLargestRange: needs 1 <= kFrom <= kTo <= size");
        return xorFirst(n - kFrom + 1) ^ xorFirst(n - kTo);
    }

    // O(logU) -- xor of the kFrom-th..kTo-th smallest values (1-indexed, inclusive); throws out_of_range unless 1 <= kFrom <= kTo <= size
    T xorOfKthSmallestRange(long long kFrom, long long kTo) {
        if (kFrom < 1 || kFrom > kTo || kTo > n) throw out_of_range("xorOfKthSmallestRange: needs 1 <= kFrom <= kTo <= size");
        return xorFirst(kTo) ^ xorFirst(kFrom - 1);
    }

    // O(logU) -- xor of the k largest values (copies count); throws out_of_range unless 0 <= k <= size
    T xorOfLargestK(long long k) {
        if (k < 0 || k > n) throw out_of_range("xorOfLargestK: needs 0 <= k <= size");
        return xtotal ^ xorFirst(n - k);
    }

    // O(logU) -- xor of the values < x (copies count)
    T xorOfLtX(T x) {
        return xlt(x);
    }

    // O(logU) -- xor of the values <= x (copies count)
    T xorOfLteX(T x) {
        return xle(x);
    }

    // O(logU) -- xor of the k smallest values (copies count); throws out_of_range unless 0 <= k <= size
    T xorOfSmallestK(long long k) {
        if (k < 0 || k > n) throw out_of_range("xorOfSmallestK: needs 0 <= k <= size");
        return xorFirst(k);
    }
};
