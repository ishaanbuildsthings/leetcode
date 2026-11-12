// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries/agg-deque-gcd-and-lcm/fast.cpp
#include <bits/stdc++.h>
using namespace std;
using ll = long long;

// @operations: andAll append appendLeft gcdAll getAll lcmAll pointGet pop popLeft size sumAll xorAll
// @data-structure-type: agg-deque
// @complexities:
//   andAll: 1
//   append: log(U)
//   appendLeft: log(U)
//   gcdAll: log(U)
//   getAll: N
//   lcmAll: log(U)
//   pointGet: 1
//   pop: log(U) amortized
//   popLeft: log(U) amortized
//   size: 1
//   sumAll: 1
//   xorAll: 1
//   build: N
// @memory:
//   layout: none
//   node: front[1*N] back[1*N] Fg[1*N] Bg[1*N] Fan[1*N] Ban[1*N] Flc[1*N] Blc[1*N]
//   tags: none
//   other: none
//   note: the front half (stored last to first) and the back half hold the window; each half also keeps the gcd, AND, LCM of its bottom..top, so the whole window's is one combine of the two tops; a pop that empties a half moves half of the other over and rebuilds both (amortized O(1)); the sum and xor are running totals
// Aggregate deque (two stacks): a window that grows and shrinks at both ends (sliding windows, deques) with the gcd,
// AND, LCM, sum and xor of the whole window in O(1). Each half is a stack that keeps the aggregates of its bottom..top,
// so a push or pop is O(1) and the whole window is one combine of the two tops; a pop that empties its half moves half
// of the other over and rebuilds both, amortized O(1). The sum and xor are running totals. No point assign or range
// query: for those, use a seg tree or treap. All indices 0-based. A gcd or LCM is a Euclid run,
// O(log U), so a push and gcdAll / lcmAll cost that. lcmAll answers -1 once the LCM passes cap, so it can't
// overflow. cap defaults to the largest T (2^63 - 1 for long long); pass your own after arr, e.g.
// AggDequeGcdAndLcm<long long> d(arr, 1000000000LL). Removing values is safe: each half keeps the LCM (or -1) of
// every prefix of its stack, so once the values that pushed it past cap are popped, lcmAll is exact again.
// T: int, long long, ...; the sum is kept in S (long long for small T).
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
struct AggDequeGcdAndLcm {
    using S = conditional_t<(sizeof(T) < sizeof(long long)), long long, T>;
    // front: the first values, stored last to first; F*[j] over front[0..j], B*[k] over back[0..k]
    HotVector<T> front, back, Fg, Bg, Fan, Ban, Flc, Blc;
    S sm = 0;
    T xr = 0;
    T cap;  // lcmAll is -1 past it

    // O(N) -- arr: the initial array, or left out to start empty; cap: lcmAll is -1 past it
    explicit AggDequeGcdAndLcm(const vector<T>& arr = {}, T cap = numeric_limits<T>::max()) : cap(cap) {
        for (const T& v : arr) append(v);
    }

    // O(1) -- the current length of the window
    LEETCODE_NO_SANITIZE int size() const { return int(front.size() + back.size()); }

    // O(N) -- the whole window
    LEETCODE_NO_SANITIZE vector<T> getAll() const {
        vector<T> out(front.rbegin(), front.rend());
        out.insert(out.end(), back.begin(), back.end());
        return out;
    }

    // O(1) -- a[i]; needs 0 <= i < size(), else throws out_of_range
    LEETCODE_NO_SANITIZE T pointGet(int i) const {
        if (i < 0 || i >= size()) throw out_of_range("pointGet: needs 0 <= i < size()");
        int f = int(front.size());
        return i < f ? front[f - 1 - i] : back[i - f];
    }

    // O(log U) -- append v at the right end
    LEETCODE_NO_SANITIZE void append(T v) {
        sm += S(v);
        xr ^= v;
        push(Bg, v, [](T a, T b) { return gcd(a, b); }, [](T v) { return gcd(v, T(0)); });
        push(Ban, v, [](T a, T b) { return a & b; }, [](T v) { return v; });
        push(Blc, v, [this](T a, T b) { return lcmOf(a, b); }, [this](T v) { return lcmOne(v); });
        back.push_back(v);
    }

    // O(log U) -- insert v at the left end (it becomes a[0]; every index shifts up by 1)
    LEETCODE_NO_SANITIZE void appendLeft(T v) {
        sm += S(v);
        xr ^= v;
        push(Fg, v, [](T a, T b) { return gcd(a, b); }, [](T v) { return gcd(v, T(0)); });
        push(Fan, v, [](T a, T b) { return a & b; }, [](T v) { return v; });
        push(Flc, v, [this](T a, T b) { return lcmOf(a, b); }, [this](T v) { return lcmOne(v); });
        front.push_back(v);
    }

    // O(log U) amortized -- remove a[size()-1] and return it; needs size() >= 1, else throws out_of_range
    LEETCODE_NO_SANITIZE T pop() {
        if (size() < 1) throw out_of_range("pop: needs size() >= 1");
        if (back.empty()) moveToBack();
        Bg.pop_back();
        Ban.pop_back();
        Blc.pop_back();
        T v = back.back();
        back.pop_back();
        sm -= S(v);
        xr ^= v;
        return v;
    }

    // O(log U) amortized -- remove a[0] and return it (every index shifts down by 1); needs size() >= 1, else throws
    // out_of_range
    LEETCODE_NO_SANITIZE T popLeft() {
        if (size() < 1) throw out_of_range("popLeft: needs size() >= 1");
        if (front.empty()) moveToFront();
        Fg.pop_back();
        Fan.pop_back();
        Flc.pop_back();
        T v = front.back();
        front.pop_back();
        sm -= S(v);
        xr ^= v;
        return v;
    }

    // O(1) -- a[0] + ... + a[n-1]; needs n >= 1, else throws out_of_range
    LEETCODE_NO_SANITIZE S sumAll() const {
        if (size() < 1) throw out_of_range("sumAll: needs n >= 1");
        return sm;
    }

    // O(1) -- xor of the whole window; needs n >= 1, else throws out_of_range
    LEETCODE_NO_SANITIZE T xorAll() const {
        if (size() < 1) throw out_of_range("xorAll: needs n >= 1");
        return xr;
    }

    // O(log U) -- gcd of the whole window (one combine of the two halves' tops); needs n >= 1, else throws out_of_range
    LEETCODE_NO_SANITIZE T gcdAll() const {
        if (size() < 1) throw out_of_range("gcdAll: needs n >= 1");
        if (Fg.empty()) return Bg.back();
        if (Bg.empty()) return Fg.back();
        T a = Fg.back(), b = Bg.back();
        return gcd(a, b);
    }

    // O(1) -- AND of the whole window (one combine of the two halves' tops); needs n >= 1, else throws out_of_range
    LEETCODE_NO_SANITIZE T andAll() const {
        if (size() < 1) throw out_of_range("andAll: needs n >= 1");
        if (Fan.empty()) return Ban.back();
        if (Ban.empty()) return Fan.back();
        T a = Fan.back(), b = Ban.back();
        return a & b;
    }

    // O(log U) -- LCM of the whole window (one combine of the two halves' tops) or -1 once it passes cap; needs n >= 1,
    // else throws out_of_range
    LEETCODE_NO_SANITIZE T lcmAll() const {
        if (size() < 1) throw out_of_range("lcmAll: needs n >= 1");
        if (Flc.empty()) return Blc.back();
        if (Blc.empty()) return Flc.back();
        T a = Flc.back(), b = Blc.back();
        return lcmOf(a, b);
    }

    // ---- internals ----

    // |v|, or -1 past cap
    LEETCODE_NO_SANITIZE T lcmOne(T v) const { T x = v < 0 ? -v : v; return x > cap ? T(-1) : x; }

    LEETCODE_NO_SANITIZE T lcmOf(T a, T b) const {
        // 0 if either is 0 (an LCM with a 0 is 0); else -1 if either is past cap or the LCM is
        if (a == 0 || b == 0) return 0;
        if (a < 0 || b < 0) return -1;
        T r;
        if (__builtin_mul_overflow(a / gcd(a, b), b, &r) || r > cap) return -1;
        return r;
    }

    template <typename C, typename O>
    LEETCODE_NO_SANITIZE static void push(vector<T>& st, T v, C comb, O one) {
        st.push_back(st.empty() ? one(v) : comb(st.back(), one(v)));  // (one(v): |v| for gcd / LCM, v % MOD)
    }

    template <typename C, typename O>
    LEETCODE_NO_SANITIZE static void rebuildOne(vector<T>& st, const vector<T>& src, C comb, O one) {
        st.clear();
        for (const T& v : src) push(st, v, comb, one);
    }

    LEETCODE_NO_SANITIZE void moveToFront() {  // the back half's first half becomes the front (the front is empty)
        size_t k = (back.size() + 1) / 2;
        front.assign(back.rend() - k, back.rend());
        back.erase(back.begin(), back.begin() + k);
        rebuild();
    }

    LEETCODE_NO_SANITIZE void moveToBack() {
        // the front half's values nearest the middle (stored first) become the back
        size_t k = (front.size() + 1) / 2;
        back.assign(front.rend() - k, front.rend());
        front.erase(front.begin(), front.begin() + k);
        rebuild();
    }

    LEETCODE_NO_SANITIZE void rebuild() {  // every half's aggregates, O(size())
        rebuildOne(Fg, front, [](T a, T b) { return gcd(a, b); }, [](T v) { return gcd(v, T(0)); });
        rebuildOne(Bg, back, [](T a, T b) { return gcd(a, b); }, [](T v) { return gcd(v, T(0)); });
        rebuildOne(Fan, front, [](T a, T b) { return a & b; }, [](T v) { return v; });
        rebuildOne(Ban, back, [](T a, T b) { return a & b; }, [](T v) { return v; });
        rebuildOne(Flc, front, [this](T a, T b) { return lcmOf(a, b); }, [this](T v) { return lcmOne(v); });
        rebuildOne(Blc, back, [this](T a, T b) { return lcmOf(a, b); }, [this](T v) { return lcmOne(v); });
    }
};
