// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/sets/trie-with-sums-and-mex-medians-vbound-sumxor/template.cpp
// @operations: add addCount andOfAll andOfGtX andOfGteX andOfInValRange andOfKthLargestRange andOfKthSmallestRange andOfLargestK andOfLtX andOfLteX andOfSmallestK clear count countDistinct countDistinctInValRange countGtX countGteX countInValRange countLtX countLteX countXorGtK countXorGteK countXorLtK countXorLteK firstIndex kth kthXor largestLtX largestLteX largestXorLtK largestXorLteK lastIndex max maxXor maxXorWithVGtM maxXorWithVGteM maxXorWithVInValRange maxXorWithVLtM maxXorWithVLteM medianHigh medianLow mex mexXor min minXor minXorWithVGtM minXorWithVGteM minXorWithVInValRange minXorWithVLtM minXorWithVLteM pop popMax popMin remove removeAll removeCount removeInValRange size smallestGtX smallestGteX smallestXorGtK smallestXorGteK sumAbsDiffToMedian sumAbsDiffToX sumAll sumGtX sumGteX sumInValRange sumKthLargestRange sumKthSmallestRange sumLargestK sumLtX sumLteX sumSmallestK sumXor
// @data-structure-type: trie
// @values: online-bits
// @keys: numbers
// @tracks: vbound sumxor medians
// @complexities:
//   add: log(U)
//   addCount: log(U)
//   andOfAll: 1
//   andOfGtX: log(U)
//   andOfGteX: log(U)
//   andOfInValRange: log(U)
//   andOfKthLargestRange: log(U)
//   andOfKthSmallestRange: log(U)
//   andOfLargestK: log(U)
//   andOfLtX: log(U)
//   andOfLteX: log(U)
//   andOfSmallestK: log(U)
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
//   maxXorWithVGtM: log(U)
//   maxXorWithVGteM: log(U)
//   maxXorWithVInValRange: log(U)
//   maxXorWithVLtM: log(U)
//   maxXorWithVLteM: log(U)
//   medianHigh: 1
//   medianLow: 1
//   mex: log(U)
//   mexXor: log(U)
//   min: 1
//   minXor: log(U)
//   minXorWithVGtM: log(U)
//   minXorWithVGteM: log(U)
//   minXorWithVInValRange: log(U)
//   minXorWithVLtM: log(U)
//   minXorWithVLteM: log(U)
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
//   sumAbsDiffToMedian: 1
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
//   sumXor: log(U)
//   build: 1
// @memory:
//   layout: sparse
//   node: c[1*log(U)] s[1*log(U)] p[1*log(U)] mn[1*log(U)] mx[1*log(U)] and[1*log(U)]
//   tags: none
//   other: children[2*log(U)]
//   note: per add of a new value, one node per bit of its path; U = 2^bits. Each multiset owns its nodes (clear() keeps the arrays' capacity)

// Ordered multiset of integers in [0, 2^bits) as a binary trie: one level per bit, highest bit first; each node keeps
// how many copies, their sum, how many distinct values, the smallest and largest value, their AND are below it. Besides the usual ordered queries it answers questions
// about v ^ x over every value v (max / min / k-th / counts / closest to a bound / limits on v, sum, mex) by walking one bit
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
    vector<long long> mnv{0, 0}, mxv{0, 0};  // smallest / largest value below (meaningful while its count > 0)
    vector<long long> bc;  // bc[h] = copies with bit h set
    vector<T> andv{~T(0), ~T(0)};  // AND of the values below (an empty node's: every bit)
    long long n = 0, d = 0;
    struct Info { T v; long long before, c; S sb; };  // a value, copies before it, its copies, sum before it
    Info low{}, high{};  // both medians, kept current by addRaw while n > 0
    S total = 0;

    // O(1) -- an empty multiset for integers in [0, 2^bits) (bits = 30 holds values up to 1073741823)
    TrieMultiset(int bits) : B(bits), top((1LL << bits) - 1), bc(bits, 0) {}

    int newNode() {  // a new empty node
        ch.push_back({0, 0}), c.push_back(0);
        sm.push_back(0);
        p.push_back(0);
        mnv.push_back(0), mxv.push_back(0);
        andv.push_back(~T(0));
        return int(c.size()) - 1;
    }

    void clearData() {  // back to just the root (the arrays keep their capacity)
        ch.assign(2, array<int, 2>{0, 0}), c.assign(2, 0);
        sm.assign(2, 0);
        p.assign(2, 0);
        mnv.assign(2, 0), mxv.assign(2, 0);
        bc.assign(B, 0);
        andv.assign(2, ~T(0));
    }

    long long insert(T x, long long k) {  // k copies of x; returns x's new count
        long long y = (long long)x;
        int t = 1;
        c[1] += k;
        sm[1] += S(k) * x;
        int path[66], dep = 0;
        path[dep++] = 1;
        for (int h = B - 1; h >= 0; h--) {
            int b = int(y >> h & 1);
            if (b) bc[h] += k;
            if (!ch[t][b]) {
                int u = newNode();
                ch[t][b] = u;
            }
            t = ch[t][b];
            c[t] += k;
            sm[t] += S(k) * x;
            path[dep++] = t;
        }
        long long f = c[t];
        if (!f || f == k) {  // x appeared or disappeared
            d += f ? 1 : -1;
            for (int i = 0; i < dep; i++) p[path[i]] += f ? 1 : -1;
            if (f) mnv[t] = mxv[t] = (long long)x;
            andv[t] = f ? x : ~T(0);
            for (int i = dep - 2; i >= 0; i--) {  // from the bottom: what is present below each node changed
                int u = path[i], l = ch[u][0], r = ch[u][1];
                mnv[u] = c[l] ? mnv[l] : mnv[r];
                mxv[u] = c[r] ? mxv[r] : mxv[l];
                andv[u] = andv[l] & andv[r];
            }
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

    S sumX(long long key) const {  // sum of stored value ^ key over every copy: bit by bit from the per-bit counts
        S res = 0;
        for (int h = 0; h < B; h++) res += S(key >> h & 1 ? n - bc[h] : bc[h]) << h;
        return res;
    }

    optional<T> bestIn(long long x, long long lo, long long hi, bool big) const {  // the largest (big) / smallest v ^ x over the values v in [lo, hi]
        lo = std::max(lo, 0LL), hi = std::min(hi, top);
        if (lo > hi) return nullopt;
        int t = 1, h = B - 1;
        for (; h >= 0 && (lo >> h & 1) == (hi >> h & 1); h--) t = ch[t][lo >> h & 1];  // the bits lo and hi share: one path
        if (!c[t]) return nullopt;
        if (h < 0) return T(lo ^ x);  // lo == hi, present
        // where they split, the left child only needs v >= lo and the right child only v <= hi
        optional<T> a = bestSide(ch[t][0], h - 1, x, lo, true, big), b = bestSide(ch[t][1], h - 1, x, hi, false, big);
        if (!a || !b) return a ? a : b;
        return big ? std::max(*a, *b) : std::min(*a, *b);
    }

    optional<T> bestSide(int t, int h, long long x, long long bound, bool ge, bool big) const {  // best v ^ x below t with v >= bound (ge) / v <= bound
        auto ok = [&](int u) { return c[u] && (ge ? mxv[u] >= bound : mnv[u] <= bound); };
        if (!ok(t)) return nullopt;
        for (; h >= 0; h--) {
            int pb = int(x >> h & 1) ^ int(big);  // the child whose bit of v ^ x is 1 (big) / 0
            t = ok(ch[t][pb]) ? ch[t][pb] : ch[t][pb ^ 1];
        }
        return T(mnv[t] ^ x);
    }

    void addRaw(T x, long long c) {  // c copies of x (c < 0 removes); keeps both medians current
        n += c;
        total += S(c) * x;
        insert(x, c);
        if (c > 0) {
            if (n == c) {  // the set was empty
                low = high = Info{x, 0, c, 0};
                return;
            }
        } else {
            if (!n) return;
        }
        // each median is a tracked rank: shift its (value, copies before, copies, sum before), and search again only
        // when the rank leaves the tracked value
        if (x < low.v) low.before += c, low.sb += S(c) * x;
        else if (x == low.v) low.c += c;
        long long r = (n + 1) / 2;
        if (r <= low.before || r > low.before + low.c) low = kthInfo(r);
        if (x < high.v) high.before += c, high.sb += S(c) * x;
        else if (x == high.v) high.c += c;
        r = n / 2 + 1;
        if (r <= high.before || r > high.before + high.c) high = kthInfo(r);
    }

    S sumFirst(long long k) {  // sum of the k smallest values
        if (k <= 0) return 0;
        Info f = kthInfo(k);
        return f.sb + S(k - f.before) * f.v;
    }

    void resetCached() {  // nothing counted: as newly built
        n = d = 0;
        total = 0;
    }

    T andIn(T ql, T qr) const {  // AND of the values in [ql, qr]
        long long lo = std::max<long long>(ql, 0), hi = std::min<long long>(qr, top);
        if (lo > hi) return ~T(0);
        int t = 1, h = B - 1;
        for (; h >= 0 && (lo >> h & 1) == (hi >> h & 1); h--) t = ch[t][lo >> h & 1];  // the bits lo and hi share: one path
        if (h < 0 || !t) return andv[t];
        T res = ~T(0);
        int u = ch[t][0];  // where they split, the left child only needs v >= lo
        for (int g = h - 1; g >= 0 && u; g--) {
            if (lo >> g & 1) u = ch[u][1];
            else res &= andv[ch[u][1]], u = ch[u][0];
        }
        res &= andv[u];
        u = ch[t][1];  // and the right child only v <= hi
        for (int g = h - 1; g >= 0 && u; g--) {
            if (hi >> g & 1) res &= andv[ch[u][0]], u = ch[u][1];
            else u = ch[u][0];
        }
        return res & andv[u];
    }

    T andLe(T x) const { return andIn(T(0), x); }  // AND of the values <= x
    T andGe(T x) const { return andIn(x, T(top)); }  // AND of the values >= x

    // O(logU) -- add one copy of x
    void add(T x) {
        addRaw(x, 1);
    }

    // O(logU) -- add cnt copies of val (nothing if cnt <= 0)
    void addCount(T val, long long cnt) {
        if (cnt > 0) addRaw(val, cnt);
    }

    // O(1) -- bitwise AND of all values; -1 (every bit set) if empty
    T andOfAll() {
        return andv[1];
    }

    // O(logU) -- bitwise AND of the values > x; -1 (every bit set) if there are none
    T andOfGtX(T x) {
        if (x == numeric_limits<T>::max()) return ~T(0);
        return andGe(x + 1);
    }

    // O(logU) -- bitwise AND of the values >= x; -1 (every bit set) if there are none
    T andOfGteX(T x) {
        return andGe(x);
    }

    // O(logU) -- bitwise AND of the values v with lo <= v <= hi; -1 (every bit set) if there are none
    T andOfInValRange(T lo, T hi) {
        return lo <= hi ? andIn(lo, hi) : ~T(0);
    }

    // O(logU) -- bitwise AND of the kFrom-th..kTo-th largest values (1-indexed, inclusive); throws out_of_range unless 1 <= kFrom <= kTo <= size
    T andOfKthLargestRange(long long kFrom, long long kTo) {
        if (kFrom < 1 || kFrom > kTo || kTo > n) throw out_of_range("andOfKthLargestRange: needs 1 <= kFrom <= kTo <= size");
        T a = kthAt(n - kTo + 1);
        return andIn(a, kthAt(n - kFrom + 1));
    }

    // O(logU) -- bitwise AND of the kFrom-th..kTo-th smallest values (1-indexed, inclusive); throws out_of_range unless 1 <= kFrom <= kTo <= size
    T andOfKthSmallestRange(long long kFrom, long long kTo) {
        if (kFrom < 1 || kFrom > kTo || kTo > n) throw out_of_range("andOfKthSmallestRange: needs 1 <= kFrom <= kTo <= size");
        T a = kthAt(kFrom);
        return andIn(a, kthAt(kTo));
    }

    // O(logU) -- bitwise AND of the k largest values (-1 (every bit set) for k = 0); throws out_of_range unless 0 <= k <= size
    T andOfLargestK(long long k) {
        if (k < 0 || k > n) throw out_of_range("andOfLargestK: needs 0 <= k <= size");
        return k ? andGe(kthAt(n - k + 1)) : ~T(0);
    }

    // O(logU) -- bitwise AND of the values < x; -1 (every bit set) if there are none
    T andOfLtX(T x) {
        if (x == numeric_limits<T>::min()) return ~T(0);
        return andLe(x - 1);
    }

    // O(logU) -- bitwise AND of the values <= x; -1 (every bit set) if there are none
    T andOfLteX(T x) {
        return andLe(x);
    }

    // O(logU) -- bitwise AND of the k smallest values (-1 (every bit set) for k = 0); throws out_of_range unless 0 <= k <= size
    T andOfSmallestK(long long k) {
        if (k < 0 || k > n) throw out_of_range("andOfSmallestK: needs 0 <= k <= size");
        return k ? andLe(kthAt(k)) : ~T(0);
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
        return T(mxv[1]);
    }

    // O(logU) -- largest v ^ x over the values v; nullopt if empty (needs 0 <= x < 2^bits)
    optional<T> maxXor(T x) {
        if (!n) return nullopt;
        return T(extreme(1, B - 1, (long long)x, true));
    }

    // O(logU) -- largest v ^ x over the values v > m; nullopt if there is none
    optional<T> maxXorWithVGtM(T x, long long m) {
        return bestIn(x, m + 1, top, true);
    }

    // O(logU) -- largest v ^ x over the values v >= m; nullopt if there is none
    optional<T> maxXorWithVGteM(T x, long long m) {
        return bestIn(x, m, top, true);
    }

    // O(logU) -- largest v ^ x over the values v with lo <= v <= hi; nullopt if there is none
    optional<T> maxXorWithVInValRange(T x, long long lo, long long hi) {
        return bestIn(x, lo, hi, true);
    }

    // O(logU) -- largest v ^ x over the values v < m; nullopt if there is none
    optional<T> maxXorWithVLtM(T x, long long m) {
        return bestIn(x, 0, m - 1, true);
    }

    // O(logU) -- largest v ^ x over the values v <= m; nullopt if there is none
    optional<T> maxXorWithVLteM(T x, long long m) {
        return bestIn(x, 0, m, true);
    }

    // O(1) -- upper median: the (floor(size/2) + 1)-th smallest value; nullopt if empty
    optional<T> medianHigh() {
        if (!n) return nullopt;
        return high.v;
    }

    // O(1) -- lower median: the ceil(size/2)-th smallest value; nullopt if empty
    optional<T> medianLow() {
        if (!n) return nullopt;
        return low.v;
    }

    // O(logU) -- smallest non-negative integer not in the set
    long long mex() {
        return findMex();
    }

    // O(logU) -- smallest non-negative integer that is not v ^ x for any value v
    long long mexXor(T x) {
        return mexX((long long)x);
    }

    // O(1) -- smallest value; nullopt if empty
    optional<T> min() {
        if (!n) return nullopt;
        return T(mnv[1]);
    }

    // O(logU) -- smallest v ^ x over the values v; nullopt if empty (needs 0 <= x < 2^bits)
    optional<T> minXor(T x) {
        if (!n) return nullopt;
        return T(extreme(1, B - 1, (long long)x, false));
    }

    // O(logU) -- smallest v ^ x over the values v > m; nullopt if there is none
    optional<T> minXorWithVGtM(T x, long long m) {
        return bestIn(x, m + 1, top, false);
    }

    // O(logU) -- smallest v ^ x over the values v >= m; nullopt if there is none
    optional<T> minXorWithVGteM(T x, long long m) {
        return bestIn(x, m, top, false);
    }

    // O(logU) -- smallest v ^ x over the values v with lo <= v <= hi; nullopt if there is none
    optional<T> minXorWithVInValRange(T x, long long lo, long long hi) {
        return bestIn(x, lo, hi, false);
    }

    // O(logU) -- smallest v ^ x over the values v < m; nullopt if there is none
    optional<T> minXorWithVLtM(T x, long long m) {
        return bestIn(x, 0, m - 1, false);
    }

    // O(logU) -- smallest v ^ x over the values v <= m; nullopt if there is none
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
        T v = T(mxv[1]);
        addRaw(v, -1);
        return v;
    }

    // O(logU) -- remove and return the smallest value; nullopt if empty
    optional<T> popMin() {
        if (!n) return nullopt;
        T v = T(mnv[1]);
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

    // O(1) -- sum of |v - medianLow()| over all values (min total moves to make all equal); 0 if empty
    S sumAbsDiffToMedian() {
        if (!n) return 0;
        const Info& m = low;
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

    // O(logU) -- sum of v ^ x over every value v (copies count)
    S sumXor(T x) {
        return sumX((long long)x);
    }
};
