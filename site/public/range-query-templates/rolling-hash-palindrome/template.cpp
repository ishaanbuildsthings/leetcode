// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries/rolling-hash-palindrome/template.cpp
#include <bits/stdc++.h>
using namespace std;
using ll = long long;

// @operations: append getAll hashAll isPalindrome longestPalCenteredAtI longestPalCenteredAtIPlusOne pointGet pop rangeHash rangeHashReversed rangesEqual size
// @data-structure-type: rolling-hash
// @letters: same
// @complexities:
//   append: 1
//   getAll: N
//   isPalindrome: 1
//   pointGet: 1
//   pop: 1
//   rangeHash: 1
//   rangeHashReversed: 1
//   rangesEqual: 1
//   size: 1
//   hashAll: 1
//   longestPalCenteredAtI: log(N)
//   longestPalCenteredAtIPlusOne: log(N)
//   build: N
// @memory:
//   layout: none
//   node: back[1*N] P[1*N] RB[1*N]
//   tags: none
//   other: pw[1*N] pwi[1*N]
//   note: prefix hashes read both ways; the right end only, so every op is O(1) worst case

// Rolling hashes read both ways over a window that grows and shrinks at the right end: range hashes, reversed range
// hashes and palindrome checks in O(1) worst case (the longest palindrome around a centre by binary search).
// Values are numbers or single characters (then they hash by their code). All indices 0-based, ranges inclusive.
// Hashes: polynomial, mod a prime (2^61 - 1 unless you pass one) with a base drawn at random once per run and shared by
// every structure in it, so hashes compare across structures; a base and mod passed to the constructor are that
// structure's own. The base needs no relation to the alphabet: with a 61-bit prime mod and a random base, collisions
// are chance (about 2^-61 per comparison), not structure.
//
// Usage:
//     vector<long long> arr = {3, 1, 4, 1, 5};
//     unsigned long long base = 911, mod = 1000000007;                                    // set these only to match
//     something else (unset, they are shared between structures, so hashes compare)
//     RollingHashPalindrome<long long> t1(arr);                                           // the defaults: hashing just
//     works for negatives, large numbers, chars, with the run's random base
//     RollingHashPalindrome<long long> t0;                                                // or start empty
//     RollingHashPalindrome<int> ti(vector<int>{3, 1, 4});                                // ints work too (T = int),
//     and negatives
//     RollingHashPalindrome<long long> t2(arr, base);                                     // your base, mod 2^61 - 1
//     RollingHashPalindrome<long long> t3(arr, nullopt, mod);                             // the run's random base,
//     your mod
//     RollingHashPalindrome<long long> t4(arr, base, mod);                                // both
//     RollingHashPalindrome<char> s(vector<char>(str.begin(), str.end()));                // characters: T = char
//     t1.rangeHash(0, 2) == RollingHashPalindrome<long long>({3, 1, 4}).rangeHash(0, 2);  // true: the same values,
//     base and mod (the run's)
// The run's random base, shared by every rolling-hash structure built without one (so their hashes compare): no test
// can be built against it. Two rolling-hash templates in one file share this one copy.
#ifndef LEETGOAT_ROLLING_HASH_SHARED
#define LEETGOAT_ROLLING_HASH_SHARED
struct RollingHashShared {
    static constexpr unsigned long long HP = (1ULL << 61) - 1;  // the default mod: a prime
    static inline unsigned long long base = 0;
    static unsigned long long rnd() {
        static mt19937_64 g(chrono::steady_clock::now().time_since_epoch().count());
        return g();
    }
    static void init() {  // (the random base, the first time anything is built)
        if (!base) base = (1ULL << 40) + rnd() % (HP - (1ULL << 41));
    }
};
#endif

template <typename T>
struct RollingHashPalindrome {
    using U64 = unsigned long long;
    using R = RollingHashShared;
    vector<T> back;
    vector<U64> P;  // P[k]: hash of back[0..k] read left to right
    vector<U64> RB;  // RB[k]: sum of hval(back[k']) * base^k' over k' <= k: the back half read backwards
    U64 mod, base, baseInv;
    vector<U64> pw{1}, pwi{1};  // pw[k] = base^k, pwi[k] = base^-k, grown as the window grows (amortized O(1))

    // O(N) -- arr: the initial array (a vector of ints, long longs or chars; negatives are fine), or left out to start
    // empty. Hashing just works with the defaults: any 64-bit values, negatives and characters, with the run's random
    // base
    // (shared by every structure of the run, so their hashes compare) and the prime mod 2^61 - 1 (the fast one: its
    // reduction is two shifts). Set hashBase / hashMod only to match something else: then every value must be below the
    // mod, the mod a prime below 2^63, and the base in [2, mod - 2]
    explicit RollingHashPalindrome(const vector<T>& arr = {}, optional<U64> hashBase = nullopt,
        optional<U64> hashMod = nullopt) {
        R::init();
        mod = hashMod ? *hashMod : R::HP;
        base = (hashBase ? *hashBase : R::base) % mod;
        baseInv = power(base, mod - 2);
        for (const T& v : arr) append(v);
    }

    // O(1) -- the current length of the window
    int size() const { return (int)back.size(); }

    // O(N) -- the whole window
    vector<T> getAll() const {
        return back;
    }

    // O(1) -- a[i]; needs 0 <= i < size(), else throws out_of_range
    T pointGet(int i) const {
        if (i < 0 || i >= size()) throw out_of_range("pointGet: needs 0 <= i < size()");
        return back[i];
    }

    // O(1) -- append v at the right end
    void append(T v) {
        U64 hv = hval(v);
        size_t k = back.size();
        P.push_back(k ? add(mul(P.back(), base), hv) : hv);
        powers(k);
        RB.push_back(add(k ? RB.back() : 0, mul(hv, pw[k])));
        back.push_back(v);
    }

    // O(1) -- remove a[size()-1] and return it; needs size() >= 1, else throws out_of_range
    T pop() {
        if (size() < 1) throw out_of_range("pop: needs size() >= 1");
        P.pop_back();
        RB.pop_back();
        T v = back.back();
        back.pop_back();
        return v;
    }

    // O(1) -- hash of a[l..r] read left to right (mod 2^61 - 1, random base): equal ranges hash equal; needs
    // 0 <= l <= r < size(), else throws out_of_range
    U64 rangeHash(int l, int r) {
        if (l < 0 || l > r || r >= size()) throw out_of_range("rangeHash: needs 0 <= l <= r < size()");
        return hash(l, r);
    }

    // O(1) -- hash of a[l..r] read right to left (what rangeHash gives for the reversed range); needs
    // 0 <= l <= r < size(), else throws out_of_range
    U64 rangeHashReversed(int l, int r) {
        if (l < 0 || l > r || r >= size()) throw out_of_range("rangeHashReversed: needs 0 <= l <= r < size()");
        return hashRev(l, r);
    }

    // O(1) -- is a[l..r] a palindrome (its two readings hash equal); needs 0 <= l <= r < size(), else throws
    // out_of_range
    bool isPalindrome(int l, int r) {
        if (l < 0 || l > r || r >= size()) throw out_of_range("isPalindrome: needs 0 <= l <= r < size()");
        return hash(l, r) == hashRev(l, r);
    }

    // O(1) -- are a[l1..r1] and a[l2..r2] equal (same length and hash); needs 0 <= l1 <= r1 < size() and
    // 0 <= l2 <= r2 < size(), else throws out_of_range
    bool rangesEqual(int l1, int r1, int l2, int r2) {
        if (l1 < 0 || l1 > r1 || r1 >= size() || l2 < 0 || l2 > r2 || r2 >= size())
            throw out_of_range("rangesEqual: needs 0 <= l1 <= r1 < size() and 0 <= l2 <= r2 < size()");
        return r1 - l1 == r2 - l2 && hash(l1, r1) == hash(l2, r2);
    }

    // O(1) -- hash of the whole array a[0..n-1]: the same base and mod as rangeHash (shared by every structure
    // this run, so it compares with another one's hashes); needs n >= 1, else throws out_of_range
    auto hashAll() {
        if (size() < 1) throw out_of_range("hashAll: needs n >= 1");
        return rangeHash(0, size() - 1);
    }

    // O(log(N)) -- (l, r) of the longest odd palindrome a[l..r] centred on a[i] (at least (i, i)): a binary search on
    // its radius, log N calls of isPalindrome; needs 0 <= i < n, else throws out_of_range
    pair<long long, long long> longestPalCenteredAtI(long long i) {
        long long len = size();
        if (i < 0 || i >= len) throw out_of_range("longestPalCenteredAtI: needs 0 <= i < n");
        long long lo = 0, hi = min(i, len - 1 - i);
        while (lo < hi) {
            long long mid = (lo + hi + 1) / 2;
            if (isPalindrome(i - mid, i + mid)) lo = mid;
            else hi = mid - 1;
        }
        return {i - lo, i + lo};
    }

    // O(log(N)) -- (l, r) of the longest even palindrome a[l..r] centred between a[i] and a[i+1]; (i + 1, i), the empty
    // range, when there is none (so also for i = n - 1): a binary search on its radius, log N calls of isPalindrome;
    // needs 0 <= i < n, else throws out_of_range
    pair<long long, long long> longestPalCenteredAtIPlusOne(long long i) {
        long long len = size();
        if (i < 0 || i >= len) throw out_of_range("longestPalCenteredAtIPlusOne: needs 0 <= i < n");
        long long lo = 0, hi = min(i + 1, len - 1 - i);
        while (lo < hi) {
            long long mid = (lo + hi + 1) / 2;
            if (isPalindrome(i - mid + 1, i + mid)) lo = mid;
            else hi = mid - 1;
        }
        return {i - lo + 1, i + lo};
    }

    // ---- internals ----

    U64 hash(int x, int y) {  // hash of a[x..y] left to right
        powers(y - x + 1);
        return sub(P[y], x ? mul(P[x - 1], pw[y - x + 1]) : 0);
    }

    U64 hashRev(int x, int y) {  // hash of a[y], a[y-1], ..., a[x]
        powers(x);
        return mul(sub(RB[y], x ? RB[x - 1] : 0), pwi[x]);
    }

    U64 mul(U64 a, U64 b) const {
        __uint128_t c = (__uint128_t)a * b;
        if (mod != R::HP) return (U64)(c % mod);
        U64 r = (U64)(c & mod) + (U64)(c >> 61);  // (2^61 - 1: two shifts instead of a division)
        r = (r & mod) + (r >> 61);
        return r >= mod ? r - mod : r;
    }
    U64 add(U64 a, U64 b) const { return a + b >= mod ? a + b - mod : a + b; }
    U64 sub(U64 a, U64 b) const { return a >= b ? a - b : a + mod - b; }
    U64 power(U64 a, U64 e) const {
        U64 r = 1;
        for (; e; e >>= 1, a = mul(a, a)) if (e & 1) r = mul(r, a);
        return r;
    }
    void powers(size_t k) {  // pw and pwi with at least k + 1 entries
        while (pw.size() <= k) pw.push_back(mul(pw.back(), base)), pwi.push_back(mul(pwi.back(), baseInv));
    }

    U64 hval(T v) const {  // the hash of value v: v + 1, so a 0 is not nothing (a 0 in front would vanish)
        long long r = (long long)v % (long long)mod;
        return add(r < 0 ? (U64)(r + (long long)mod) : (U64)r, 1);
    }
};
