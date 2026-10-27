// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/sets/trie-with-cachedmex-mode/template.cpp
// @operations: add addCount clear count countDistinct countDistinctInValRange countGtX countGteX countInValRange countLtX countLteX countXorGtK countXorGteK countXorLtK countXorLteK firstIndex kth kthXor largestLtX largestLteX largestXorLtK largestXorLteK lastIndex max maxXor maxXorWithVGtM maxXorWithVGteM maxXorWithVInValRange maxXorWithVLtM maxXorWithVLteM medianHigh medianLow mex mexXor min minXor minXorWithVGtM minXorWithVGteM minXorWithVInValRange minXorWithVLtM minXorWithVLteM mode pop popMax popMin remove removeAll removeCount removeInValRange size smallestGtX smallestGteX smallestXorGtK smallestXorGteK
// @data-structure-type: trie
// @values: online-bits
// @keys: numbers
// @tracks: mex mode
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
//   max: log(U)
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
//   min: log(U)
//   minXor: log(U)
//   minXorWithVGtM: log(U)*log(U)
//   minXorWithVGteM: log(U)*log(U)
//   minXorWithVInValRange: log(U)*log(U)
//   minXorWithVLtM: log(U)*log(U)
//   minXorWithVLteM: log(U)*log(U)
//   mode: 1
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
//   build: 1
// @memory:
//   layout: sparse
//   node: c[1*log(U)] p[1*log(U)]
//   tags: none
//   other: children[2*log(U)]
//   note: per add of a new value, one node per bit of its path; U = 2^bits. Each multiset owns its nodes (clear() keeps the arrays' capacity)

// Ordered multiset of integers in [0, 2^bits) as a binary trie: one level per bit, highest bit first; each node keeps
// how many copies, how many distinct values are below it. Besides the usual ordered queries it answers questions
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
    vector<long long> p{0, 0};  // distinct values below
    long long n = 0, d = 0;
    struct Info { T v; long long before, c; };  // a value, copies before it, its copies
    long long mexV = 0;  // the mex, kept current (0 for the empty set)
    map<long long, set<T>> bk;  // mode: count -> the values with that many copies

    // O(1) -- an empty multiset for integers in [0, 2^bits) (bits = 30 holds values up to 1073741823)
    TrieMultiset(int bits) : B(bits), top((1LL << bits) - 1) {}

    int newNode() {  // a new empty node
        ch.push_back({0, 0}), c.push_back(0);
        p.push_back(0);
        return int(c.size()) - 1;
    }

    void clearData() {  // back to just the root (the arrays keep their capacity)
        ch.assign(2, array<int, 2>{0, 0}), c.assign(2, 0);
        p.assign(2, 0);
    }

    long long insert(T x, long long k) {  // k copies of x; returns x's new count
        long long y = (long long)x;
        int t = 1;
        c[1] += k;
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

    Info kthInfo(long long k) const {  // the k-th smallest, copies before it, its copies
        int t = 1;
        long long v = 0, before = 0;
        for (int h = B - 1; h >= 0; h--) {
            int l = ch[t][0];
            if (before + c[l] < k) before += c[l], t = ch[t][1], v |= 1LL << h;
            else t = l;
        }
        return {T(v), before, c[t]};
    }

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

    void addRaw(T x, long long c) {  // c copies of x (c < 0 removes); keeps the mex current
        n += c;
        long long f = insert(x, c);  // x's new count
        long long g = f - c;  // x's old count
        {  // mode: x moves from the bucket of its old count to its new one
            if (g) {
                auto it = bk.find(g);
                it->second.erase(x);
                if (it->second.empty()) bk.erase(it);
            }
            if (f) bk[f].insert(x);
        }
        if (c > 0) {
            if constexpr (is_integral_v<T>) if (x == T(mexV)) mexV = findMex();  // x filled the mex
        } else {
            if constexpr (is_integral_v<T>) if (x >= 0 && x < T(mexV) && !f) mexV = x;  // the last copy of a value below the mex
        }
    }

    void resetCached() {  // nothing counted: as newly built
        mexV = 0;
        bk.clear();
        n = d = 0;
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

    // O(logU) -- largest value; nullopt if empty
    optional<T> max() {
        if (!n) return nullopt;
        return kthAt(n);
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

    // O(logU) -- smallest value; nullopt if empty
    optional<T> min() {
        if (!n) return nullopt;
        return kthAt(1);
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

    // O(1) -- (a most frequent value, its count); nullopt if empty. C++ returns the smallest of the most frequent values
    optional<pair<T, long long>> mode() {
        if (!n) return nullopt;
        auto& [f, vs] = *bk.rbegin();
        return pair<T, long long>{*vs.begin(), f};
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
        T v = kthAt(n);
        addRaw(v, -1);
        return v;
    }

    // O(logU) -- remove and return the smallest value; nullopt if empty
    optional<T> popMin() {
        if (!n) return nullopt;
        T v = kthAt(1);
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
};
