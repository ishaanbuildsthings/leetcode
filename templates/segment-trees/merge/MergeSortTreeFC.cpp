#include <bits/stdc++.h>
using namespace std;
// Merge sort tree with fractional cascading.
// Build: O(n log n) time, ceil(log2 n) * n ints of space.
// Every query: O(log n) — one binary search at the root, then an iterative
// top-down walk, O(1) per level, no recursion and no per-node vectors.
//
// Two representational changes vs the straightforward version:
//   * Nodes do not store their sorted values. Fractional cascading only ever
//     binary searches the root, so only sortedVals is kept. A node's element
//     count is tr - tl + 1, which the walk already tracks.
//   * cntL is one flat array instead of 4n vectors. At any depth the segment
//     tree nodes partition [0, n-1], and a node covering [tl, tr] owns exactly
//     working-array slots tl..tr, so (depth, tl) addresses a node's prefix data
//     with no offset table and no node index at all.
struct MergeSortTree {
    int n = 0, levels = 0;
    vector<int> sortedVals;  // root's sorted values — the only array ever binary-searched
    vector<int> cnt;         // cnt[d * n + tl + j] = # of the first (j+1) elements of the depth-d node starting at tl that live in its left child

    MergeSortTree() {}

    MergeSortTree(const vector<int>& arr) {
        n = (int)arr.size();
        if (n == 0) return;
        for (int w = 1; w < n; w <<= 1) levels++;
        if (levels) cnt.assign((size_t)levels * n, 0);
        sortedVals.resize(n);

        // Indices ordered by value, ties by index — same tie rule as L[li] <= R[ri].
        // Value and index are packed into one 64-bit word and LSD-radix sorted on
        // the 32 value bits; the sort is stable, so equal values keep index order,
        // and the sorted keys hand back sortedVals for free (no second sort).
        vector<int> cur(n), buf(n);
        {
            vector<unsigned long long> src(n), dst(n);
            for (int i = 0; i < n; i++)
                src[i] = ((unsigned long long)(unsigned int)(arr[i] ^ 0x80000000u) << 32) | (unsigned int)i;
            int histogram[4][256] = {};
            for (int i = 0; i < n; i++) {
                unsigned int key = (unsigned int)(src[i] >> 32);
                histogram[0][key & 255]++;
                histogram[1][(key >> 8) & 255]++;
                histogram[2][(key >> 16) & 255]++;
                histogram[3][key >> 24]++;
            }
            for (int pass = 0; pass < 4; pass++) {
                int start[256], running = 0;
                for (int b = 0; b < 256; b++) { start[b] = running; running += histogram[pass][b]; }
                int shift = pass * 8;
                for (int i = 0; i < n; i++) {
                    unsigned int key = (unsigned int)(src[i] >> 32);
                    dst[start[(key >> shift) & 255]++] = src[i];
                }
                src.swap(dst);
            }
            for (int i = 0; i < n; i++) {
                sortedVals[i] = (int)((unsigned int)(src[i] >> 32) ^ 0x80000000u);
                cur[i] = (int)(unsigned int)src[i];
            }
        }

        // Splitting a value-ordered index list on "index <= mid" preserves the
        // ordering, so each level is one stable partition per node — a linear
        // sequential pass, no merging and no allocation.
        vector<pair<int, int>> nodes, next;
        nodes.push_back({0, n - 1});
        for (int d = 0; d < levels; d++) {
            int* C = cnt.data() + (size_t)d * n;
            next.clear();
            for (auto [tl, tr] : nodes) {
                if (tl == tr) continue;
                int mid = (tl + tr) >> 1;
                int lp = tl, rp = mid + 1, run = 0;
                for (int j = tl; j <= tr; j++) {
                    int id = cur[j];
                    if (id <= mid) { buf[lp++] = id; run++; }
                    else            { buf[rp++] = id; }
                    C[j] = run;
                }
                next.push_back({tl, mid});
                next.push_back({mid + 1, tr});
            }
            cur.swap(buf);
            nodes.swap(next);
        }
    }

    // # of the first p elements (in global sorted order) of the depth-d node
    // starting at tl that live in that node's left child
    inline int leftCount(int d, int tl, int p) const {
        return p ? cnt[(size_t)d * n + tl + p - 1] : 0;
    }

    // Sums, over the canonical nodes covering [ql, qr], how many of the p
    // globally-smallest elements live in each. Descends from the root updating
    // the cascaded p until [ql, qr] either covers the node or straddles its
    // midpoint, then walks the two boundary paths down, adding whole sibling
    // subtrees as it peels them off. Each boundary walk stops as soon as the
    // node it is standing on is itself fully covered.
    int countPrefix(int ql, int qr, int p) const {
        int tl = 0, tr = n - 1, d = 0, mid, leftP;
        for (;;) {
            if (ql <= tl && tr <= qr) return p;
            mid = (tl + tr) >> 1;
            leftP = leftCount(d, tl, p);
            if (qr <= mid)      { tr = mid;     p = leftP;     d++; }
            else if (ql > mid)  { tl = mid + 1; p -= leftP;    d++; }
            else break;
        }
        int res = 0;

        // left boundary: cover [ql, mid] inside the left child
        int a = tl, b = mid, pa = leftP, da = d + 1;
        while (a < b && ql > a) {
            int m = (a + b) >> 1;
            int lp = leftCount(da, a, pa);
            if (ql <= m) { res += pa - lp; b = m; pa = lp; }   // entire right child is inside [ql, qr]
            else         { a = m + 1; pa -= lp; }
            da++;
        }
        res += pa;

        // right boundary: cover [mid + 1, qr] inside the right child
        a = mid + 1; b = tr; pa = p - leftP; da = d + 1;
        while (a < b && qr < b) {
            int m = (a + b) >> 1;
            int lp = leftCount(da, a, pa);
            if (qr > m) { res += lp; a = m + 1; pa -= lp; }    // entire left child is inside [ql, qr]
            else        { b = m; pa = lp; }
            da++;
        }
        return res + pa;
    }

    // --- count ---

    // O(log n) — count elements >= x in [ql, qr]
    // Seeded with lower_bound(x) (elements < x) and complemented against the range size
    int countGteX(int ql, int qr, int x) const {
        if (ql < 0) ql = 0;
        if (qr > n - 1) qr = n - 1;
        if (ql > qr) return 0;
        int p = (int)(lower_bound(sortedVals.begin(), sortedVals.end(), x) - sortedVals.begin());
        return (qr - ql + 1) - countPrefix(ql, qr, p);
    }

    // O(log n) — count elements <= x in [ql, qr]
    int countLteX(int ql, int qr, int x) const {
        if (ql < 0) ql = 0;
        if (qr > n - 1) qr = n - 1;
        if (ql > qr) return 0;
        int p = (int)(upper_bound(sortedVals.begin(), sortedVals.end(), x) - sortedVals.begin());
        return countPrefix(ql, qr, p);
    }

    // O(log n) — count elements in value range [valLow, valHigh] (inclusive) in index range [ql, qr]
    int countInRange(int ql, int qr, int valLow, int valHigh) const {
        return countLteX(ql, qr, valHigh) - countLteX(ql, qr, valLow - 1);
    }

    // --- find k-th by position ---

    struct Part { int d, tl, tr, p; };

    // Same decomposition as countPrefix, but writes the canonical nodes out in
    // LEFT-TO-RIGHT order. At most 2 * levels + 2 of them, so it fits in a
    // caller-supplied stack buffer — the counting path stays allocation-free too.
    int decompose(int ql, int qr, int p, Part* out) const {
        int tl = 0, tr = n - 1, d = 0, mid, leftP;
        for (;;) {
            if (ql <= tl && tr <= qr) { out[0] = {d, tl, tr, p}; return 1; }
            mid = (tl + tr) >> 1;
            leftP = leftCount(d, tl, p);
            if (qr <= mid)      { tr = mid;     p = leftP;  d++; }
            else if (ql > mid)  { tl = mid + 1; p -= leftP; d++; }
            else break;
        }
        int cntOut = 0;

        // left walk collects right-to-left (the node it lands on is the leftmost), so reverse after
        int a = tl, b = mid, pa = leftP, da = d + 1;
        while (a < b && ql > a) {
            int m = (a + b) >> 1;
            int lp = leftCount(da, a, pa);
            if (ql <= m) { out[cntOut++] = {da + 1, m + 1, b, pa - lp}; b = m; pa = lp; }
            else         { a = m + 1; pa -= lp; }
            da++;
        }
        out[cntOut++] = {da, a, b, pa};
        reverse(out, out + cntOut);

        // right walk already collects left-to-right
        a = mid + 1; b = tr; pa = p - leftP; da = d + 1;
        while (a < b && qr < b) {
            int m = (a + b) >> 1;
            int lp = leftCount(da, a, pa);
            if (qr > m) { out[cntOut++] = {da + 1, a, m, lp}; a = m + 1; pa -= lp; }
            else        { b = m; pa = lp; }
            da++;
        }
        out[cntOut++] = {da, a, b, pa};
        return cntOut;
    }

    // O(log n) — array index (POSITION, not value) of the k-th element >= x in
    // [ql, qr], 1-indexed k, scanning left to right. Returns -1 if fewer than k exist.
    int findKthGteX(int ql, int qr, int k, int x) const {
        if (ql < 0) ql = 0;
        if (qr > n - 1) qr = n - 1;
        if (ql > qr || k <= 0) return -1;
        int p0 = (int)(lower_bound(sortedVals.begin(), sortedVals.end(), x) - sortedVals.begin());
        Part parts[80];
        int m = decompose(ql, qr, p0, parts);
        for (int i = 0; i < m; i++) {
            int d = parts[i].d, tl = parts[i].tl, tr = parts[i].tr, p = parts[i].p;
            int gteInNode = (tr - tl + 1) - p;
            if (k > gteInNode) { k -= gteInNode; continue; }
            while (tl < tr) {
                int mid = (tl + tr) >> 1;
                int lp = leftCount(d, tl, p);
                int leftGte = (mid - tl + 1) - lp;
                if (k <= leftGte) { tr = mid; p = lp; }
                else              { k -= leftGte; tl = mid + 1; p -= lp; }
                d++;
            }
            return tl;
        }
        return -1;
    }

    // O(log n) — array index (POSITION, not value) of the k-th element <= x in
    // [ql, qr], 1-indexed k, scanning left to right. Returns -1 if fewer than k exist.
    int findKthLteX(int ql, int qr, int k, int x) const {
        if (ql < 0) ql = 0;
        if (qr > n - 1) qr = n - 1;
        if (ql > qr || k <= 0) return -1;
        int p0 = (int)(upper_bound(sortedVals.begin(), sortedVals.end(), x) - sortedVals.begin());
        Part parts[80];
        int m = decompose(ql, qr, p0, parts);
        for (int i = 0; i < m; i++) {
            int d = parts[i].d, tl = parts[i].tl, tr = parts[i].tr, p = parts[i].p;
            if (k > p) { k -= p; continue; }
            while (tl < tr) {
                int mid = (tl + tr) >> 1;
                int lp = leftCount(d, tl, p);
                if (k <= lp) { tr = mid; p = lp; }
                else         { k -= lp; tl = mid + 1; p -= lp; }
                d++;
            }
            return tl;
        }
        return -1;
    }
};
