// Stress tests XorBasisDeletable.cpp, the two-group partitions and the arr submask / supermask sums against brute force.
// Run: g++ -O2 -std=c++17 test_new_bits.cpp && ./a.out
#include "../bit-operations/XorBasisDeletable.cpp"
#include "../bit-operations/XorBasis.cpp"
#include "../bit-operations/maxTwoGroupXorSum.cpp"
#include "../bit-operations/maxTwoGroupAndSum.cpp"
#include "../bit-operations/countSubmasksForAllMasks.cpp"
#include "../bit-operations/sumSubmasksForAllMasks.cpp"
#include "../bit-operations/countSupermasksForAllMasks.cpp"
#include "../bit-operations/sumSupermasksForAllMasks.cpp"

#define CHECK(c)                                                    \
    do {                                                            \
        if (!(c)) {                                                 \
            fprintf(stderr, "FAIL line %d: %s\n", __LINE__, #c);    \
            exit(1);                                                \
        }                                                           \
    } while (0)

static mt19937_64 rng(11);
static long long rnd(long long n) { return (long long)(rng() % (unsigned long long)n); }

static set<long long> spanOf(const vector<long long>& vals) {
    set<long long> s = {0};
    for (long long v : vals) {
        set<long long> t = s;
        for (long long x : s) t.insert(x ^ v);
        s = t;
    }
    return s;
}

static long long powMod(long long b, long long e, long long m) {
    long long r = 1 % m;
    for (b %= m; e > 0; e >>= 1, b = (long long)((__int128)b * b % m))
        if (e & 1) r = (long long)((__int128)r * b % m);
    return r;
}

int main() {
    const long long MOD = 1000000007;
    // ---- XorBasisDeletable: random inserts and removes, every query checked after every step
    for (int trial = 0; trial < 400; trial++) {
        int bits = 1 + (int)rnd(6);
        vector<long long> held;
        if (trial % 3 == 0)
            for (int i = rnd(6); i > 0; i--) held.push_back(rnd(1LL << bits));
        XorBasisDeletable b(held);
        int steps = 1 + (int)rnd(60);
        for (int step = 0; step < steps; step++) {
            double r = (double)rnd(1000) / 1000;
            if (r < 0.55 || held.empty()) {
                long long v = rnd(10) < 8 || held.empty() ? rnd(1LL << bits) : held[rnd(held.size())];
                set<long long> before = spanOf(held);
                CHECK(b.insert(v) == !before.count(v));
                held.push_back(v);
            } else if (r < 0.9) {
                size_t i = rnd(held.size());
                CHECK(b.remove(held[i]));
                held.erase(held.begin() + i);
            } else {
                long long v = rnd(1LL << bits);
                auto it = find(held.begin(), held.end(), v);
                CHECK(b.remove(v) == (it != held.end()));
                if (it != held.end()) held.erase(it);
            }
            set<long long> s = spanOf(held);
            int rank = 0;
            while ((1LL << rank) < (long long)s.size()) rank++;
            vector<long long> bas = b.basis();
            CHECK(b.size() == (long long)held.size() && b.rank() == rank && b.countDistinctXors() == (long long)s.size());
            CHECK((int)bas.size() == rank && spanOf(bas) == s && is_sorted(bas.rbegin(), bas.rend()));
            CHECK(b.maxXor() == *s.rbegin());
            long long x = rnd(1LL << bits), mx = 0, mn = LLONG_MAX;
            for (long long y : s) mx = max(mx, x ^ y), mn = min(mn, x ^ y);
            CHECK(b.canMake(x) == (s.count(x) > 0) && b.maxXorWith(x) == mx && b.minXorWith(x) == mn);
            long long wantMin = held.empty() ? -1 : (long long)held.size() > rank ? 0 : (s.size() > 1 ? *next(s.begin()) : -1);
            CHECK(b.minNonzeroXor() == wantMin);
            vector<long long> ordered(s.begin(), s.end());
            for (size_t k = 0; k < ordered.size() + 2; k++)
                CHECK(b.kthSmallestXor(k) == (k < ordered.size() ? ordered[k] : -1));
            CHECK(b.countSubsetsMakingMod(x, MOD) == (s.count(x) ? powMod(2, (long long)held.size() - rank, MOD) : 0));
        }
    }
    // big values, many operations: the rank, max XOR and basis against XorBasis rebuilt from what is held
    for (int trial = 0; trial < 30; trial++) {
        vector<long long> held, pool(1 + rnd(80));
        for (long long& v : pool) v = rnd(1LL << 60);
        XorBasisDeletable b;
        for (int step = 0; step < 400; step++) {
            if (!held.empty() && rnd(100) < 45) {
                size_t i = rnd(held.size());
                b.remove(held[i]);
                held.erase(held.begin() + i);
            } else {
                long long v = rnd(10) < 7 ? pool[rnd(pool.size())] : pool[rnd(pool.size())] ^ pool[rnd(pool.size())];
                b.insert(v);
                held.push_back(v);
            }
            XorBasis ref(held);
            CHECK(b.rank() == ref.rank() && b.maxXor() == ref.maxXor() && b.basis() == ref.basis());
        }
    }
    // ---- two-group partitions: every split of small arrays
    for (int trial = 0; trial < 3000; trial++) {
        int n = 2 + (int)rnd(7);
        long long cap = vector<long long>{2, 4, 16, 64}[rnd(4)];
        vector<long long> arr(n);
        for (long long& v : arr) v = rnd(cap);
        unsigned long long bestX = 0;
        long long bestA = 0;
        for (int mask = 1; mask < (1 << n) - 1; mask++) {
            long long xa = 0, xb = 0, aa = -1, ab = -1;
            for (int i = 0; i < n; i++) {
                if (mask >> i & 1) xa ^= arr[i], aa &= arr[i];
                else xb ^= arr[i], ab &= arr[i];
            }
            bestX = max(bestX, (unsigned long long)(xa + xb));
            bestA = max(bestA, aa + ab);
        }
        CHECK(maxTwoGroupXorSum(arr) == bestX);
        CHECK(maxTwoGroupAndSum(arr) == bestA);
    }
    CHECK(maxTwoGroupAndSum(vector<int>{3, 3, 4, 4}) == 7 && maxTwoGroupXorSum(vector<long long>{1, 2, 3}) == 6);
    CHECK(maxTwoGroupXorSum(vector<long long>{(1LL << 62) | 5, (1LL << 62) | 3}) == (1ULL << 63) + 8);  // (one each: past 2^63)
    bool threw = false;
    try { maxTwoGroupXorSum(vector<long long>{5}); } catch (const invalid_argument&) { threw = true; }
    CHECK(threw);
    // ---- submask / supermask counts and sums of arr's values, for every mask
    for (int trial = 0; trial < 1500; trial++) {
        long long cap = vector<long long>{1, 2, 8, 33}[rnd(4)];
        vector<long long> arr(rnd(12));
        for (long long& v : arr) v = rnd(cap);
        long long mx = arr.empty() ? 0 : *max_element(arr.begin(), arr.end());
        int bits = 0;
        while ((1LL << bits) <= mx) bits++;
        int size = 1 << bits;
        vector<long long> cs(size), ss(size), cp(size), sp(size);
        for (int m = 0; m < size; m++)
            for (long long v : arr) {
                if ((v & m) == v) cs[m]++, ss[m] += v;
                if ((v & m) == m) cp[m]++, sp[m] += v;
            }
        CHECK(countSubmasksForAllMasks(arr) == cs && sumSubmasksForAllMasks(arr) == ss);
        CHECK(countSupermasksForAllMasks(arr) == cp && sumSupermasksForAllMasks(arr) == sp);
    }
    printf("XorBasisDeletable, two-group partitions and submask / supermask sums: all agree with brute force\n");
}
