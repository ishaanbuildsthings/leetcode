// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries/agg-deque-max-or-and-lcm-product-mod/template.cpp
#include <bits/stdc++.h>
using namespace std;
using ll = long long;

// @operations: andAll append appendLeft getAll lcmAll maxAll orAll pointGet pop popLeft productAllMod size sumAll xorAll
// @data-structure-type: agg-deque
// @complexities:
//   andAll: 1
//   append: log(U)
//   appendLeft: log(U)
//   getAll: N
//   lcmAll: log(U)
//   maxAll: 1
//   orAll: 1
//   pointGet: 1
//   pop: log(U) amortized
//   popLeft: log(U) amortized
//   productAllMod: 1
//   size: 1
//   sumAll: 1
//   xorAll: 1
//   build: N
// @memory:
//   layout: none
//   node: front[1*N] back[1*N] Fmx[1*N] Bmx[1*N] Forr[1*N] Borr[1*N] Fan[1*N] Ban[1*N] Flc[1*N] Blc[1*N] Fpr[1*N] Bpr[1*N]
//   tags: none
//   other: none
//   note: the front half (stored last to first) and the back half hold the window; each half also keeps the max, OR, AND, LCM, product % MOD of its bottom..top, so the whole window's is one combine of the two tops; a pop that empties a half moves half of the other over and rebuilds both (amortized O(1)); the sum and xor are running totals
// Aggregate deque (two stacks): a window that grows and shrinks at both ends (sliding windows, deques) with the max,
// OR, AND, LCM, product % MOD, sum and xor of the whole window in O(1). Each half is a stack that keeps the aggregates
// of its bottom..top, so a push or pop is O(1) and the whole window is one combine of the two tops; a pop that empties
// its half moves half of the other over and rebuilds both, amortized O(1). The sum and xor are running totals. No point
// assign or range query: for those, use a seg tree or treap. All indices 0-based. A gcd or LCM is a
// Euclid run, O(log U), so a push and gcdAll / lcmAll cost that. lcmAll answers -1 once the LCM passes cap, so it
// can't overflow. cap defaults to the largest T (2^63 - 1 for long long); pass your own after arr and mod, e.g.
// AggDequeMaxOrAndLcmProductMod<long long> d(arr, 1000000007, 1000000000LL). Removing values is safe: each half
// keeps the LCM (or -1) of every prefix of its stack, so once the values that pushed it past cap are popped, lcmAll
// is exact again. The product is kept % MOD (pass mod to the constructor).
// T: int, long long, ...; the sum is kept in S (long long for small T).
template <typename T>
struct AggDequeMaxOrAndLcmProductMod {
    using S = conditional_t<(sizeof(T) < sizeof(long long)), long long, T>;
    using W = conditional_t<sizeof(T) <= 4, long long, __int128>;  // wide enough for a product of two residues
    // front: the first values, stored last to first; F*[j] over front[0..j], B*[k] over back[0..k]
    vector<T> front, back, Fmx, Bmx, Forr, Borr, Fan, Ban, Flc, Blc, Fpr, Bpr;
    S sm = 0;
    T xr = 0;
    T mod;
    T norm(W x) const { x %= mod; return T(x < 0 ? x + mod : x); }
    T cap;  // lcmAll is -1 past it

    // O(N) -- arr: the initial array, or left out to start empty; mod: for the product; cap: lcmAll is -1 past it
    explicit AggDequeMaxOrAndLcmProductMod(const vector<T>& arr = {}, T mod = 1000000007,
        T cap = numeric_limits<T>::max()) : mod(mod), cap(cap) {
        for (const T& v : arr) append(v);
    }

    // O(1) -- the current length of the window
    int size() const { return int(front.size() + back.size()); }

    // O(N) -- the whole window
    vector<T> getAll() const {
        vector<T> out(front.rbegin(), front.rend());
        out.insert(out.end(), back.begin(), back.end());
        return out;
    }

    // O(1) -- a[i]; needs 0 <= i < size(), else throws out_of_range
    T pointGet(int i) const {
        if (i < 0 || i >= size()) throw out_of_range("pointGet: needs 0 <= i < size()");
        int f = int(front.size());
        return i < f ? front[f - 1 - i] : back[i - f];
    }

    // O(log U) -- append v at the right end
    void append(T v) {
        sm += S(v);
        xr ^= v;
        push(Bmx, v, [](T a, T b) { return a > b ? a : b; }, [](T v) { return v; });
        push(Borr, v, [](T a, T b) { return a | b; }, [](T v) { return v; });
        push(Ban, v, [](T a, T b) { return a & b; }, [](T v) { return v; });
        push(Blc, v, [this](T a, T b) { return lcmOf(a, b); }, [this](T v) { return lcmOne(v); });
        push(Bpr, v, [this](T a, T b) { return T(W(a) * b % mod); }, [this](T v) { return norm(v); });
        back.push_back(v);
    }

    // O(log U) -- insert v at the left end (it becomes a[0]; every index shifts up by 1)
    void appendLeft(T v) {
        sm += S(v);
        xr ^= v;
        push(Fmx, v, [](T a, T b) { return a > b ? a : b; }, [](T v) { return v; });
        push(Forr, v, [](T a, T b) { return a | b; }, [](T v) { return v; });
        push(Fan, v, [](T a, T b) { return a & b; }, [](T v) { return v; });
        push(Flc, v, [this](T a, T b) { return lcmOf(a, b); }, [this](T v) { return lcmOne(v); });
        push(Fpr, v, [this](T a, T b) { return T(W(a) * b % mod); }, [this](T v) { return norm(v); });
        front.push_back(v);
    }

    // O(log U) amortized -- remove a[size()-1] and return it; needs size() >= 1, else throws out_of_range
    T pop() {
        if (size() < 1) throw out_of_range("pop: needs size() >= 1");
        if (back.empty()) moveToBack();
        Bmx.pop_back();
        Borr.pop_back();
        Ban.pop_back();
        Blc.pop_back();
        Bpr.pop_back();
        T v = back.back();
        back.pop_back();
        sm -= S(v);
        xr ^= v;
        return v;
    }

    // O(log U) amortized -- remove a[0] and return it (every index shifts down by 1); needs size() >= 1, else throws
    // out_of_range
    T popLeft() {
        if (size() < 1) throw out_of_range("popLeft: needs size() >= 1");
        if (front.empty()) moveToFront();
        Fmx.pop_back();
        Forr.pop_back();
        Fan.pop_back();
        Flc.pop_back();
        Fpr.pop_back();
        T v = front.back();
        front.pop_back();
        sm -= S(v);
        xr ^= v;
        return v;
    }

    // O(1) -- a[0] + ... + a[n-1]; needs n >= 1, else throws out_of_range
    S sumAll() const {
        if (size() < 1) throw out_of_range("sumAll: needs n >= 1");
        return sm;
    }

    // O(1) -- xor of the whole window; needs n >= 1, else throws out_of_range
    T xorAll() const {
        if (size() < 1) throw out_of_range("xorAll: needs n >= 1");
        return xr;
    }

    // O(1) -- max of the whole window (one combine of the two halves' tops); needs n >= 1, else throws out_of_range
    T maxAll() const {
        if (size() < 1) throw out_of_range("maxAll: needs n >= 1");
        if (Fmx.empty()) return Bmx.back();
        if (Bmx.empty()) return Fmx.back();
        T a = Fmx.back(), b = Bmx.back();
        return a > b ? a : b;
    }

    // O(1) -- OR of the whole window (one combine of the two halves' tops); needs n >= 1, else throws out_of_range
    T orAll() const {
        if (size() < 1) throw out_of_range("orAll: needs n >= 1");
        if (Forr.empty()) return Borr.back();
        if (Borr.empty()) return Forr.back();
        T a = Forr.back(), b = Borr.back();
        return a | b;
    }

    // O(1) -- AND of the whole window (one combine of the two halves' tops); needs n >= 1, else throws out_of_range
    T andAll() const {
        if (size() < 1) throw out_of_range("andAll: needs n >= 1");
        if (Fan.empty()) return Ban.back();
        if (Ban.empty()) return Fan.back();
        T a = Fan.back(), b = Ban.back();
        return a & b;
    }

    // O(log U) -- LCM of the whole window (one combine of the two halves' tops) or -1 once it passes cap; needs n >= 1,
    // else throws out_of_range
    T lcmAll() const {
        if (size() < 1) throw out_of_range("lcmAll: needs n >= 1");
        if (Flc.empty()) return Blc.back();
        if (Blc.empty()) return Flc.back();
        T a = Flc.back(), b = Blc.back();
        return lcmOf(a, b);
    }

    // O(1) -- product % MOD of the whole window (one combine of the two halves' tops); needs n >= 1, else throws
    // out_of_range
    T productAllMod() const {
        if (size() < 1) throw out_of_range("productAllMod: needs n >= 1");
        if (Fpr.empty()) return Bpr.back();
        if (Bpr.empty()) return Fpr.back();
        T a = Fpr.back(), b = Bpr.back();
        return T(W(a) * b % mod);
    }

    // ---- internals ----

    T lcmOne(T v) const { T x = v < 0 ? -v : v; return x > cap ? T(-1) : x; }  // |v|, or -1 past cap

    T lcmOf(T a, T b) const {  // 0 if either is 0 (an LCM with a 0 is 0); else -1 if either is past cap or the LCM is
        if (a == 0 || b == 0) return 0;
        if (a < 0 || b < 0) return -1;
        T r;
        if (__builtin_mul_overflow(a / gcd(a, b), b, &r) || r > cap) return -1;
        return r;
    }

    template <typename C, typename O>
    static void push(vector<T>& st, T v, C comb, O one) {
        st.push_back(st.empty() ? one(v) : comb(st.back(), one(v)));  // (one(v): |v| for gcd / LCM, v % MOD)
    }

    template <typename C, typename O>
    static void rebuildOne(vector<T>& st, const vector<T>& src, C comb, O one) {
        st.clear();
        for (const T& v : src) push(st, v, comb, one);
    }

    void moveToFront() {  // the back half's first half becomes the front (the front is empty)
        size_t k = (back.size() + 1) / 2;
        front.assign(back.rend() - k, back.rend());
        back.erase(back.begin(), back.begin() + k);
        rebuild();
    }

    void moveToBack() {  // the front half's values nearest the middle (stored first) become the back
        size_t k = (front.size() + 1) / 2;
        back.assign(front.rend() - k, front.rend());
        front.erase(front.begin(), front.begin() + k);
        rebuild();
    }

    void rebuild() {  // every half's aggregates, O(size())
        rebuildOne(Fmx, front, [](T a, T b) { return a > b ? a : b; }, [](T v) { return v; });
        rebuildOne(Bmx, back, [](T a, T b) { return a > b ? a : b; }, [](T v) { return v; });
        rebuildOne(Forr, front, [](T a, T b) { return a | b; }, [](T v) { return v; });
        rebuildOne(Borr, back, [](T a, T b) { return a | b; }, [](T v) { return v; });
        rebuildOne(Fan, front, [](T a, T b) { return a & b; }, [](T v) { return v; });
        rebuildOne(Ban, back, [](T a, T b) { return a & b; }, [](T v) { return v; });
        rebuildOne(Flc, front, [this](T a, T b) { return lcmOf(a, b); }, [this](T v) { return lcmOne(v); });
        rebuildOne(Blc, back, [this](T a, T b) { return lcmOf(a, b); }, [this](T v) { return lcmOne(v); });
        rebuildOne(Fpr, front, [this](T a, T b) { return T(W(a) * b % mod); }, [this](T v) { return norm(v); });
        rebuildOne(Bpr, back, [this](T a, T b) { return T(W(a) * b % mod); }, [this](T v) { return norm(v); });
    }
};
