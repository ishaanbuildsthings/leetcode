// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries/agg-deque-min-max/template.cpp
#include <bits/stdc++.h>
using namespace std;
using ll = long long;

// @operations: append appendLeft getAll maxAll minAll pointGet pop popLeft size sumAll xorAll
// @data-structure-type: agg-deque
// @complexities:
//   append: 1
//   appendLeft: 1
//   getAll: N
//   maxAll: 1
//   minAll: 1
//   pointGet: 1
//   pop: 1 amortized
//   popLeft: 1 amortized
//   size: 1
//   sumAll: 1
//   xorAll: 1
//   build: N
// @memory:
//   layout: none
//   node: front[1*N] back[1*N] Fmn[1*N] Bmn[1*N] Fmx[1*N] Bmx[1*N]
//   tags: none
//   other: none
//   note: the front half (stored last to first) and the back half hold the window; each half also keeps the min, max of its bottom..top, so the whole window's is one combine of the two tops; a pop that empties a half moves half of the other over and rebuilds both (amortized O(1)); the sum and xor are running totals
// Aggregate deque (two stacks): a window that grows and shrinks at both ends (sliding windows, deques) with the min,
// max, sum and xor of the whole window in O(1). Each half is a stack that keeps the aggregates of its bottom..top,
// so a push or pop is O(1) and the whole window is one combine of the two tops; a pop that empties its half moves
// half of the other over and rebuilds both, amortized O(1). The sum and xor are running totals. No point assign or
// range query: for those, use a seg tree or treap. All indices 0-based.
// T: int, long long, ...; the sum is kept in S (long long for small T).
template <typename T>
struct AggDequeMinMax {
    using S = conditional_t<(sizeof(T) < sizeof(long long)), long long, T>;
    // front: the first values, stored last to first; F*[j] over front[0..j], B*[k] over back[0..k]
    vector<T> front, back, Fmn, Bmn, Fmx, Bmx;
    S sm = 0;
    T xr = 0;

    // O(N) -- arr: the initial array, or left out to start empty
    explicit AggDequeMinMax(const vector<T>& arr = {}) {
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

    // O(1) -- append v at the right end
    void append(T v) {
        sm += S(v);
        xr ^= v;
        push(Bmn, v, [](T a, T b) { return a < b ? a : b; }, [](T v) { return v; });
        push(Bmx, v, [](T a, T b) { return a > b ? a : b; }, [](T v) { return v; });
        back.push_back(v);
    }

    // O(1) -- insert v at the left end (it becomes a[0]; every index shifts up by 1)
    void appendLeft(T v) {
        sm += S(v);
        xr ^= v;
        push(Fmn, v, [](T a, T b) { return a < b ? a : b; }, [](T v) { return v; });
        push(Fmx, v, [](T a, T b) { return a > b ? a : b; }, [](T v) { return v; });
        front.push_back(v);
    }

    // O(1) amortized -- remove a[size()-1] and return it; needs size() >= 1, else throws out_of_range
    T pop() {
        if (size() < 1) throw out_of_range("pop: needs size() >= 1");
        if (back.empty()) moveToBack();
        Bmn.pop_back();
        Bmx.pop_back();
        T v = back.back();
        back.pop_back();
        sm -= S(v);
        xr ^= v;
        return v;
    }

    // O(1) amortized -- remove a[0] and return it (every index shifts down by 1); needs size() >= 1, else throws
    // out_of_range
    T popLeft() {
        if (size() < 1) throw out_of_range("popLeft: needs size() >= 1");
        if (front.empty()) moveToFront();
        Fmn.pop_back();
        Fmx.pop_back();
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

    // O(1) -- min of the whole window (one combine of the two halves' tops); needs n >= 1, else throws out_of_range
    T minAll() const {
        if (size() < 1) throw out_of_range("minAll: needs n >= 1");
        if (Fmn.empty()) return Bmn.back();
        if (Bmn.empty()) return Fmn.back();
        T a = Fmn.back(), b = Bmn.back();
        return a < b ? a : b;
    }

    // O(1) -- max of the whole window (one combine of the two halves' tops); needs n >= 1, else throws out_of_range
    T maxAll() const {
        if (size() < 1) throw out_of_range("maxAll: needs n >= 1");
        if (Fmx.empty()) return Bmx.back();
        if (Bmx.empty()) return Fmx.back();
        T a = Fmx.back(), b = Bmx.back();
        return a > b ? a : b;
    }

    // ---- internals ----

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
        rebuildOne(Fmn, front, [](T a, T b) { return a < b ? a : b; }, [](T v) { return v; });
        rebuildOne(Bmn, back, [](T a, T b) { return a < b ? a : b; }, [](T v) { return v; });
        rebuildOne(Fmx, front, [](T a, T b) { return a > b ? a : b; }, [](T v) { return v; });
        rebuildOne(Bmx, back, [](T a, T b) { return a > b ? a : b; }, [](T v) { return v; });
    }
};
