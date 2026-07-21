// TEMPLATE BY ISHAANBUILDSTHINGS (see my github)
//
// USAGE
//   // x axis ascending, y axis ascending: queryMax(x, y) -> [loX, x] x [loY, y]
//   OnlineSparseBIT2DMax nxtUp(0, n - 1, lo, hi);
//
//   // x ascending, y descending: queryMax(x, y) -> [loX, x] x [y, hiY]
//   OnlineSparseBIT2DMax nxtDown(0, n - 1, lo, hi, /*descX=*/false, /*descY=*/true);
//
//   nxtUp.chmax(i, v, score);                       // raise cell (i, v)
//   long long best = nxtUp.queryMax(i - k, v - 1);  // NEG if empty / untouched
//
// Fully online sparse 2D Binary Indexed Tree over a max monoid:
//   - chmax:    tree[x][y] = max(tree[x][y], v)
//   - queryMax: max over a corner-anchored rectangle, orientation set
//               per axis at construction via descX / descY
//
// Coordinates may be arbitrary integers in [loX, hiX] x [loY, hiY];
// shifts are handled internally. Backed by one flat open-addressed hash
// table with packed 64-bit keys, so no coordinates need to be known in
// advance and no O(uX * uY) array is allocated.
//
// ORIENTATION IS FIXED AT CONSTRUCTION. descX / descY reverse an axis
// internally, turning that axis's suffix query into a prefix query.
// This cannot be a per-call option: chmax writes into node ranges
// determined by the orientation, so a tree built ascending contains no
// node covering a suffix. Choose per axis up front.
//
//     descX  descY   queryMax(x, y) covers
//     -----  -----   ---------------------
//     false  false   [loX, x] x [loY, y]     both prefixes
//     false  true    [loX, x] x [y, hiY]     prefix, suffix
//     true   false   [x, hiX] x [loY, y]     suffix, prefix
//     true   true    [x, hiX] x [y, hiY]     both suffixes
//
// Bounds are clamped, so out-of-range args are safe:
//     ascending axis,  bound < lo   -> empty, contributes NEG
//     ascending axis,  bound > hi   -> full axis
//     descending axis, bound > hi   -> empty, contributes NEG
//     descending axis, bound < lo   -> full axis
//
// Queries are always CORNER-ANCHORED. Max has no inverse, so an
// interior rectangle cannot be obtained by diffing prefixes. Orient
// the axes so every query you need is anchored.
//
// MONOTONE UPDATES ONLY. A cell can be raised, never lowered; a
// decrease is silently ignored, not applied. Internal nodes store a
// winner and forget the runners-up, so a decrease is unrecoverable.
//
// Complexities in terms of universe sizes uX, uY (coordinate ranges),
// with P = number of distinct chmax calls performed:
//   ctor:      O(uX)
//   chmax:     O(log(uX) * log(uY)) expected
//   queryMax:  O(log(uX) * log(uY)) expected
//   memory:    O(P * log(uX) * log(uY)) entries, 16 bytes each
//
// Memory is the binding constraint: each chmax materializes up to
// log(uX) * log(uY) table entries. At uX = uY = 1e5 that is ~289 per
// update, so ~1e5 updates lands near 3e7 entries and will MLE at a
// 256MB limit. When all update coordinates are knowable in advance,
// the offline variant compresses each row node's column set and costs
// only log(uX) slots per point instead.

#include <bits/stdc++.h>
using namespace std;

class OnlineSparseBIT2DMax {
public:
    static constexpr long long NEG = LLONG_MIN;

    OnlineSparseBIT2DMax(int loX_, int hiX_, int loY_, int hiY_,
                         bool descX_ = false, bool descY_ = false)
        : loX(loX_), hiX(hiX_), loY(loY_), hiY(hiY_),
          descX(descX_), descY(descY_),
          uX(hiX_ - loX_ + 1), uY(hiY_ - loY_ + 1) {
        // pack (i, j) into one 64-bit key; shift must clear all of j
        shift = 0;
        while ((1LL << shift) <= uY) ++shift;
        cap = 1u << 12;
        mask = cap - 1;
        keys.assign(cap, 0);
        vals.assign(cap, NEG);
        sz = 0;
        rowTouched.assign(uX + 2, 0);   // lets a query skip an untouched row node
    }

    // O(log(uX) * log(uY)) -- tree[x][y] = max(tree[x][y], v). Never lowers a cell.
    void chmax(int x, int y, long long v) {
        // map user coords to internal 1..u, reversing a descending axis
        //   asc:  loX -> 1,  hiX -> uX
        //   desc: hiX -> 1,  loX -> uX
        x = descX ? hiX - x + 1 : x - loX + 1;
        y = descY ? hiY - y + 1 : y - loY + 1;
        for (int i = x; i <= uX; i += i & -i) {   // every row node covering x
            rowTouched[i] = 1;
            for (int j = y; j <= uY; j += j & -j) // every col node covering y
                put(pack(i, j), v);
        }
    }

    // O(log(uX) * log(uY)) -- max over the corner rectangle bounded by x and y,
    // per the descX / descY orientation. NEG if empty or untouched, so callers
    // need no bounds guard.
    long long queryMax(int x, int y) const {
        x = descX ? hiX - x + 1 : x - loX + 1;
        y = descY ? hiY - y + 1 : y - loY + 1;
        if (x <= 0 || y <= 0) return NEG;
        if (x > uX) x = uX;
        if (y > uY) y = uY;
        long long best = NEG;
        for (int i = x; i > 0; i -= i & -i) {     // disjoint row blocks tiling [1..x]
            if (!rowTouched[i]) continue;         // skip whole row node if never written
            for (int j = y; j > 0; j -= j & -j) { // disjoint col blocks tiling [1..y]
                long long cur = get(pack(i, j));
                if (cur > best) best = cur;
            }
        }
        return best;
    }

private:
    int loX, hiX, loY, hiY;
    bool descX, descY;
    int uX, uY, shift;
    size_t cap, mask, sz;
    vector<uint64_t> keys;                // 0 == empty; real keys have i >= 1
    vector<long long> vals;
    vector<char> rowTouched;

    inline uint64_t pack(int i, int j) const {
        return ((uint64_t)i << shift) | (uint64_t)j;
    }

    static inline uint64_t hashKey(uint64_t z) {   // splitmix64 finalizer
        z += 0x9e3779b97f4a7c15ULL;
        z = (z ^ (z >> 30)) * 0xbf58476d1ce4e5b9ULL;
        z = (z ^ (z >> 27)) * 0x94d049bb133111ebULL;
        return z ^ (z >> 31);
    }

    void put(uint64_t key, long long v) {
        size_t p = hashKey(key) & mask;
        while (keys[p] && keys[p] != key) p = (p + 1) & mask;
        if (!keys[p]) {
            keys[p] = key;
            vals[p] = v;
            if (++sz * 2 >= cap) grow();
        } else if (vals[p] < v) {
            vals[p] = v;
        }
    }

    long long get(uint64_t key) const {
        size_t p = hashKey(key) & mask;
        while (keys[p]) {
            if (keys[p] == key) return vals[p];
            p = (p + 1) & mask;
        }
        return NEG;
    }

    void grow() {
        size_t ncap = cap << 1, nmask = ncap - 1;
        vector<uint64_t> nk(ncap, 0);
        vector<long long> nv(ncap, NEG);
        for (size_t i = 0; i < cap; i++) {
            if (!keys[i]) continue;
            size_t p = hashKey(keys[i]) & nmask;
            while (nk[p]) p = (p + 1) & nmask;
            nk[p] = keys[i];
            nv[p] = vals[i];
        }
        keys.swap(nk);
        vals.swap(nv);
        cap = ncap;
        mask = nmask;
    }
};