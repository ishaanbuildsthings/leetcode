// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/sets/fastset/template.cpp
// @operations: add addCount clear count countDistinct largestLtX largestLteX max min popMax popMin remove removeAll removeCount size smallestGtX smallestGteX
// @data-structure-type: fastset
// @values: online-range
// @keys: numbers
// @complexities:
//   add: log64(U)
//   addCount: log64(U)
//   clear: N*log64(U)
//   count: 1
//   countDistinct: 1
//   largestLtX: log64(U)
//   largestLteX: log64(U)
//   max: 1 amortized
//   min: 1 amortized
//   popMax: log64(U)
//   popMin: log64(U)
//   remove: log64(U)
//   removeAll: log64(U)
//   removeCount: log64(U)
//   size: 1
//   smallestGtX: log64(U)
//   smallestGteX: log64(U)
//   build: U
// @memory:
//   layout: none
//   node: cnt[1*U]
//   tags: none
//   other: none
//   note: U = hi - lo + 1: a count per value, plus the trie's U / 64 + U / 4096 + ... 64-bit words (about U / 63)

// Ordered multiset of integers in [lo, hi] (FastSet): a 64-ary bit trie over the U = hi - lo + 1 slots, a bit meaning
// "this value (or something under this word) is present", plus a count per value. add / remove / smallest >= x /
// largest <= x touch one word per level: log_64(U) levels, about 4 for U = 10^7. It keeps no ranks, so no k-th and
// no "how many below x". T: int, long long, ...
template <typename T>
struct FastSetMultiset {
    long long lo, hi;
    int u;
    vector<vector<unsigned long long>> seg;  // seg[h][w] = 64 bits, one per word of level h - 1 (level 0: one per value)
    vector<long long> cnt;                   // copies of lo + i
    long long n = 0, d = 0;
    struct Info { T v; long long before, c; };  // a value, copies before it, its copies
    T mn{}, mx{};  // kept current by addRaw once min() / max() has been called (mm)
    bool mm = false;
    bool med = false;  // medians (low, high) are tracked from the first median query on
    Info low{}, high{};

    // O(U) -- lo, hi: every value added lies in [lo, hi] (any integers, negative is fine); U = hi - lo + 1
    FastSetMultiset(long long lo, long long hi) : lo(lo), hi(hi), u(int(hi - lo + 1)), cnt(u) {
        for (int width = std::max(u, 1);;) {  // (std::: the struct's own max() hides it)
            int words = (width + 63) >> 6;
            seg.emplace_back(words, 0);
            if (words == 1) break;
            width = words;
        }
    }

    void insert(T x, long long c) {
        int i = int((long long)x - lo);  // x must lie in [lo, hi]
        long long old = cnt[i];
        cnt[i] += c;
        if (!old) {  // first copy: set its bit on every level
            d++;
            for (auto& level : seg) level[i >> 6] |= 1ULL << (i & 63), i >>= 6;
        } else if (!cnt[i]) {  // last copy: clear bits upward while the word empties
            d--;
            for (auto& level : seg) {
                int j = i >> 6;
                if (level[j] &= ~(1ULL << (i & 63))) break;
                i = j;
            }
        }
    }

    long long countOf(T x) const { return (long long)x >= lo && (long long)x <= hi ? cnt[(long long)x - lo] : 0; }

    long long next(long long i) const {  // smallest present slot >= i, or -1
        if (i < 0) i = 0;
        if (i >= u) return -1;
        for (int h = 0; h < (int)seg.size(); h++) {
            long long idx = i >> 6;
            if (idx >= (long long)seg[h].size()) break;
            unsigned long long v = seg[h][idx] >> (i & 63);
            if (v) {
                i += __builtin_ctzll(v);
                for (int g = h - 1; g >= 0; g--) i = (i << 6) + __builtin_ctzll(seg[g][i]);
                return i;
            }
            i = idx + 1;
        }
        return -1;
    }

    long long prev(long long i) const {  // largest present slot <= i, or -1
        if (i >= u) i = u - 1;
        if (i < 0) return -1;
        for (int h = 0; h < (int)seg.size(); h++) {
            long long idx = i >> 6;
            unsigned long long v = seg[h][idx] & (~0ULL >> (63 - (i & 63)));
            if (v) {
                i = (idx << 6) + 63 - __builtin_clzll(v);
                for (int g = h - 1; g >= 0; g--) i = (i << 6) + 63 - __builtin_clzll(seg[g][i]);
                return i;
            }
            if (!idx) return -1;
            i = idx - 1;
        }
        return -1;
    }

    T kthAt(long long k) const { return T(lo + (k == 1 ? next(0) : prev(u - 1))); }  // only the min (k = 1) or the max (k = n): no ranks

    Info kthInfo(long long k) const { return {kthAt(k), 0, 0}; }  // never called: this structure has no median ops

    void addRaw(T x, long long c) {  // c copies of x (c < 0 removes); keeps min / max, medians, mex current once asked for
        n += c;
        insert(x, c);
        if (c > 0) {
            if (n == c) {  // the set was empty
                if (mm) mn = mx = x;
                if (med) low = high = Info{x, 0, c};
                return;
            }
            if (mm) {
                if (x < mn) mn = x;
                if (x > mx) mx = x;
            }
        } else {
            if (!n) return;
            if (mm) {
                if (x == mn) mn = kthAt(1);
                if (x == mx) mx = kthAt(n);
            }
        }
        if (!med) return;
        // each median is a tracked rank: shift its (value, copies before, copies), and search again only
        // when the rank leaves the tracked value
        if (x < low.v) low.before += c;
        else if (x == low.v) low.c += c;
        long long r = (n + 1) / 2;
        if (r <= low.before || r > low.before + low.c) low = kthInfo(r);
        if (x < high.v) high.before += c;
        else if (x == high.v) high.c += c;
        r = n / 2 + 1;
        if (r <= high.before || r > high.before + high.c) high = kthInfo(r);
    }

    void startMinMax() {  // the first min() / max() (n > 0): from now on addRaw keeps both current
        mm = true;
        mn = kthAt(1), mx = kthAt(n);
    }

    void startMedians() {  // the first median query (n > 0): from now on addRaw keeps both medians current
        med = true;
        low = kthInfo((n + 1) / 2), high = kthInfo(n / 2 + 1);
    }

    void resetCached() {  // nothing counted, nothing tracked: as newly built
        mm = med = false;
        n = d = 0;
    }

    void clearData() {  // zero only the trie words in use (walking down from the top through set bits)
        vector<pair<int, int>> st{{(int)seg.size() - 1, 0}};
        while (!st.empty()) {
            auto [h, w] = st.back();
            st.pop_back();
            unsigned long long bits = seg[h][w];
            if (!bits) continue;
            seg[h][w] = 0;
            int base = w << 6;
            for (; bits; bits &= bits - 1) {
                int b = __builtin_ctzll(bits);
                if (h) st.push_back({h - 1, base + b});
                else cnt[base + b] = 0;
            }
        }
    }

    // O(log64(U)) -- add one copy of x
    void add(T x) {
        addRaw(x, 1);
    }

    // O(log64(U)) -- add cnt copies of val (nothing if cnt <= 0)
    void addCount(T val, long long cnt) {
        if (cnt > 0) addRaw(val, cnt);
    }

    // O(N log64(U)) -- remove everything: afterwards it is as if newly built (same constructor arguments), so reuse it instead of building a new one
    void clear() {
        clearData();
        resetCached();
    }

    // O(1) -- how many copies of x
    long long count(T x) {
        return countOf(x);
    }

    // O(1) -- how many distinct values
    long long countDistinct() {
        return d;
    }

    // O(log64(U)) -- largest value < x; nullopt if there is none
    optional<T> largestLtX(T x) {
        long long i = prev((long long)x - lo - 1);
        if (i < 0) return nullopt;
        return T(lo + i);
    }

    // O(log64(U)) -- largest value <= x; nullopt if there is none
    optional<T> largestLteX(T x) {
        long long i = prev((long long)x - lo);
        if (i < 0) return nullopt;
        return T(lo + i);
    }

    // O(1 amortized) -- largest value; nullopt if empty
    optional<T> max() {
        if (!n) return nullopt;
        if (!mm) startMinMax();
        return mx;
    }

    // O(1 amortized) -- smallest value; nullopt if empty
    optional<T> min() {
        if (!n) return nullopt;
        if (!mm) startMinMax();
        return mn;
    }

    // O(log64(U)) -- remove and return the largest value; nullopt if empty
    optional<T> popMax() {
        if (!n) return nullopt;
        T v = mm ? mx : kthAt(n);
        addRaw(v, -1);
        return v;
    }

    // O(log64(U)) -- remove and return the smallest value; nullopt if empty
    optional<T> popMin() {
        if (!n) return nullopt;
        T v = mm ? mn : kthAt(1);
        addRaw(v, -1);
        return v;
    }

    // O(log64(U)) -- remove one copy of x if present; returns how many were removed (0 or 1)
    long long remove(T x) {
        if (!count(x)) return 0;
        addRaw(x, -1);
        return 1;
    }

    // O(log64(U)) -- remove every copy of val; returns how many were removed
    long long removeAll(T val) {
        long long k = count(val);
        if (k) addRaw(val, -k);
        return k;
    }

    // O(log64(U)) -- remove min(cnt, count(val)) copies of val; returns how many were removed
    long long removeCount(T val, long long cnt) {
        long long k = std::min(cnt, count(val));
        if (k <= 0) return 0;
        addRaw(val, -k);
        return k;
    }

    // O(1) -- how many values (copies count)
    long long size() {
        return n;
    }

    // O(log64(U)) -- smallest value > x; nullopt if there is none
    optional<T> smallestGtX(T x) {
        long long i = next((long long)x - lo + 1);
        if (i < 0) return nullopt;
        return T(lo + i);
    }

    // O(log64(U)) -- smallest value >= x; nullopt if there is none
    optional<T> smallestGteX(T x) {
        long long i = next((long long)x - lo);
        if (i < 0) return nullopt;
        return T(lo + i);
    }
};
