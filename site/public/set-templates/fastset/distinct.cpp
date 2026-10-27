// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/sets/fastset/distinct.cpp
// @operations: add clear count countDistinct largestLtX largestLteX max min popMax popMin remove removeInValRange size smallestGtX smallestGteX
// @data-structure-type: fastset
// @values: online-range
// @keys: numbers
// @tracks: none
// @complexities:
//   add: log64(U)
//   clear: N*log64(U)
//   count: 1
//   countDistinct: 1
//   largestLtX: log64(U)
//   largestLteX: log64(U)
//   max: log64(U)
//   min: log64(U)
//   popMax: log64(U)
//   popMin: log64(U)
//   remove: log64(U)
//   removeInValRange: log64(U) amortized
//   size: 1
//   smallestGtX: log64(U)
//   smallestGteX: log64(U)
//   build: U/64
// @memory:
//   layout: none
//   node: seg[1*U/64]
//   tags: none
//   other: none
//   note: U = hi - lo + 1: just the trie's U / 64 + U / 4096 + ... 64-bit words (about U / 63); no duplicates

// Ordered set of DISTINCT integers in [lo, hi] (FastSet): a 64-ary bit trie over the U = hi - lo + 1 slots, a bit
// meaning "this value (or something under this word) is present". No duplicates: adding a value that is already in
// the set does nothing, so there is no count per value and building is just the trie's ~U / 63 words. Every op touches
// one word per level: log_64(U) levels, about 4 for U = 10^7. T: int, long long, ...
template <typename T>
struct FastSet {
    long long lo, hi;
    int u;
    vector<vector<unsigned long long>> seg;  // seg[h][w] = 64 bits, one per word of level h - 1 (level 0: one per value)
    long long n = 0;

    // O(U/64) -- lo, hi: every value added lies in [lo, hi] (any integers, negative is fine); U = hi - lo + 1
    FastSet(long long lo, long long hi) : lo(lo), hi(hi), u(int(hi - lo + 1)) {
        for (int width = std::max(u, 1);;) {  // (std::: the struct's own max() hides it)
            int words = (width + 63) >> 6;
            seg.emplace_back(words, 0);
            if (words == 1) break;
            width = words;
        }
    }

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

    // O(log64(U)) -- add x (nothing if x is already in the set: no duplicates)
    void add(T x) {
        int i = int((long long)x - lo);  // x must lie in [lo, hi]
        if (seg[0][i >> 6] >> (i & 63) & 1) return;
        n++;
        for (auto& level : seg) level[i >> 6] |= 1ULL << (i & 63), i >>= 6;
    }

    // O(log64(U)) -- remove x if present; returns how many were removed (0 or 1)
    long long remove(T x) {
        long long i = (long long)x - lo;
        if (i < 0 || i >= u || !(seg[0][i >> 6] >> (i & 63) & 1)) return 0;
        n--;
        for (auto& level : seg) {
            long long j = i >> 6;
            if (level[j] &= ~(1ULL << (i & 63))) break;
            i = j;
        }
        return 1;
    }

    // O(N log64(U)) -- remove everything (N = values in it): as newly built, so reuse it instead of building a new one
    void clear() {
        n = 0;
        clearData();
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
            }
        }
    }

    // O(log64(U) amortized) -- remove every value v with lo <= v <= hi; returns how many were removed (0 if lo > hi)
    long long removeInValRange(T lo, T hi) {
        if (hi < lo) return 0;
        long long removed = 0;
        for (long long i = next((long long)lo - this->lo); i >= 0 && this->lo + i <= (long long)hi; i = next(i + 1))
            remove(T(this->lo + i)), removed++;
        return removed;
    }

    // O(1) -- 1 if x is in the set, else 0
    long long count(T x) const {
        long long i = (long long)x - lo;
        return i >= 0 && i < u ? (long long)(seg[0][i >> 6] >> (i & 63) & 1) : 0;
    }

    // O(1) -- how many values (no duplicates, so also how many distinct)
    long long countDistinct() const { return n; }

    // O(1) -- how many values
    long long size() const { return n; }

    // O(log64(U)) -- smallest value; nullopt if empty
    optional<T> min() const {
        long long i = next(0);
        if (i < 0) return nullopt;
        return T(lo + i);
    }

    // O(log64(U)) -- largest value; nullopt if empty
    optional<T> max() const {
        long long i = prev(u - 1);
        if (i < 0) return nullopt;
        return T(lo + i);
    }

    // O(log64(U)) -- remove and return the smallest value; nullopt if empty
    optional<T> popMin() {
        optional<T> v = min();
        if (v) remove(*v);
        return v;
    }

    // O(log64(U)) -- remove and return the largest value; nullopt if empty
    optional<T> popMax() {
        optional<T> v = max();
        if (v) remove(*v);
        return v;
    }

    // O(log64(U)) -- smallest value >= x; nullopt if there is none
    optional<T> smallestGteX(T x) const {
        long long i = next((long long)x - lo);
        if (i < 0) return nullopt;
        return T(lo + i);
    }

    // O(log64(U)) -- smallest value > x; nullopt if there is none
    optional<T> smallestGtX(T x) const {
        long long i = next((long long)x - lo + 1);
        if (i < 0) return nullopt;
        return T(lo + i);
    }

    // O(log64(U)) -- largest value <= x; nullopt if there is none
    optional<T> largestLteX(T x) const {
        long long i = prev((long long)x - lo);
        if (i < 0) return nullopt;
        return T(lo + i);
    }

    // O(log64(U)) -- largest value < x; nullopt if there is none
    optional<T> largestLtX(T x) const {
        long long i = prev((long long)x - lo - 1);
        if (i < 0) return nullopt;
        return T(lo + i);
    }
};
