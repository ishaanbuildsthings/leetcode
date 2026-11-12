// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries/agg-deque-min-max-or-and-product-mod/fast.cpp
#include <bits/stdc++.h>
using namespace std;
using ll = long long;

// @operations: andAll append appendLeft getAll maxAll minAll orAll pointGet pop popLeft productAllMod size sumAll xorAll
// @data-structure-type: agg-deque
// @complexities:
//   andAll: 1
//   append: 1
//   appendLeft: 1
//   getAll: N
//   maxAll: 1
//   minAll: 1
//   orAll: 1
//   pointGet: 1
//   pop: 1 amortized
//   popLeft: 1 amortized
//   productAllMod: 1
//   size: 1
//   sumAll: 1
//   xorAll: 1
//   build: N
// @memory:
//   layout: none
//   node: front[1*N] back[1*N] Fmn[1*N] Bmn[1*N] Fmx[1*N] Bmx[1*N] Forr[1*N] Borr[1*N] Fan[1*N] Ban[1*N] Fpr[1*N] Bpr[1*N]
//   tags: none
//   other: none
//   note: the front half (stored last to first) and the back half hold the window; each half also keeps the min, max, OR, AND, product % MOD of its bottom..top, so the whole window's is one combine of the two tops; a pop that empties a half moves half of the other over and rebuilds both (amortized O(1)); the sum and xor are running totals
// Aggregate deque (two stacks): a window that grows and shrinks at both ends (sliding windows, deques) with the min,
// max, OR, AND, product % MOD, sum and xor of the whole window in O(1). Each half is a stack that keeps the aggregates
// of its bottom..top, so a push or pop is O(1) and the whole window is one combine of the two tops; a pop that empties
// its half moves half of the other over and rebuilds both, amortized O(1). The sum and xor are running totals. No point
// assign or range query: for those, use a seg tree or treap. All indices 0-based. The product is kept % MOD (pass mod
// to the constructor).
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
struct AggDequeMinMaxOrAndProductMod {
    using S = conditional_t<(sizeof(T) < sizeof(long long)), long long, T>;
    using W = conditional_t<sizeof(T) <= 4, long long, __int128>;  // wide enough for a product of two residues
    // front: the first values, stored last to first; F*[j] over front[0..j], B*[k] over back[0..k]
    HotVector<T> front, back, Fmn, Bmn, Fmx, Bmx, Forr, Borr, Fan, Ban, Fpr, Bpr;
    S sm = 0;
    T xr = 0;
    T mod;
    LEETCODE_NO_SANITIZE T norm(W x) const { x %= mod; return T(x < 0 ? x + mod : x); }

    // O(N) -- arr: the initial array, or left out to start empty; mod: for the product
    explicit AggDequeMinMaxOrAndProductMod(const vector<T>& arr = {}, T mod = 1000000007) : mod(mod) {
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

    // O(1) -- append v at the right end
    LEETCODE_NO_SANITIZE void append(T v) {
        sm += S(v);
        xr ^= v;
        push(Bmn, v, [](T a, T b) { return a < b ? a : b; }, [](T v) { return v; });
        push(Bmx, v, [](T a, T b) { return a > b ? a : b; }, [](T v) { return v; });
        push(Borr, v, [](T a, T b) { return a | b; }, [](T v) { return v; });
        push(Ban, v, [](T a, T b) { return a & b; }, [](T v) { return v; });
        push(Bpr, v, [this](T a, T b) { return T(W(a) * b % mod); }, [this](T v) { return norm(v); });
        back.push_back(v);
    }

    // O(1) -- insert v at the left end (it becomes a[0]; every index shifts up by 1)
    LEETCODE_NO_SANITIZE void appendLeft(T v) {
        sm += S(v);
        xr ^= v;
        push(Fmn, v, [](T a, T b) { return a < b ? a : b; }, [](T v) { return v; });
        push(Fmx, v, [](T a, T b) { return a > b ? a : b; }, [](T v) { return v; });
        push(Forr, v, [](T a, T b) { return a | b; }, [](T v) { return v; });
        push(Fan, v, [](T a, T b) { return a & b; }, [](T v) { return v; });
        push(Fpr, v, [this](T a, T b) { return T(W(a) * b % mod); }, [this](T v) { return norm(v); });
        front.push_back(v);
    }

    // O(1) amortized -- remove a[size()-1] and return it; needs size() >= 1, else throws out_of_range
    LEETCODE_NO_SANITIZE T pop() {
        if (size() < 1) throw out_of_range("pop: needs size() >= 1");
        if (back.empty()) moveToBack();
        Bmn.pop_back();
        Bmx.pop_back();
        Borr.pop_back();
        Ban.pop_back();
        Bpr.pop_back();
        T v = back.back();
        back.pop_back();
        sm -= S(v);
        xr ^= v;
        return v;
    }

    // O(1) amortized -- remove a[0] and return it (every index shifts down by 1); needs size() >= 1, else throws
    // out_of_range
    LEETCODE_NO_SANITIZE T popLeft() {
        if (size() < 1) throw out_of_range("popLeft: needs size() >= 1");
        if (front.empty()) moveToFront();
        Fmn.pop_back();
        Fmx.pop_back();
        Forr.pop_back();
        Fan.pop_back();
        Fpr.pop_back();
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

    // O(1) -- max of the whole window (one combine of the two halves' tops); needs n >= 1, else throws out_of_range
    LEETCODE_NO_SANITIZE T maxAll() const {
        if (size() < 1) throw out_of_range("maxAll: needs n >= 1");
        if (Fmx.empty()) return Bmx.back();
        if (Bmx.empty()) return Fmx.back();
        T a = Fmx.back(), b = Bmx.back();
        return a > b ? a : b;
    }

    // O(1) -- OR of the whole window (one combine of the two halves' tops); needs n >= 1, else throws out_of_range
    LEETCODE_NO_SANITIZE T orAll() const {
        if (size() < 1) throw out_of_range("orAll: needs n >= 1");
        if (Forr.empty()) return Borr.back();
        if (Borr.empty()) return Forr.back();
        T a = Forr.back(), b = Borr.back();
        return a | b;
    }

    // O(1) -- AND of the whole window (one combine of the two halves' tops); needs n >= 1, else throws out_of_range
    LEETCODE_NO_SANITIZE T andAll() const {
        if (size() < 1) throw out_of_range("andAll: needs n >= 1");
        if (Fan.empty()) return Ban.back();
        if (Ban.empty()) return Fan.back();
        T a = Fan.back(), b = Ban.back();
        return a & b;
    }

    // O(1) -- product % MOD of the whole window (one combine of the two halves' tops); needs n >= 1, else throws
    // out_of_range
    LEETCODE_NO_SANITIZE T productAllMod() const {
        if (size() < 1) throw out_of_range("productAllMod: needs n >= 1");
        if (Fpr.empty()) return Bpr.back();
        if (Bpr.empty()) return Fpr.back();
        T a = Fpr.back(), b = Bpr.back();
        return T(W(a) * b % mod);
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
        rebuildOne(Fmx, front, [](T a, T b) { return a > b ? a : b; }, [](T v) { return v; });
        rebuildOne(Bmx, back, [](T a, T b) { return a > b ? a : b; }, [](T v) { return v; });
        rebuildOne(Forr, front, [](T a, T b) { return a | b; }, [](T v) { return v; });
        rebuildOne(Borr, back, [](T a, T b) { return a | b; }, [](T v) { return v; });
        rebuildOne(Fan, front, [](T a, T b) { return a & b; }, [](T v) { return v; });
        rebuildOne(Ban, back, [](T a, T b) { return a & b; }, [](T v) { return v; });
        rebuildOne(Fpr, front, [this](T a, T b) { return T(W(a) * b % mod); }, [this](T v) { return norm(v); });
        rebuildOne(Bpr, back, [this](T a, T b) { return T(W(a) * b % mod); }, [this](T v) { return norm(v); });
    }
};
