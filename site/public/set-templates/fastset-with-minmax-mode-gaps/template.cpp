// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/sets/fastset-with-minmax-mode-gaps/template.cpp
// @operations: add addCount clear count countDistinct largestLtX largestLteX max maxGap min minAdjacentDiff mode popMax popMin remove removeAll removeCount removeInValRange size smallestGtX smallestGteX
// @data-structure-type: fastset
// @values: online-range
// @keys: numbers
// @tracks: minmax mode gaps
// @complexities:
//   add: log64(U)
//   addCount: log64(U)
//   clear: N*log64(U)
//   count: 1
//   countDistinct: 1
//   largestLtX: log64(U)
//   largestLteX: log64(U)
//   max: 1
//   maxGap: 1 amortized
//   min: 1
//   minAdjacentDiff: 1 amortized
//   mode: 1
//   popMax: log64(U)
//   popMin: log64(U)
//   remove: log64(U)
//   removeAll: log64(U)
//   removeCount: log64(U)
//   removeInValRange: log64(U) amortized
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
    T mn{}, mx{};  // kept current by addRaw while n > 0
    map<long long, set<T>> bk;  // mode: count -> the values with that many copies
    multiset<long long> gaps;  // differences between neighbouring distinct values
    long long dups = 0;  // values with 2+ copies

    // O(U) -- lo, hi: every value added lies in [lo, hi] (any integers, negative is fine); U = hi - lo + 1
    FastSetMultiset(long long lo, long long hi) : lo(lo), hi(hi), u(int(hi - lo + 1)), cnt(u) {
        for (int width = std::max(u, 1);;) {  // (std::: the struct's own max() hides it)
            int words = (width + 63) >> 6;
            seg.emplace_back(words, 0);
            if (words == 1) break;
            width = words;
        }
    }

    long long insert(T x, long long c) {  // returns x's new count
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
        return cnt[(long long)x - lo];
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

    void addRaw(T x, long long c) {  // c copies of x (c < 0 removes); keeps min / max current
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
        {  // gaps
            if ((g >= 2) != (f >= 2)) dups += f >= 2 ? 1 : -1;  // values with 2+ copies (then the smallest difference is 0)
            if (!g || !f) {  // x appeared or disappeared: the gap between its neighbours splits or comes back
                optional<T> p = largestLtX(x), q = smallestGtX(x);
                auto drop = [&](long long v) { gaps.erase(gaps.find(v)); };
                if (f) {
                    if (p && q) drop((long long)*q - (long long)*p);
                    if (p) gaps.insert((long long)x - (long long)*p);
                    if (q) gaps.insert((long long)*q - (long long)x);
                } else {
                    if (p) drop((long long)x - (long long)*p);
                    if (q) drop((long long)*q - (long long)x);
                    if (p && q) gaps.insert((long long)*q - (long long)*p);
                }
            }
        }
        if (c > 0) {
            if (n == c) {  // the set was empty
                mn = mx = x;
                return;
            }
            if (x < mn) mn = x;
            if (x > mx) mx = x;
        } else {
            if (!n) return;
            if (!f) {  // x is gone: it may have been the min / max
                if (x == mn) mn = kthAt(1);
                if (x == mx) mx = kthAt(n);
            }
        }
    }

    void resetCached() {  // nothing counted: as newly built
        bk.clear();
        gaps.clear(), dups = 0;
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

    // O(1) -- largest value; nullopt if empty
    optional<T> max() {
        if (!n) return nullopt;
        return mx;
    }

    // O(1 amortized) -- largest difference between two neighbouring distinct values; nullopt if fewer than 2 distinct values
    optional<long long> maxGap() {
        if (d < 2) return nullopt;
        return *gaps.rbegin();
    }

    // O(1) -- smallest value; nullopt if empty
    optional<T> min() {
        if (!n) return nullopt;
        return mn;
    }

    // O(1 amortized) -- smallest difference between two values in the set (0 if some value has 2+ copies); nullopt if fewer than 2 values
    optional<long long> minAdjacentDiff() {
        if (n < 2) return nullopt;
        if (dups) return 0LL;
        return *gaps.begin();
    }

    // O(1) -- (a most frequent value, its count); nullopt if empty. C++ returns the smallest of the most frequent values
    optional<pair<T, long long>> mode() {
        if (!n) return nullopt;
        auto& [f, vs] = *bk.rbegin();
        return pair<T, long long>{*vs.begin(), f};
    }

    // O(log64(U)) -- remove and return the largest value; nullopt if empty
    optional<T> popMax() {
        if (!n) return nullopt;
        T v = mx;
        addRaw(v, -1);
        return v;
    }

    // O(log64(U)) -- remove and return the smallest value; nullopt if empty
    optional<T> popMin() {
        if (!n) return nullopt;
        T v = mn;
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

    // O(log64(U) amortized) -- remove every value v with lo <= v <= hi; returns how many copies were removed (0 if lo > hi)
    long long removeInValRange(T lo, T hi) {
        if (hi < lo) return 0;
        long long removed = 0;
        for (long long i = next((long long)lo - this->lo); i >= 0 && this->lo + i <= (long long)hi; i = next(i + 1)) {  // each present value in [lo, hi]
            long long k = cnt[i];
            addRaw(T(this->lo + i), -k), removed += k;
        }
        return removed;
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
