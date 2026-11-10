// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries/countOccurrences-leftmostIndexOf-leftmostIndexOfInRange-pointAssign-pointGet-rangeAssign-rangeReplace-rightmostIndexOf-rightmostIndexOfInRange__sqrt/template.cpp
#include <bits/stdc++.h>
using namespace std;
using ll = long long;

// @operations: countOccurrences getAll leftmostIndexOf leftmostIndexOfInRange pointAssign pointGet rangeAssign rangeReplace rightmostIndexOf rightmostIndexOfInRange
// @data-structure-type: sqrt
// @letters: same
// @complexities:
//   countOccurrences: sqrt(N)
//   getAll: N
//   leftmostIndexOf: sqrt(N)
//   leftmostIndexOfInRange: sqrt(N)
//   pointAssign: 1 amortized
//   pointGet: 1 amortized
//   rangeAssign: sqrt(N) amortized
//   rangeReplace: sqrt(N) amortized
//   rightmostIndexOf: sqrt(N)
//   rightmostIndexOfInRange: sqrt(N)
//   build: N
// @memory:
//   layout: none
//   node: cls[1*N] par[2*N] val[2*N] cnt[2*N] where[1*N]
//   tags: none
//   other: none
//   note: blocks of about sqrt(N) values; each block's values are classes joined by a union-find (union by size, path halving: O(alpha), counted as O(1)); where maps each value in the block to its class; values are hashed, so any values work

// Blocks whose values form a union-find of classes (mass change, CF 911G, in O(sqrt N)): the array is cut into blocks
// of about sqrt(N) values. Inside a block equal values form a class, and the classes are joined by a union-find:
// rangeReplace(l, r, x, y) on a whole block renames x's class to y, or joins it into y's, in O(1); rangeAssign joins
// every class. Only the (at most two) partly covered blocks are touched value by value. Any values work (each block
// hashes them). a[i] and a[i] = v are O(1) amortized. All indices 0-based, ranges inclusive [l, r]; searches return
// -1 when nothing qualifies.
// T: any type with a hash (int, long long, char, ...)

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
    // a run of the array: cls[k] is the class of its k-th value. Classes form a union-find
    // (par); a root class holds its value (val) and how many of the block's values are in it (cnt). where: value ->
    // root
    struct Block {
        vector<int> cls, par, cnt;
        vector<T> val;
        unordered_map<T, int, SafeHash> where;

        Block() {}
        explicit Block(const vector<T>& vals) { build(vals); }

        void build(const vector<T>& vals) {  // O(len) -- the classes from scratch
            cls.clear(), par.clear(), cnt.clear(), val.clear(), where.clear();
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
            return val[find(cls[k])];
        }

        vector<T> values() {  // every value, in order
            vector<T> out;
            out.reserve(cls.size());
            for (int c : cls) out.push_back(val[find(c)]);
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

        void assign(int k, const T& v) {
            // O(1) amortized -- the k-th value becomes v (a class of its own if v is new here)
            int c = find(cls[k]);
            if (val[c] == v) return;
            if (!--cnt[c]) where.erase(val[c]);
            auto [it, fresh] = where.try_emplace(v, (int)par.size());
            if (fresh) par.push_back(it->second), val.push_back(v), cnt.push_back(0);
            cnt[it->second]++;
            cls[k] = it->second;
            // (many dead classes: start over, paid for by the assigns)
            if ((int)par.size() > 2 * size() + 8) build(values());
        }
    };

    vector<Block> blocks;
    int n = 0, B = 1;

    // O(N) -- arr: the initial array
    explicit SqrtReplace(const vector<T>& arr) { fill(arr); }

    // O(1) -- the length of the array
    int size() const { return n; }

    // O(N) -- the whole current array
    vector<T> getAll() {
        vector<T> out;
        out.reserve(n);
        for (Block& b : blocks) {
            vector<T> v = b.values();
            out.insert(out.end(), v.begin(), v.end());
        }
        return out;
    }

    // O(1) amortized) -- a[i]; needs 0 <= i < size(), else throws out_of_range
    T pointGet(int i) {
        if (i < 0 || i >= size()) throw out_of_range("pointGet: needs 0 <= i < size()");
        auto [j, k] = locate(i);
        return blocks[j].get(k);
    }

    // O(1) amortized) -- a[i] = v; needs 0 <= i < size(), else throws out_of_range
    void pointAssign(int i, const T& v) {
        if (i < 0 || i >= size()) throw out_of_range("pointAssign: needs 0 <= i < size()");
        auto [j, k] = locate(i);
        blocks[j].assign(k, v);
    }

    // O(sqrt(N)) amortized -- every a[i] == x with l <= i <= r becomes y; needs 0 <= l <= r < size(), else throws
    // out_of_range
    void rangeReplace(int l, int r, const T& x, const T& y) {
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
    void rangeAssign(int l, int r, const T& v) {
        if (l < 0 || l > r || r >= size()) throw out_of_range("rangeAssign: needs 0 <= l <= r < size()");
        span(l, r, [&](Block& b, int lo, int hi, bool whole, int) {
            if (whole) b.assignAll(v);
            else
                for (int k = lo; k <= hi; k++) b.assign(k, v);
            return false;
        });
    }

    // O(sqrt(N)) -- # of i in [l, r] with a[i] == x; needs 0 <= l <= r < size(), else throws out_of_range
    int countOccurrences(int l, int r, const T& x) {
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
    int leftmostIndexOf(const T& x) { return findIn(0, n - 1, x, true); }

    // O(sqrt(N)) -- the largest i with a[i] == x, or -1 if x isn't in the array
    int rightmostIndexOf(const T& x) { return findIn(0, n - 1, x, false); }

    // O(sqrt(N)) -- the smallest i in [l, r] with a[i] == x, or -1 if there is none; needs 0 <= l <= r < size(), else
    // throws out_of_range
    int leftmostIndexOfInRange(int l, int r, const T& x) {
        if (l < 0 || l > r || r >= size()) throw out_of_range("leftmostIndexOfInRange: needs 0 <= l <= r < size()");
        return findIn(l, r, x, true);
    }

    // O(sqrt(N)) -- the largest i in [l, r] with a[i] == x, or -1 if there is none; needs 0 <= l <= r < size(), else
    // throws out_of_range
    int rightmostIndexOfInRange(int l, int r, const T& x) {
        if (l < 0 || l > r || r >= size()) throw out_of_range("rightmostIndexOfInRange: needs 0 <= l <= r < size()");
        return findIn(l, r, x, false);
    }

    // ---- internals ----

    static int idealB(int m) { return max(1, (int)sqrt((double)m)); }

    void fill(const vector<T>& vals) {  // blocks of about idealB values holding vals
        n = (int)vals.size(), B = idealB(n);
        blocks.clear();
        for (int s = 0; s < n; s += B) blocks.emplace_back(vector<T>(vals.begin() + s, vals.begin() + min(n, s + B)));
    }

    pair<int, int> locate(int i) const { return {i / B, i % B}; }  // (block index, position in it) of a[i]

    // f(block, lo, hi, whole, start) for each block meeting a[l..r] (positions lo..hi of it, whether that is all of
    // it, the index of its first value), until f returns true
    template <class F>
    void span(int l, int r, F f) {
        for (int j = l / B; j <= r / B; j++) {
            int start = j * B, m = blocks[j].size(), lo = max(l - start, 0), hi = min(r - start, m - 1);
            if (f(blocks[j], lo, hi, lo == 0 && hi == m - 1, start)) return;
        }
    }

    int findIn(int l, int r, const T& x, bool left) {  // the first (left) / last i in [l, r] with a[i] == x, or -1
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
