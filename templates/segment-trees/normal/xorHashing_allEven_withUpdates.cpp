#include<bits/stdc++.h>
using namespace std;

// Range "is every value's count even?" via XOR hashing.
// Each distinct value gets a random 64-bit tag. XOR over a range cancels tags
// in pairs, so an all-even range hashes to 0. False positives (nonzero counts
// that happen to cancel) have probability ~q/2^64.
// XOR is invertible, so a Fenwick tree suffices — no segment tree needed.
// T may be any hashable type. O(n) build, O(log n) update, O(log n) query.
// All indices 0-based, all ranges inclusive.
template <typename T>
struct XorEven {
    int n;
    vector<unsigned long long> a;   // a[i] = tag of the value at position i
    vector<unsigned long long> bit; // 1-indexed
    unordered_map<T, unsigned long long> tag;
    mt19937_64 rng;

    XorEven() {}
    XorEven(const vector<T>& arr)
        : rng(chrono::steady_clock::now().time_since_epoch().count()) {
        n = arr.size();
        a.resize(n);
        tag.reserve(2 * n);
        for (int i = 0; i < n; i++) a[i] = tagOf(arr[i]);
        // O(n) build: seed the tree, then push each node into its parent
        bit.assign(n + 1, 0);
        for (int i = 0; i < n; i++) bit[i + 1] = a[i];
        for (int i = 1; i <= n; i++) {
            int j = i + (i & -i);
            if (j <= n) bit[j] ^= bit[i];
        }
    }

    // O(1) amortized — random tag for a value, minted on first sight
    // Seeded from the clock: a fixed seed is hackable, since an adversary can
    // precompute two values whose tags collide.
    unsigned long long tagOf(const T& v) {
        auto it = tag.find(v);
        if (it != tag.end()) return it->second;
        return tag[v] = rng();
    }

    // O(log n) — assign position i the value val (overwrite, not add)
    void pointSet(int i, const T& val) {
        unsigned long long t = tagOf(val), d = a[i] ^ t;
        if (!d) return;
        a[i] = t;
        for (int p = i + 1; p <= n; p += p & -p) bit[p] ^= d;
    }

    // O(log n) — XOR of tags over [0, i]; i may be -1
    unsigned long long prefix(int i) {
        unsigned long long s = 0;
        for (int p = i + 1; p > 0; p -= p & -p) s ^= bit[p];
        return s;
    }

    // O(log n) — XOR of tags over [l, r]
    unsigned long long rangeXor(int l, int r) {
        return prefix(r) ^ (l ? prefix(l - 1) : 0ULL);
    }

    // O(log n) — true iff every value in a[l..r] occurs an even number of times
    bool allEven(int l, int r) {
        return rangeXor(l, r) == 0;
    }

    // O(log n) — true iff exactly one value occurs an odd number of times in
    // a[l..r], and that value is val (the classic "all even except one" check)
    bool oneOdd(int l, int r, const T& val) {
        return rangeXor(l, r) == tagOf(val);
    }
};