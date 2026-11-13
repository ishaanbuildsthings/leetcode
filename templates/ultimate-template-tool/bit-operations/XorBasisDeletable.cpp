// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/bit-operations/XorBasisDeletable.cpp
#include <bits/stdc++.h>
using namespace std;

// XorBasisDeletable: an XOR basis you can insert values into and remove values from, online (a multiset: copies count).
// Every query is about the values held right now: what XORs of their subsets can make (the empty subset makes 0).
// Values must be >= 0 (long long). B = number of bits in the largest value, N = number of values held.
// Use XorBasis instead when nothing is ever removed: the same queries, with O(B) inserts.
//
// XorBasisDeletable basis(vector<long long>{3, 10, 5});
// basis.remove(10);    // true: one copy of 10 was held
// basis.maxSubsetXor();      // 6, from 3 ^ 5
//
// How removes work (https://eolymp.com/posts/7u074ngkv127l3fl0m33bf5gck): the values are split into several bases,
// each spanning a subspace of the one before, grouped by dimension; the biggest spans everything, so queries read it.
// A value goes into the first basis that can't already make it. To remove v from basis X: if X without v still spans
// the next smaller basis Y, v is just dropped (X loses a dimension); else some value y of Y restores X's span, so y
// takes v's place in X and y is removed from Y instead. That walks down at most B dimensions. Each basis keeps fully
// reduced rows that remember which of its values they combine, so every step is O(B).
struct XorBasisDeletable {
    // O(N * B^2)
    explicit XorBasisDeletable(const vector<long long>& arr = {}) {
        for (long long x : arr) insert(x);
    }

    // inserts x; returns true if x couldn't be made before (the basis grew), else false
    // O(B^2)
    bool insert(long long x) {
        if (x < 0) throw invalid_argument("XorBasisDeletable::insert: x = " + to_string(x) + " is negative");
        count++;
        if (x == 0) {
            zeros++;
            return false;
        }
        int e = newElem(x);
        byVal[x].push_back(e);
        int top = topLevel();
        for (int d = top; d >= 1; d--) {  // the first basis (biggest first) that can't make x
            if (levels[d].empty()) continue;
            int b = levels[d].back();
            if (reduce(pool[b], x)) {
                detach(b);
                addRow(b, e, x);
                attach(b);
                return d == top;
            }
        }
        int b = newBasis();  // every basis can make x: a new one of dimension 1 (the same span as any other of dim 1)
        addRow(b, e, x);
        attach(b);
        return top == 0;
    }

    // removes one copy of x; returns true if one was held, else false (nothing changes)
    // O(B^2)
    bool remove(long long x) {
        if (x == 0) {
            if (!zeros) return false;
            zeros--;
            count--;
            return true;
        }
        auto it = byVal.find(x);
        if (it == byVal.end()) return false;
        int e = it->second.back();
        it->second.pop_back();
        if (it->second.empty()) byVal.erase(it);
        count--;
        freeElems.push_back(e);
        int b = loc[e], p = pos[e];
        while (true) {
            int d = (int)pool[b].vec.size();
            vector<int> rows;  // the rows that use the removed value
            int r0 = -1;
            unsigned long long pivotsUsed = 0;
            for (int i = 0; i < d; i++) {
                if (!(pool[b].msk[i] >> p & 1)) continue;
                rows.push_back(i);
                pivotsUsed |= 1ULL << pool[b].piv[i];
                if (r0 < 0 || pool[b].piv[i] < pool[b].piv[r0]) r0 = i;
            }
            // y (any value b can make) needs the removed one iff its reduced form uses an odd number of those rows
            int smaller = -1, yAt = -1;
            for (int k = d - 1; k >= 1 && smaller < 0; k--)
                if (!levels[k].empty()) smaller = levels[k].back();
            if (smaller >= 0) {
                const vector<int>& ys = pool[smaller].elem;
                for (int j = 0; j < (int)ys.size(); j++) {
                    if (__builtin_popcountll((unsigned long long)val[ys[j]] & pivotsUsed) & 1) {
                        yAt = j;
                        break;
                    }
                }
            }
            detach(b);
            removeAt(b, p, rows, r0);
            if (yAt < 0) {  // b without the value still spans the smaller basis: done, b drops a dimension
                if (pool[b].vec.empty()) freeBases.push_back(b);
                else attach(b);
                return true;
            }
            int y = pool[smaller].elem[yAt];  // y takes the removed value's place (b keeps its span), leaves smaller
            addRow(b, y, val[y]);
            attach(b);
            b = smaller;
            p = yAt;
        }
    }

    // true if some subset XORs to exactly x (x = 0 is always true: the empty subset)
    // O(B)
    bool doesSubsetXorEqualToXExist(long long x) const {
        if (x < 0) return false;
        int top = topBasis();
        return top < 0 ? x == 0 : reduce(pool[top], x) == 0;
    }

    // largest XOR of any subset (0 if nothing is held)
    // O(B)
    long long maxSubsetXor() const { return maxXorOfXAndSubsetXor(0); }

    // largest x ^ (XOR of some subset)
    // O(B)
    long long maxXorOfXAndSubsetXor(long long x) const {
        if (x < 0) throw invalid_argument("XorBasisDeletable::maxXorOfXAndSubsetXor: x = " + to_string(x)
            + " is negative");
        int top = topBasis();
        if (top >= 0) {
            const Basis& b = pool[top];
            for (int i = 0; i < (int)b.vec.size(); i++)
                if (!(x >> b.piv[i] & 1)) x ^= b.vec[i];
        }
        return x;
    }

    // smallest x ^ (XOR of some subset)
    // O(B)
    long long minXorOfXAndSubsetXor(long long x) const {
        if (x < 0) throw invalid_argument("XorBasisDeletable::minXorOfXAndSubsetXor: x = " + to_string(x)
            + " is negative");
        int top = topBasis();
        return top < 0 ? x : reduce(pool[top], x);
    }

    // smallest XOR of a non-empty subset: 0 if some non-empty subset XORs to 0, -1 if nothing is held
    // O(B)
    long long minNonEmptySubsetXor() const {
        if (count == 0) return -1;
        int top = topBasis();
        if (top < 0 || count > (long long)pool[top].vec.size()) return 0;
        return *min_element(pool[top].vec.begin(), pool[top].vec.end());
    }

    // the kth smallest distinct value some subset makes, k 0-indexed (k = 0 -> 0), or -1 if k >=
    // countDistinctSubsetXors()
    // O(B log B)
    long long kthSmallestDistinctSubsetXor(long long k) const {
        if (k < 0) throw invalid_argument("XorBasisDeletable::kthSmallestDistinctSubsetXor: k = " + to_string(k)
            + " is negative");
        vector<long long> rows = basis();
        reverse(rows.begin(), rows.end());
        int r = (int)rows.size();
        if (r < 63 && (k >> r)) return -1;
        long long res = 0;
        for (int i = 0; i < r; i++)
            if (k >> i & 1) res ^= rows[i];
        return res;
    }

    // the kth smallest XOR over all 2^N subsets by position (the empty one included, repeats kept), k 0-indexed, or
    // -1 if k >= 2^N. Each distinct value comes from 2^(N - basisSize()) subsets, so it is the distinct one at
    // k >> (N - basisSize())
    // XorBasisDeletable(vector<int>{1, 1}).kthSmallestSubsetXor(1) -> 0   // every subset XOR, sorted: 0, 0, 1, 1
    // O(B log B)
    long long kthSmallestSubsetXor(long long k) const {
        if (k < 0) {
            throw invalid_argument("XorBasisDeletable::kthSmallestSubsetXor: k = " + to_string(k) + " is negative");
        }
        long long n = size();
        if (n < 63 && (k >> n)) {
            return -1;
        }
        long long shift = n - basisSize();
        return kthSmallestDistinctSubsetXor(shift >= 63 ? 0 : k >> shift);
    }

    // number of distinct values the subsets make, counting 0 from the empty subset: 2^basisSize() (basisSize() must be
    // <= 62)
    // O(B)
    long long countDistinctSubsetXors() const { return 1LL << basisSize(); }

    // number of subsets of the held values (by position, the empty one included) whose XOR is exactly x, mod mod:
    // 2^(N - basisSize()) if x can be made, else 0
    // O(B + log(N))
    long long countSubsetsWithXorEqualToXMod(long long x, long long mod) const {
        if (!doesSubsetXorEqualToXExist(x)) return 0;
        long long res = 1 % mod, base = 2 % mod;
        for (long long e = count - basisSize(); e > 0; e >>= 1) {
            if (e & 1) res = (long long)((__int128)res * base % mod);
            base = (long long)((__int128)base * base % mod);
        }
        return res;
    }

    // size of the basis of the held values
    // O(B)
    int basisSize() const { return topLevel(); }

    // how many values are held, copies and zeros included
    // O(1)
    long long size() const { return count; }

    // a basis of the held values, largest first (basisSize() of them, fully reduced)
    // O(B log B)
    vector<long long> basis() const {
        int top = topBasis();
        if (top < 0) return {};
        vector<long long> res = pool[top].vec;
        sort(res.rbegin(), res.rend());
        return res;
    }

    // ---- internals ----

    // one basis: fully reduced rows (vec, which values of elem they XOR together as msk, highest set bit piv)
    struct Basis {
        vector<long long> vec;
        vector<unsigned long long> msk;
        vector<int> piv, elem;
        int idx = -1;  // index in its dimension's list
    };
    struct SplitMix {  // (hashes values so no fixed input can make them collide)
        size_t operator()(long long x) const {
            static const unsigned long long salt = chrono::steady_clock::now().time_since_epoch().count();
            unsigned long long z = (unsigned long long)x + salt + 0x9e3779b97f4a7c15ULL;
            z = (z ^ (z >> 30)) * 0xbf58476d1ce4e5b9ULL;
            z = (z ^ (z >> 27)) * 0x94d049bb133111ebULL;
            return z ^ (z >> 31);
        }
    };

    vector<Basis> pool;
    vector<int> freeBases;
    vector<vector<int>> levels = vector<vector<int>>(1);  // levels[d]: the bases of dimension d (all the same span)
    vector<long long> val;  // per value id: its value, its basis, its position in that basis (a bit of the masks)
    vector<int> loc, pos, freeElems;
    unordered_map<long long, vector<int>, SplitMix> byVal;  // value -> ids of its copies held in a basis
    long long zeros = 0, count = 0;

    int topLevel() const {
        for (int d = (int)levels.size() - 1; d >= 1; d--)
            if (!levels[d].empty()) return d;
        return 0;
    }

    int topBasis() const {
        int d = topLevel();
        return d ? levels[d].back() : -1;
    }

    static long long reduce(const Basis& b, long long x) {  // x with b's pivot bits cleared: 0 iff b can make x
        for (int i = 0; i < (int)b.vec.size(); i++)
            if (x >> b.piv[i] & 1) x ^= b.vec[i];
        return x;
    }

    int newElem(long long x) {
        if (!freeElems.empty()) {
            int e = freeElems.back();
            freeElems.pop_back();
            val[e] = x;
            return e;
        }
        val.push_back(x);
        loc.push_back(-1);
        pos.push_back(-1);
        return (int)val.size() - 1;
    }

    int newBasis() {
        if (!freeBases.empty()) {
            int b = freeBases.back();
            freeBases.pop_back();
            pool[b] = Basis();
            return b;
        }
        pool.emplace_back();
        return (int)pool.size() - 1;
    }

    void attach(int b) {  // into the list of its dimension
        size_t d = pool[b].vec.size();
        if (levels.size() <= d) levels.resize(d + 1);
        pool[b].idx = (int)levels[d].size();
        levels[d].push_back(b);
    }

    void detach(int b) {
        vector<int>& lst = levels[pool[b].vec.size()];
        int last = lst.back();
        lst.pop_back();
        if (last != b) {
            lst[pool[b].idx] = last;
            pool[last].idx = pool[b].idx;
        }
    }

    void addRow(int bi, int e, long long x) {  // value x (id e) into basis bi, which can't make it yet; stays reduced
        Basis& b = pool[bi];
        int p = (int)b.elem.size();
        unsigned long long m = 1ULL << p;
        for (int i = 0; i < (int)b.vec.size(); i++) {
            if (x >> b.piv[i] & 1) {
                x ^= b.vec[i];
                m ^= b.msk[i];
            }
        }
        int q = 63 - __builtin_clzll((unsigned long long)x);
        for (int i = 0; i < (int)b.vec.size(); i++) {
            if (b.vec[i] >> q & 1) {
                b.vec[i] ^= x;
                b.msk[i] ^= m;
            }
        }
        b.vec.push_back(x);
        b.msk.push_back(m);
        b.piv.push_back(q);
        b.elem.push_back(e);
        loc[e] = bi;
        pos[e] = p;
    }

    void removeAt(int bi, int p, const vector<int>& rows, int r0) {  // drops the value at position p (its rows: rows)
        Basis& b = pool[bi];
        for (int i : rows) {
            if (i != r0) {  // (r0's pivot is below theirs, so their pivots stay put)
                b.vec[i] ^= b.vec[r0];
                b.msk[i] ^= b.msk[r0];
            }
        }
        b.vec[r0] = b.vec.back(), b.vec.pop_back();
        b.msk[r0] = b.msk.back(), b.msk.pop_back();
        b.piv[r0] = b.piv.back(), b.piv.pop_back();
        int last = (int)b.elem.size() - 1;  // the last position moves into p, so positions stay 0..dim-1
        if (p != last) {
            int moved = b.elem[last];
            b.elem[p] = moved;
            pos[moved] = p;
            for (unsigned long long& m : b.msk)
                if (m >> last & 1) m ^= (1ULL << last) | (1ULL << p);
        }
        b.elem.pop_back();
    }
};
