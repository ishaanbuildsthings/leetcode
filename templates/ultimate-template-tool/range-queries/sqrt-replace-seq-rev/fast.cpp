// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries/sqrt-replace-seq-rev/fast.cpp
#include <bits/stdc++.h>
using namespace std;
using ll = long long;

// @operations: append appendLeft countOccurrences cut getAll insertAt insertCopiesAt leftmostIndexOf leftmostIndexOfInRange merge paste pointAssign pointGet pop popLeft rangeAssign rangeReplace rangeReverse rangeRotateLeft rangeRotateRight rightmostIndexOf rightmostIndexOfInRange size split trisect
// @data-structure-type: sqrt
// @letters: same
// @complexities:
//   append: sqrt(N) amortized
//   appendLeft: sqrt(N) amortized
//   countOccurrences: sqrt(N) amortized
//   cut: sqrt(N) amortized
//   getAll: N
//   insertAt: sqrt(N) amortized
//   insertCopiesAt: sqrt(N) amortized
//   leftmostIndexOf: sqrt(N) amortized
//   leftmostIndexOfInRange: sqrt(N) amortized
//   merge: sqrt(N) amortized
//   paste: sqrt(N) amortized
//   pointAssign: sqrt(N) amortized
//   pointGet: sqrt(N)
//   rangeAssign: sqrt(N) amortized
//   rangeReplace: sqrt(N) amortized
//   rangeReverse: sqrt(N) amortized
//   rangeRotateLeft: sqrt(N) amortized
//   rangeRotateRight: sqrt(N) amortized
//   rightmostIndexOf: sqrt(N) amortized
//   rightmostIndexOfInRange: sqrt(N) amortized
//   split: sqrt(N) amortized
//   trisect: sqrt(N) amortized
//   size: 1
//   pop: sqrt(N) amortized
//   popLeft: sqrt(N) amortized
//   build: N
// @memory:
//   layout: none
//   node: cls[1*N] par[2*N] val[2*N] cnt[2*N] where[1*N]
//   tags: rev[1*sqrt(N)]
//   other: none
//   note: blocks of about sqrt(N) values; each block's values are classes joined by a union-find (union by size, path halving: O(alpha), counted as O(1)); where maps each value in the block to its class; values are hashed, so any values work

// Blocks whose values form a union-find of classes (mass change, CF 911G, in O(sqrt N), with sequence edits): the
// array is cut into blocks of about sqrt(N) values. Inside a block equal values form a class, and the classes are
// joined by a union-find: rangeReplace(l, r, x, y) on a whole block renames x's class to y, or joins it into y's, in
// O(1); rangeAssign joins every class. Only the (at most two) partly covered blocks are touched value by value. Any
// values work (each block hashes them). The blocks form a list you can insert into anywhere, reverse, rotate, cut
// pieces out of (that is how to erase) and paste back; a[i] then walks the list (O(sqrt N)). All indices 0-based,
// ranges inclusive [l, r], an index always the position in the CURRENT array; searches return -1 when nothing
// qualifies.
// T: any type with a hash (int, long long, char, ...)

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
    LEETCODE_NO_SANITIZE_INLINE typename vector<U>::const_reference operator[](size_t i) const { return this->_M_impl._M_start[i]; }
    LEETCODE_NO_SANITIZE_INLINE size_t size() const { return size_t(this->_M_impl._M_finish - this->_M_impl._M_start); }
#endif
};

template <typename T>
struct SqrtReplace {
    struct SafeHash {  // splitmix64 with a seed random per run (the default hash of an integer is easy to attack)
        size_t operator()(const T& x) const {
            static const unsigned long long seed = chrono::steady_clock::now().time_since_epoch().count();
            unsigned long long z = (unsigned long long)x + seed + 0x9e3779b97f4a7c15ULL;
            z = (z ^ (z >> 30)) * 0xbf58476d1ce4e5b9ULL;
            z = (z ^ (z >> 27)) * 0x94d049bb133111ebULL;
            return z ^ (z >> 31);
        }
    };
    // a run of the array: cls[k] is the class of its k-th value (read backwards when rev). Classes form a union-find
    // (par); a root class holds its value (val) and how many of the block's values are in it (cnt). where: value -> root
    struct Block {
        vector<int> cls, par, cnt;
        vector<T> val;
        unordered_map<T, int, SafeHash> where;
        bool rev = false;

        Block() {}
        explicit Block(const vector<T>& vals) { build(vals); }

        void build(const vector<T>& vals) {  // O(len) -- the classes from scratch
            cls.clear(), par.clear(), cnt.clear(), val.clear(), where.clear();
            rev = false;
            for (const T& v : vals) {
                auto [it, fresh] = where.try_emplace(v, (int)par.size());
                if (fresh) par.push_back(it->second), val.push_back(v), cnt.push_back(0);
                cnt[it->second]++;
                cls.push_back(it->second);
            }
        }

        int size() const { return (int)cls.size(); }

        int find(int c) {  // c's root class (path halving)
            while (par[c] != c) c = par[c] = par[par[c]];
            return c;
        }

        T get(int k) {  // the k-th value
            if (rev) k = size() - 1 - k;
            return val[find(cls[k])];
        }

        vector<T> values() {  // every value, in order
            vector<T> out;
            out.reserve(cls.size());
            for (int c : cls) out.push_back(val[find(c)]);
            if (rev) reverse(out.begin(), out.end());
            return out;
        }

        int count(const T& x) const {  // how many x's
            auto it = where.find(x);
            return it == where.end() ? 0 : cnt[it->second];
        }

        void replace(const T& x, const T& y) {  // O(1) -- every x becomes y: x's class is renamed, or joined to y's
            auto it = where.find(x);
            if (it == where.end()) return;
            int cx = it->second;
            where.erase(it);
            auto jt = where.find(y);
            if (jt == where.end()) {
                val[cx] = y, where[y] = cx;
                return;
            }
            int cy = jt->second;
            if (cnt[cx] > cnt[cy]) swap(cx, cy);  // (union by size)
            par[cx] = cy, cnt[cy] += cnt[cx], val[cy] = y, jt->second = cy;
        }

        // every value becomes v: every class joined into one (O(1) amortized: each join removes one)
        void assignAll(const T& v) {
            int r = -1;
            for (auto& [x, c] : where)
                if (r == -1 || cnt[c] > cnt[r]) r = c;
            for (auto& [x, c] : where)
                if (c != r) par[c] = r, cnt[r] += cnt[c];
            val[r] = v;
            where.clear();
            where[v] = r;
        }

        void assign(int k, const T& v) {  // O(1) amortized -- the k-th value becomes v (a class of its own if v is new here)
            if (rev) k = size() - 1 - k;
            int c = find(cls[k]);
            if (val[c] == v) return;
            if (!--cnt[c]) where.erase(val[c]);
            auto [it, fresh] = where.try_emplace(v, (int)par.size());
            if (fresh) par.push_back(it->second), val.push_back(v), cnt.push_back(0);
            cnt[it->second]++;
            cls[k] = it->second;
            if ((int)par.size() > 2 * size() + 8) build(values());  // (many dead classes: start over, paid for by the assigns)
        }
    };

    HotVector<Block> blocks;
    int n = 0, B = 1;

    SqrtReplace() {}  // (an empty one)

    // O(N) -- arr: the initial array
    explicit SqrtReplace(const vector<T>& arr) { fill(arr); }

    // O(1) -- the current length of the array
    LEETCODE_NO_SANITIZE int size() const { return n; }

    // O(N) -- the whole current array
    LEETCODE_NO_SANITIZE vector<T> getAll() {
        vector<T> out;
        out.reserve(n);
        for (Block& b : blocks) {
            vector<T> v = b.values();
            out.insert(out.end(), v.begin(), v.end());
        }
        return out;
    }

    // O(sqrt(N)) -- a[i]; needs 0 <= i < size(), else throws out_of_range
    LEETCODE_NO_SANITIZE T pointGet(int i) {
        if (i < 0 || i >= size()) throw out_of_range("pointGet: needs 0 <= i < size()");
        auto [j, k] = locate(i);
        return blocks[j].get(k);
    }

    // O(sqrt(N)) -- a[i] = v; needs 0 <= i < size(), else throws out_of_range
    LEETCODE_NO_SANITIZE void pointAssign(int i, const T& v) {
        if (i < 0 || i >= size()) throw out_of_range("pointAssign: needs 0 <= i < size()");
        auto [j, k] = locate(i);
        blocks[j].assign(k, v);
    }

    // O(sqrt(N)) amortized -- every a[i] == x with l <= i <= r becomes y; needs 0 <= l <= r < size(), else throws
    // out_of_range
    LEETCODE_NO_SANITIZE void rangeReplace(int l, int r, const T& x, const T& y) {
        if (l < 0 || l > r || r >= size()) throw out_of_range("rangeReplace: needs 0 <= l <= r < size()");
        if (x == y) return;
        span(l, r, [&](Block& b, int lo, int hi, bool whole, int) {
            if (whole) b.replace(x, y);
            else
                for (int k = lo; k <= hi; k++)
                    if (b.get(k) == x) b.assign(k, y);
            return false;
        });
    }

    // O(sqrt(N)) amortized -- a[l..r] = v; needs 0 <= l <= r < size(), else throws out_of_range
    LEETCODE_NO_SANITIZE void rangeAssign(int l, int r, const T& v) {
        if (l < 0 || l > r || r >= size()) throw out_of_range("rangeAssign: needs 0 <= l <= r < size()");
        span(l, r, [&](Block& b, int lo, int hi, bool whole, int) {
            if (whole) b.assignAll(v);
            else
                for (int k = lo; k <= hi; k++) b.assign(k, v);
            return false;
        });
    }

    // O(sqrt(N)) -- # of i in [l, r] with a[i] == x; needs 0 <= l <= r < size(), else throws out_of_range
    LEETCODE_NO_SANITIZE int countOccurrences(int l, int r, const T& x) {
        if (l < 0 || l > r || r >= size()) throw out_of_range("countOccurrences: needs 0 <= l <= r < size()");
        int res = 0;
        span(l, r, [&](Block& b, int lo, int hi, bool whole, int) {
            if (whole) res += b.count(x);
            else
                for (int k = lo; k <= hi; k++) res += b.get(k) == x;
            return false;
        });
        return res;
    }

    // O(sqrt(N)) -- the smallest i with a[i] == x, or -1 if x isn't in the array
    LEETCODE_NO_SANITIZE int leftmostIndexOf(const T& x) { return findIn(0, n - 1, x, true); }

    // O(sqrt(N)) -- the largest i with a[i] == x, or -1 if x isn't in the array
    LEETCODE_NO_SANITIZE int rightmostIndexOf(const T& x) { return findIn(0, n - 1, x, false); }

    // O(sqrt(N)) -- the smallest i in [l, r] with a[i] == x, or -1 if there is none; needs 0 <= l <= r < size(), else
    // throws out_of_range
    LEETCODE_NO_SANITIZE int leftmostIndexOfInRange(int l, int r, const T& x) {
        if (l < 0 || l > r || r >= size()) throw out_of_range("leftmostIndexOfInRange: needs 0 <= l <= r < size()");
        return findIn(l, r, x, true);
    }

    // O(sqrt(N)) -- the largest i in [l, r] with a[i] == x, or -1 if there is none; needs 0 <= l <= r < size(), else
    // throws out_of_range
    LEETCODE_NO_SANITIZE int rightmostIndexOfInRange(int l, int r, const T& x) {
        if (l < 0 || l > r || r >= size()) throw out_of_range("rightmostIndexOfInRange: needs 0 <= l <= r < size()");
        return findIn(l, r, x, false);
    }

    // O(sqrt(N)) amortized -- insert v so it becomes a[i]; needs 0 <= i <= size(), else throws out_of_range
    LEETCODE_NO_SANITIZE void insertAt(int i, const T& v) {
        if (i < 0 || i > size()) throw out_of_range("insertAt: needs 0 <= i <= size()");
        auto [j, k] = at(i);
        if (j == (int)blocks.size()) {  // (the end: onto the last block)
            if (!j || blocks.back().size() >= 2 * B) {
                blocks.emplace_back(vector<T>{v});
                n++;
                return;
            }
            j--, k = blocks.back().size();
        }
        vector<T> vals = blocks[j].values();
        vals.insert(vals.begin() + k, v);
        if ((int)vals.size() > 2 * B) {  // (too long: two blocks)
            int h = (int)vals.size() / 2;
            blocks[j] = Block(vector<T>(vals.begin(), vals.begin() + h));
            blocks.insert(blocks.begin() + j + 1, Block(vector<T>(vals.begin() + h, vals.end())));
        } else {
            blocks[j].build(vals);
        }
        n++;
        if (idealB(n) > 2 * B) fill(getAll());  // (grown a lot: bigger blocks)
    }

    // O(sqrt(N)) amortized -- append v to the end
    LEETCODE_NO_SANITIZE void append(const T& v) { insertAt(n, v); }

    // O(sqrt(N)) amortized -- insert v at the front (it becomes a[0]; everything else shifts right by one)
    LEETCODE_NO_SANITIZE void appendLeft(const T& v) { insertAt(0, v); }

    // O(k + sqrt(N)) amortized -- insert k copies of v so they become a[i..i+k-1] (nothing if k <= 0); needs
    // 0 <= i <= size(), else throws out_of_range
    LEETCODE_NO_SANITIZE void insertCopiesAt(int i, const T& v, int k) {
        if (i < 0 || i > size()) throw out_of_range("insertCopiesAt: needs 0 <= i <= size()");
        if (k <= 0) return;
        int j = splitAt(i);
        vector<Block> add;
        for (int s = 0; s < k; s += B) add.emplace_back(vector<T>(min(B, k - s), v));
        blocks.insert(blocks.begin() + j, make_move_iterator(add.begin()), make_move_iterator(add.end()));
        n += k;
        tidy();
    }

    // O(sqrt(N)) amortized -- reverse a[l..r] in place; needs 0 <= l <= r < size(), else throws out_of_range
    LEETCODE_NO_SANITIZE void rangeReverse(int l, int r) {
        if (l < 0 || l > r || r >= size()) throw out_of_range("rangeReverse: needs 0 <= l <= r < size()");
        int j1 = splitAt(l), j2 = splitAt(r + 1);
        reverse(blocks.begin() + j1, blocks.begin() + j2);
        for (int j = j1; j < j2; j++) blocks[j].rev = !blocks[j].rev;
        tidy();
    }

    // O(sqrt(N)) amortized -- cyclic shift a[l..r] left by k (a[l + k] moves to l); k can be huge or negative: it is
    // taken mod the length (negative shifts right); needs 0 <= l <= r < size(), else throws out_of_range
    LEETCODE_NO_SANITIZE void rangeRotateLeft(int l, int r, long long k) {
        if (l < 0 || l > r || r >= size()) throw out_of_range("rangeRotateLeft: needs 0 <= l <= r < size()");
        long long m = r - l + 1;
        k = (k % m + m) % m;
        if (!k) return;
        int j1 = splitAt(l), j2 = splitAt(l + (int)k), j3 = splitAt(r + 1);
        rotate(blocks.begin() + j1, blocks.begin() + j2, blocks.begin() + j3);
        tidy();
    }

    // O(sqrt(N)) amortized -- cyclic shift a[l..r] right by k; k can be huge or negative: it is taken mod the length
    // (negative shifts left); needs 0 <= l <= r < size(), else throws out_of_range
    LEETCODE_NO_SANITIZE void rangeRotateRight(int l, int r, long long k) {
        if (l < 0 || l > r || r >= size()) throw out_of_range("rangeRotateRight: needs 0 <= l <= r < size()");
        long long m = r - l + 1;
        rangeRotateLeft(l, r, m - (k % m + m) % m);
    }

    // O(sqrt(N)) amortized -- remove a[l..r] and return it as a SqrtReplace of its own (indices from 0); needs
    // 0 <= l <= r < size(), else throws out_of_range
    SqrtReplace cut(int l, int r) {
        if (l < 0 || l > r || r >= size()) throw out_of_range("cut: needs 0 <= l <= r < size()");
        int j1 = splitAt(l), j2 = splitAt(r + 1);
        SqrtReplace piece;
        piece.blocks.assign(make_move_iterator(blocks.begin() + j1), make_move_iterator(blocks.begin() + j2));
        piece.n = r - l + 1, piece.B = B;
        blocks.erase(blocks.begin() + j1, blocks.begin() + j2);
        n -= r - l + 1;
        tidy(), piece.tidy();
        return piece;
    }

    // O(sqrt(N)) amortized -- insert all of other (any SqrtReplace, e.g. a cut piece) so it starts at a[i]; other is
    // left empty; needs 0 <= i <= size(), else throws out_of_range
    LEETCODE_NO_SANITIZE void paste(int i, SqrtReplace& other) {
        if (i < 0 || i > size()) throw out_of_range("paste: needs 0 <= i <= size()");
        int j = splitAt(i);
        blocks.insert(blocks.begin() + j, make_move_iterator(other.blocks.begin()), make_move_iterator(other.blocks.end()));
        n += other.n;
        other.blocks.clear(), other.n = 0;
        tidy();
    }
    LEETCODE_NO_SANITIZE void paste(int i, SqrtReplace&& other) { paste(i, other); }

    // O(sqrt(N)) amortized -- append all of other at the end; other is left empty
    LEETCODE_NO_SANITIZE void merge(SqrtReplace& other) { paste(n, other); }
    LEETCODE_NO_SANITIZE void merge(SqrtReplace&& other) { paste(n, other); }

    // O(sqrt(N)) amortized -- (a[0..k-1], a[k..]) as two SqrtReplaces of their own; this one is left empty; needs
    // 0 <= k <= size(), else throws out_of_range
    LEETCODE_NO_SANITIZE pair<SqrtReplace, SqrtReplace> split(int k) {
        if (k < 0 || k > size()) throw out_of_range("split: needs 0 <= k <= size()");
        SqrtReplace left;
        swap(left.blocks, blocks), left.n = n, left.B = B, n = 0;
        SqrtReplace right = k < left.n ? left.cut(k, left.n - 1) : SqrtReplace();
        return {std::move(left), std::move(right)};
    }

    // O(sqrt(N)) amortized -- (a[0..l-1], a[l..r], a[r+1..]) as three SqrtReplaces of their own; this one is left
    // empty; needs 0 <= l <= r < size(), else throws out_of_range
    LEETCODE_NO_SANITIZE tuple<SqrtReplace, SqrtReplace, SqrtReplace> trisect(int l, int r) {
        if (l < 0 || l > r || r >= size()) throw out_of_range("trisect: needs 0 <= l <= r < size()");
        auto [left, right] = split(r + 1);
        auto [first, mid] = left.split(l);
        return {std::move(first), std::move(mid), std::move(right)};
    }

    // O(sqrt(N) amortized) -- remove a[size()-1] and return it; needs size() >= 1, else throws out_of_range
    LEETCODE_NO_SANITIZE T pop() {
        auto n = size();
        if (n < 1) throw out_of_range("pop: needs size() >= 1");
        T v = pointGet(n - 1);
        cut(n - 1, n - 1);
        return v;
    }

    // O(sqrt(N) amortized) -- remove a[0] and return it (every index shifts down by 1); needs size() >= 1, else throws out_of_range
    LEETCODE_NO_SANITIZE T popLeft() {
        if (size() < 1) throw out_of_range("popLeft: needs size() >= 1");
        T v = pointGet(0);
        cut(0, 0);
        return v;
    }

    // ---- internals ----

    LEETCODE_NO_SANITIZE static int idealB(int m) { return max(16, (int)sqrt((double)m)); }

    LEETCODE_NO_SANITIZE void fill(const vector<T>& vals) {  // blocks of about idealB values holding vals
        n = (int)vals.size(), B = idealB(n);
        blocks.clear();
        for (int s = 0; s < n; s += B) blocks.emplace_back(vector<T>(vals.begin() + s, vals.begin() + min(n, s + B)));
    }

    // O(N / B + B) amortized -- merge each run of neighbours that fit in one block (each merge is paid for by the
    // split that made it); when the array has grown so much that B is too small, rebuild into even blocks
    LEETCODE_NO_SANITIZE void tidy() {
        if (idealB(n) > 2 * B) return fill(getAll());
        vector<Block> out;
        for (Block& b : blocks) {
            if (!b.size()) continue;
            if (!out.empty() && out.back().size() + b.size() <= B) {
                vector<T> vals = out.back().values(), more = b.values();
                vals.insert(vals.end(), more.begin(), more.end());
                out.back().build(vals);
            } else {
                out.push_back(std::move(b));
            }
        }
        blocks = std::move(out);
    }

    LEETCODE_NO_SANITIZE pair<int, int> at(int i) const {  // (block index, position in it) of a[i]; i == size() gives (number of blocks, 0)
        for (int j = 0; j < (int)blocks.size(); j++) {
            if (i < blocks[j].size()) return {j, i};
            i -= blocks[j].size();
        }
        return {(int)blocks.size(), 0};
    }

    LEETCODE_NO_SANITIZE pair<int, int> locate(int i) const { return at(i); }

    LEETCODE_NO_SANITIZE int splitAt(int i) {  // make a block start at a[i] (0 <= i <= size()): that block's index
        auto [j, k] = at(i);
        if (!k) return j;
        vector<T> vals = blocks[j].values();
        blocks[j].build(vector<T>(vals.begin(), vals.begin() + k));
        blocks.insert(blocks.begin() + j + 1, Block(vector<T>(vals.begin() + k, vals.end())));
        return j + 1;
    }

    // f(block, lo, hi, whole, start) for each block meeting a[l..r] (positions lo..hi of it, whether that is all of
    // it, the index of its first value), until f returns true
    template <class F>
    LEETCODE_NO_SANITIZE void span(int l, int r, F f) {
        int i = 0;
        for (Block& b : blocks) {
            int m = b.size();
            if (i + m > l) {
                int lo = max(l - i, 0), hi = min(r - i, m - 1);
                if (f(b, lo, hi, lo == 0 && hi == m - 1, i) || i + m > r) return;
            }
            i += m;
        }
    }

    LEETCODE_NO_SANITIZE int findIn(int l, int r, const T& x, bool left) {  // the first (left) / last i in [l, r] with a[i] == x, or -1
        if (l > r) return -1;
        vector<tuple<Block*, int, int, bool, int>> parts;
        span(l, r, [&](Block& b, int lo, int hi, bool whole, int start) {
            parts.emplace_back(&b, lo, hi, whole, start);
            return false;
        });
        if (!left) reverse(parts.begin(), parts.end());
        for (auto& [b, lo, hi, whole, start] : parts) {
            if (whole && !b->count(x)) continue;
            for (int k = left ? lo : hi; left ? k <= hi : k >= lo; k += left ? 1 : -1)
                if (b->get(k) == x) return start + k;
        }
        return -1;
    }
};
