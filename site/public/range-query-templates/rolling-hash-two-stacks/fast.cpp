// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries/rolling-hash-two-stacks/fast.cpp
#include <bits/stdc++.h>
using namespace std;
using ll = long long;

// @operations: append appendLeft getAll hashAll pointGet pop popLeft rangeHash rangesEqual size
// @data-structure-type: rolling-hash
// @letters: same
// @complexities:
//   append: 1
//   appendLeft: 1
//   getAll: N
//   pointGet: 1
//   pop: 1 amortized
//   popLeft: 1 amortized
//   rangeHash: 1
//   rangesEqual: 1
//   size: 1
//   hashAll: 1
//   build: N
// @memory:
//   layout: none
//   node: back[1*N] front[1*N] P[1*N] G[1*N]
//   tags: none
//   other: pw[1*N] pwi[1*N]
//   note: prefix hashes on the back half, suffix-anchored ones on the front, so any range is O(1); a pop that empties a half moves half of the other over and rebuilds its hashes (amortized O(1)); no point assign (it would invalidate every prefix hash)

// Rolling hashes of any range of a window that grows and shrinks at both ends (sliding windows, deques): the back half
// keeps prefix hashes, the front half (stored reversed) suffix-anchored ones, so a range in either half or across the
// middle is O(1). No point assign: that would change every prefix hash after it (a seg tree does that in log N).
// Values are numbers or single characters (then they hash by their code). All indices 0-based, ranges inclusive.
// Hashes: polynomial, mod a prime (2^61 - 1 unless you pass one) with a base drawn at random once per run and shared by
// every structure in it, so hashes compare across structures; a base and mod passed to the constructor are that
// structure's own. The base needs no relation to the alphabet: with a 61-bit prime mod and a random base, collisions
// are chance (about 2^-61 per comparison), not structure.
//
// Usage:
//     vector<long long> arr = {3, 1, 4, 1, 5};
//     unsigned long long base = 911, mod = 1000000007;                               // set these only to match
//     something else (unset, they are shared between structures, so hashes compare)
//     RollingHashDeque<long long> t1(arr);                                           // the defaults: hashing just
//     works for negatives, large numbers, chars, with the run's random base
//     RollingHashDeque<long long> t0;                                                // or start empty
//     RollingHashDeque<int> ti(vector<int>{3, 1, 4});                                // ints work too (T = int), and
//     negatives
//     RollingHashDeque<long long> t2(arr, base);                                     // your base, mod 2^61 - 1
//     RollingHashDeque<long long> t3(arr, nullopt, mod);                             // the run's random base, your mod
//     RollingHashDeque<long long> t4(arr, base, mod);                                // both
//     RollingHashDeque<char> s(vector<char>(str.begin(), str.end()));                // characters: T = char
//     t1.rangeHash(0, 2) == RollingHashDeque<long long>({3, 1, 4}).rangeHash(0, 2);  // true: the same values, base and
//     mod (the run's)
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

// FAST MODE drawbacks compared with template.cpp:
//   - sanitizers are skipped inside this template, so a bad access in it goes unreported
// Same public operations and answers, same limits; it needs GCC or Clang and C++17.
#ifdef __SSE2__
#include <immintrin.h>
#endif

// LEETCODE_NO_SANITIZE skips sanitizers in a function. It only changes anything where sanitizers run, like LeetCode: on
// Codeforces it compiles and does nothing.
// This template already uses it. To go further, put it on the one function with your hot loop:
//   LEETCODE_NO_SANITIZE long long maxSum(vector<int>& nums, int k) {
// A lambda needs its own: [&](int x) LEETCODE_NO_SANITIZE { ... }. It does not carry into anything that function calls.
// Inside a marked function use raw pointers and plain comparisons, not vector[] and min / max, or it can get slower.
// Bad memory accesses in a marked function go unreported.
#ifndef LEETCODE_NO_SANITIZE
#define LEETCODE_NO_SANITIZE __attribute__((no_sanitize("address"), no_sanitize("undefined")))
#endif
#define LEETCODE_NO_SANITIZE_INLINE LEETCODE_NO_SANITIZE __attribute__((always_inline)) inline

// A vector whose [] and size() always inline, even with sanitizers skipped (libstdc++ only; elsewhere a plain vector)
template <typename U>
struct HotVector : vector<U> {
    using vector<U>::vector;
    HotVector() = default;
    HotVector(const vector<U>& other) : vector<U>(other) {}
    HotVector(vector<U>&& other) : vector<U>(move(other)) {}
#ifdef __GLIBCXX__
    LEETCODE_NO_SANITIZE_INLINE typename vector<U>::reference operator[](size_t i) { return this->_M_impl._M_start[i]; }
    LEETCODE_NO_SANITIZE_INLINE typename vector<U>::const_reference operator[](size_t i) const {
        return this->_M_impl._M_start[i];
    }
    LEETCODE_NO_SANITIZE_INLINE size_t size() const { return size_t(this->_M_impl._M_finish - this->_M_impl._M_start); }
#endif
};

template <typename T>
struct RollingHashDeque {
    using U64 = unsigned long long;
    using R = RollingHashShared;
    HotVector<T> back;
    HotVector<T> front;  // the first values, stored last to first
    HotVector<U64> P;  // P[k]: hash of back[0..k] read left to right
    // G[j]: sum of hval(front[j']) * base^j' over j' <= j: front[j..0] read in window order, times base^0
    HotVector<U64> G;
    U64 mod, base, baseInv;
    HotVector<U64> pw{1}, pwi{1};  // pw[k] = base^k, pwi[k] = base^-k, grown as the window grows (amortized O(1))

    // O(N) -- arr: the initial array (a vector of ints, long longs or chars; negatives are fine), or left out to start
    // empty. Hashing just works with the defaults: any 64-bit values, negatives and characters, with the run's random
    // base
    // (shared by every structure of the run, so their hashes compare) and the prime mod 2^61 - 1 (the fast one: its
    // reduction is two shifts). Set hashBase / hashMod only to match something else: then every value must be below the
    // mod, the mod a prime below 2^63, and the base in [2, mod - 2]
    explicit RollingHashDeque(const vector<T>& arr = {}, optional<U64> hashBase = nullopt,
        optional<U64> hashMod = nullopt) {
        R::init();
        mod = hashMod ? *hashMod : R::HP;
        base = (hashBase ? *hashBase : R::base) % mod;
        baseInv = power(base, mod - 2);
        for (const T& v : arr) append(v);
    }

    // O(1) -- the current length of the window
    LEETCODE_NO_SANITIZE int size() const { return (int)(front.size() + back.size()); }

    // O(N) -- the whole window
    LEETCODE_NO_SANITIZE vector<T> getAll() const {
        vector<T> out(front.rbegin(), front.rend());
        out.insert(out.end(), back.begin(), back.end());
        return out;
    }

    // O(1) -- a[i]; needs 0 <= i < size(), else throws out_of_range
    LEETCODE_NO_SANITIZE T pointGet(int i) const {
        if (i < 0 || i >= size()) throw out_of_range("pointGet: needs 0 <= i < size()");
        int f = (int)front.size();
        return i < f ? front[f - 1 - i] : back[i - f];
    }

    // O(1) -- append v at the right end
    LEETCODE_NO_SANITIZE void append(T v) {
        U64 hv = hval(v);
        size_t k = back.size();
        P.push_back(k ? add(mul(P.back(), base), hv) : hv);
        back.push_back(v);
    }

    // O(1) -- insert v at the left end (it becomes a[0]; every index shifts up by 1)
    LEETCODE_NO_SANITIZE void appendLeft(T v) {
        U64 hv = hval(v);
        size_t j = front.size();
        powers(j);
        G.push_back(add(j ? G.back() : 0, mul(hv, pw[j])));
        front.push_back(v);
    }

    // O(1 amortized) -- remove a[size()-1] and return it; needs size() >= 1, else throws out_of_range
    LEETCODE_NO_SANITIZE T pop() {
        if (size() < 1) throw out_of_range("pop: needs size() >= 1");
        if (back.empty()) moveToBack();
        P.pop_back();
        T v = back.back();
        back.pop_back();
        return v;
    }

    // O(1 amortized) -- remove a[0] and return it (every index shifts down by 1); needs size() >= 1, else throws
    // out_of_range
    LEETCODE_NO_SANITIZE T popLeft() {
        if (size() < 1) throw out_of_range("popLeft: needs size() >= 1");
        if (front.empty()) moveToFront();
        G.pop_back();
        T v = front.back();
        front.pop_back();
        return v;
    }

    // O(1) -- hash of a[l..r] read left to right (mod 2^61 - 1, random base): equal ranges hash equal; needs
    // 0 <= l <= r < size(), else throws out_of_range
    LEETCODE_NO_SANITIZE U64 rangeHash(int l, int r) {
        if (l < 0 || l > r || r >= size()) throw out_of_range("rangeHash: needs 0 <= l <= r < size()");
        return hash(l, r);
    }

    // O(1) -- are a[l1..r1] and a[l2..r2] equal (same length and hash); needs 0 <= l1 <= r1 < size() and
    // 0 <= l2 <= r2 < size(), else throws out_of_range
    LEETCODE_NO_SANITIZE bool rangesEqual(int l1, int r1, int l2, int r2) {
        if (l1 < 0 || l1 > r1 || r1 >= size() || l2 < 0 || l2 > r2 || r2 >= size())
            throw out_of_range("rangesEqual: needs 0 <= l1 <= r1 < size() and 0 <= l2 <= r2 < size()");
        return r1 - l1 == r2 - l2 && hash(l1, r1) == hash(l2, r2);
    }

    // O(1) -- hash of the whole array a[0..n-1]: the same base and mod as rangeHash (shared by every structure
    // this run, so it compares with another one's hashes); needs n >= 1, else throws out_of_range
    LEETCODE_NO_SANITIZE auto hashAll() {
        if (size() < 1) throw out_of_range("hashAll: needs n >= 1");
        return rangeHash(0, size() - 1);
    }

    // ---- internals ----

    LEETCODE_NO_SANITIZE U64 backHash(int x, int y) {  // hash of back[x..y] left to right
        powers(y - x + 1);
        return sub(P[y], x ? mul(P[x - 1], pw[y - x + 1]) : 0);
    }

    LEETCODE_NO_SANITIZE U64 frontHash(int jl, int jr) {
        // hash of front[jl], front[jl-1], ..., front[jr] (jr <= jl): a[f-1-jl .. f-1-jr]
        powers(jr);
        return mul(sub(G[jl], jr ? G[jr - 1] : 0), pwi[jr]);
    }

    LEETCODE_NO_SANITIZE U64 hash(int l, int r) {
        int f = (int)front.size();
        if (l >= f) return backHash(l - f, r - f);
        if (r < f) return frontHash(f - 1 - l, f - 1 - r);
        powers(r - f + 1);
        return add(mul(frontHash(f - 1 - l, 0), pw[r - f + 1]), backHash(0, r - f));
    }

    LEETCODE_NO_SANITIZE U64 mul(U64 a, U64 b) const {
        __uint128_t c = (__uint128_t)a * b;
        if (mod != R::HP) return (U64)(c % mod);
        U64 r = (U64)(c & mod) + (U64)(c >> 61);  // (2^61 - 1: two shifts instead of a division)
        r = (r & mod) + (r >> 61);
        return r >= mod ? r - mod : r;
    }
    LEETCODE_NO_SANITIZE U64 add(U64 a, U64 b) const { return a + b >= mod ? a + b - mod : a + b; }
    LEETCODE_NO_SANITIZE U64 sub(U64 a, U64 b) const { return a >= b ? a - b : a + mod - b; }
    LEETCODE_NO_SANITIZE U64 power(U64 a, U64 e) const {
        U64 r = 1;
        for (; e; e >>= 1, a = mul(a, a)) if (e & 1) r = mul(r, a);
        return r;
    }
    LEETCODE_NO_SANITIZE void powers(size_t k) {  // pw and pwi with at least k + 1 entries
        while (pw.size() <= k) pw.push_back(mul(pw.back(), base)), pwi.push_back(mul(pwi.back(), baseInv));
    }

    LEETCODE_NO_SANITIZE U64 hval(T v) const {
        // the hash of value v: v + 1, so a 0 is not nothing (a 0 in front would vanish)
        long long r = (long long)v % (long long)mod;
        return add(r < 0 ? (U64)(r + (long long)mod) : (U64)r, 1);
    }

    LEETCODE_NO_SANITIZE void moveToFront() {  // the first half of the back becomes the front (the front is empty)
        size_t k = (back.size() + 1) / 2;
        front.assign(back.rend() - k, back.rend());
        back.erase(back.begin(), back.begin() + k);
        rebuild();
    }

    LEETCODE_NO_SANITIZE void moveToBack() {
        // the half of the front nearest the middle (stored first) becomes the back (the back is empty)
        size_t k = (front.size() + 1) / 2;
        back.assign(front.rend() - k, front.rend());
        front.erase(front.begin(), front.begin() + k);
        rebuild();
    }

    LEETCODE_NO_SANITIZE void rebuild() {
        // every prefix hash of both halves, O(size()): each value moves at most once per half-emptying
        powers(max(front.size(), back.size()));
        P.clear();
        for (const T& v : back) P.push_back(P.empty() ? hval(v) : add(mul(P.back(), base), hval(v)));
        G.clear();
        for (size_t j = 0; j < front.size(); j++) G.push_back(add(j ? G.back() : 0, mul(hval(front[j]), pw[j])));
    }
};
