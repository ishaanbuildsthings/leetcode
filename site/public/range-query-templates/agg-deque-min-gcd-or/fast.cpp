// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries/agg-deque-min-gcd-or/fast.cpp
#include <bits/stdc++.h>
using namespace std;
using ll = long long;

// @operations: append appendLeft gcdAll getAll minAll orAll pointGet pop popLeft size sumAll xorAll
// @data-structure-type: agg-deque
// @complexities:
//   append: log(U)
//   appendLeft: log(U)
//   gcdAll: log(U)
//   getAll: N
//   minAll: 1
//   orAll: 1
//   pointGet: 1
//   pop: log(U) amortized
//   popLeft: log(U) amortized
//   size: 1
//   sumAll: 1
//   xorAll: 1
//   build: N
// @memory:
//   layout: none
//   node: front[1*N] back[1*N] Fmn[1*N] Bmn[1*N] Fg[1*N] Bg[1*N] Forr[1*N] Borr[1*N]
//   tags: none
//   other: none
//   note: the front half (stored last to first) and the back half hold the window; each half also keeps the min, gcd, OR of its bottom..top, so the whole window's is one combine of the two tops; a pop that empties a half moves half of the other over and rebuilds both (amortized O(1)); the sum and xor are running totals
// Aggregate deque (two stacks): a window that grows and shrinks at both ends (sliding windows, deques) with the min,
// gcd, OR, sum and xor of the whole window in O(1). Each half is a stack that keeps the aggregates of its bottom..top,
// so a push or pop is O(1) and the whole window is one combine of the two tops; a pop that empties its half moves half
// of the other over and rebuilds both, amortized O(1). The sum and xor are running totals. No point assign or range
// query: for those, use a seg tree or treap. All indices 0-based. A gcd or LCM is a Euclid run,
// O(log U), so a push and gcdAll / lcmAll cost that.
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
struct AggDequeMinGcdOr {
    using S = conditional_t<(sizeof(T) < sizeof(long long)), long long, T>;
    // front: the first values, stored last to first; F*[j] over front[0..j], B*[k] over back[0..k]
    HotVector<T> front, back, Fmn, Bmn, Fg, Bg, Forr, Borr;
    S sm = 0;
    T xr = 0;

    // O(N) -- arr: the initial array, or left out to start empty
    explicit AggDequeMinGcdOr(const vector<T>& arr = {}) {
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
        push(Bmn, v, [](T a, T b) { return a < b ? a : b; }, [](T v) { return v; });
        push(Bg, v, [](T a, T b) { return gcd(a, b); }, [](T v) { return gcd(v, T(0)); });
        push(Borr, v, [](T a, T b) { return a | b; }, [](T v) { return v; });
        back.push_back(v);
    }

    // O(log U) -- insert v at the left end (it becomes a[0]; every index shifts up by 1)
    LEETCODE_NO_SANITIZE void appendLeft(T v) {
        sm += S(v);
        xr ^= v;
        push(Fmn, v, [](T a, T b) { return a < b ? a : b; }, [](T v) { return v; });
        push(Fg, v, [](T a, T b) { return gcd(a, b); }, [](T v) { return gcd(v, T(0)); });
        push(Forr, v, [](T a, T b) { return a | b; }, [](T v) { return v; });
        front.push_back(v);
    }

    // O(log U) amortized -- remove a[size()-1] and return it; needs size() >= 1, else throws out_of_range
    LEETCODE_NO_SANITIZE T pop() {
        if (size() < 1) throw out_of_range("pop: needs size() >= 1");
        if (back.empty()) moveToBack();
        Bmn.pop_back();
        Bg.pop_back();
        Borr.pop_back();
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
        Fmn.pop_back();
        Fg.pop_back();
        Forr.pop_back();
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

    // O(1) -- min of the whole window (one combine of the two halves' tops); needs n >= 1, else throws out_of_range
    LEETCODE_NO_SANITIZE T minAll() const {
        if (size() < 1) throw out_of_range("minAll: needs n >= 1");
        if (Fmn.empty()) return Bmn.back();
        if (Bmn.empty()) return Fmn.back();
        T a = Fmn.back(), b = Bmn.back();
        return a < b ? a : b;
    }

    // O(log U) -- gcd of the whole window (one combine of the two halves' tops); needs n >= 1, else throws out_of_range
    LEETCODE_NO_SANITIZE T gcdAll() const {
        if (size() < 1) throw out_of_range("gcdAll: needs n >= 1");
        if (Fg.empty()) return Bg.back();
        if (Bg.empty()) return Fg.back();
        T a = Fg.back(), b = Bg.back();
        return gcd(a, b);
    }

    // O(1) -- OR of the whole window (one combine of the two halves' tops); needs n >= 1, else throws out_of_range
    LEETCODE_NO_SANITIZE T orAll() const {
        if (size() < 1) throw out_of_range("orAll: needs n >= 1");
        if (Forr.empty()) return Borr.back();
        if (Borr.empty()) return Forr.back();
        T a = Forr.back(), b = Borr.back();
        return a | b;
    }

    // ---- internals ----

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
        rebuildOne(Fmn, front, [](T a, T b) { return a < b ? a : b; }, [](T v) { return v; });
        rebuildOne(Bmn, back, [](T a, T b) { return a < b ? a : b; }, [](T v) { return v; });
        rebuildOne(Fg, front, [](T a, T b) { return gcd(a, b); }, [](T v) { return gcd(v, T(0)); });
        rebuildOne(Bg, back, [](T a, T b) { return gcd(a, b); }, [](T v) { return gcd(v, T(0)); });
        rebuildOne(Forr, front, [](T a, T b) { return a | b; }, [](T v) { return v; });
        rebuildOne(Borr, back, [](T a, T b) { return a | b; }, [](T v) { return v; });
    }
};
