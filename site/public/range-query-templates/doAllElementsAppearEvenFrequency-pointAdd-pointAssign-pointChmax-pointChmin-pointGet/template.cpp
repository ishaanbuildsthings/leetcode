// @operations: doAllElementsAppearEvenFrequency pointAdd pointAssign pointChmax pointChmin pointGet
// @data-structure-type: BIT
// @complexities:
//   doAllElementsAppearEvenFrequency: log(N)
//   pointAdd: log(N)
//   pointAssign: log(N)
//   pointChmax: log(N)
//   pointChmin: log(N)
//   pointGet: 1
//   build: N
// @memory:
//   layout: none
//   node: bit[1*N]
//   tags: none
//   other: vals[1*N] a[1*N] tag[1*N]
//   note: a holds each index's random hash; tag maps each distinct value to its hash
// @original-file-url: https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/segment-trees/normal/xorHashing_allEven_withUpdates.cpp

// Range "does every value appear an even number of times?" via xor hashing, with point updates.
// Each distinct value gets a random 64-bit tag; xor over a range cancels tags in pairs, so an all-even range
// hashes to 0. False positives have probability ~q / 2^64. Xor is invertible, so a Fenwick tree suffices.
// All indices 0-based, ranges inclusive. T: any hashable type with ==.
template <typename T>
struct XorEven {
    int n;
    vector<T> vals;
    vector<unsigned long long> a;    // a[i] = tag of the value at position i
    vector<unsigned long long> bit;  // 1-indexed Fenwick tree over a
    unordered_map<T, unsigned long long> tag;
    mt19937_64 rng;

    // O(N). Seeded from the clock: a fixed seed is hackable, since tags could be precomputed to collide.
    explicit XorEven(const vector<T>& arr)
        : n((int)arr.size()), vals(arr), a(arr.size()), bit(arr.size() + 1),
          rng(chrono::steady_clock::now().time_since_epoch().count()) {
        tag.reserve(2 * n);
        for (int i = 0; i < n; i++) a[i] = bit[i + 1] = tagOf(arr[i]);
        for (int i = 1; i <= n; i++) {
            int j = i + (i & -i);
            if (j <= n) bit[j] ^= bit[i];
        }
    }

    // O(1) amortized -- random tag for a value, minted on first sight
    unsigned long long tagOf(const T& v) {
        auto it = tag.find(v);
        if (it != tag.end()) return it->second;
        return tag[v] = rng();
    }

    // O(logN) -- xor of tags over a[0..i]; i may be -1
    unsigned long long prefix(int i) const {
        unsigned long long s = 0;
        for (int p = i + 1; p > 0; p &= p - 1) s ^= bit[p];
        return s;
    }

    // O(logN) -- xor of tags over a[l..r]
    unsigned long long rangeXor(int l, int r) const { return prefix(r) ^ (l ? prefix(l - 1) : 0ULL); }

    // O(logN) -- true iff every value in a[l..r] appears an even number of times
    bool doAllElementsAppearEvenFrequency(int l, int r) const { return rangeXor(l, r) == 0; }

    // O(logN) -- true iff exactly one value appears an odd number of times in a[l..r], and it is v
    bool oneOdd(int l, int r, const T& v) { return rangeXor(l, r) == tagOf(v); }

    // O(logN) -- a[i] = v
    void pointAssign(int i, const T& v) {
        vals[i] = v;
        unsigned long long t = tagOf(v), d = a[i] ^ t;
        if (!d) return;
        a[i] = t;
        for (int p = i + 1; p <= n; p += p & -p) bit[p] ^= d;
    }

    // O(1) -- a[i]
    T pointGet(int i) const { return vals[i]; }

    // O(logN) -- a[i] = max(a[i], v)
    void pointChmax(int i, const T& v) { if (v > vals[i]) pointAssign(i, v); }

    // O(logN) -- a[i] = min(a[i], v)
    void pointChmin(int i, const T& v) { if (v < vals[i]) pointAssign(i, v); }

    // O(logN) -- a[i] += delta
    void pointAdd(int i, const T& delta) { pointAssign(i, vals[i] + delta); }
};
