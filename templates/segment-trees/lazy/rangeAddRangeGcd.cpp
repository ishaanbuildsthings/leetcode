// TEMPLATE BY https://github.com/ishaanbuildsthings

// ========================
// COMPLEXITIES

// O(n) build time, O(n) memory

// O(log n * log maxVal) rangeAdd(l, r, x)
// O(log n) pointQuery(i) -> value
// O(log n + log maxVal) rangeGcd(l, r) -> gcd

// ========================
/*
How does range add + range gcd work?

The gcd of a group of numbers doesn't change if we swap every number except one for its difference with a neighbor.
Think of each number as a node and each adjacent difference as an edge. Starting from one real value (the anchor),
walking an edge only adds a known difference, so anything dividing the anchor and every edge divides every number
we reach. The adjacent differences form a chain touching every node, so the gcd of a range is the first value in the
range gcd'd with the differences strictly inside the range. The difference entering the range connects to a number
outside it and must not be used.

Adding x to a whole range leaves every difference inside it unchanged. Only two differences move: the one entering
the range goes up by x, and the one leaving it goes down by x. So a range add is two point changes on the difference
array.

We keep that one difference array in two structures:
-a Fenwick tree, since summing the differences up to a position gives the real value there (the anchor)
-a gcd segment tree, for the gcd of the differences inside a range

Example: [6, 10, 14, 22, 30], differences [_, 4, 4, 8, 8]
rangeGcd(1, 3) = gcd(10, 4, 8) = 2 (anchor 10, then the two differences inside, never the 4 entering at index 1)

Overflow: values (and differences between neighbors) must stay within long long. Values up to 1e18 are fine.
*/

// ========================

#include <bits/stdc++.h>
using namespace std;

struct RangeAddRangeGcd {
    int n;
    vector<long long> diff;
    vector<long long> fen;
    vector<long long> seg;

    // O(n)
    RangeAddRangeGcd(const vector<long long>& arr) : n((int)arr.size()), diff(n), fen(n + 1, 0), seg(2 * n, 0) {
        diff[0] = arr[0];
        for (int i = 1; i < n; i++) {
            diff[i] = arr[i] - arr[i - 1];
        }

        for (int i = 1; i <= n; i++) {
            fen[i] += diff[i - 1];
            int parent = i + (i & -i);
            if (parent <= n) {
                fen[parent] += fen[i];
            }
        }

        // leaf 0 stays 0 (it holds the anchor in diff, not a real difference)
        for (int i = 1; i < n; i++) {
            seg[n + i] = llabs(diff[i]);
        }
        for (int p = n - 1; p > 0; p--) {
            seg[p] = gcd(seg[2 * p], seg[2 * p + 1]);
        }
    }

    //################### PUBLIC METHODS START HERE ####################

    // O(log n * log maxVal) -- adds x to every arr[l...r] inclusive. requires 0 <= l <= r < n, x may be negative
    void rangeAdd(int l, int r, long long x) {
        shiftDiff(l, x);
        if (r + 1 < n) {
            shiftDiff(r + 1, -x);
        }
    }

    // O(log n) -- current value of arr[i]
    long long pointQuery(int i) {
        return fenPrefix(i);
    }

    // O(log n + log maxVal) -- gcd of arr[l...r] inclusive, always >= 0. requires 0 <= l <= r < n
    // returns 0 only if every value in the range is 0
    long long rangeGcd(int l, int r) {
        long long res = llabs(fenPrefix(l));
        if (l < r) {
            res = gcd(res, segQuery(l + 1, r));
        }
        return res;
    }

private:
    void fenAdd(int i, long long x) {
        for (i++; i <= n; i += i & -i) {
            fen[i] += x;
        }
    }

    long long fenPrefix(int i) {
        long long total = 0;
        for (i++; i > 0; i -= i & -i) {
            total += fen[i];
        }
        return total;
    }

    void segSet(int i, long long val) {
        int p = i + n;
        seg[p] = val;
        for (p >>= 1; p > 0; p >>= 1) {
            seg[p] = gcd(seg[2 * p], seg[2 * p + 1]);
        }
    }

    long long segQuery(int l, int r) {
        long long res = 0;
        for (l += n, r += n + 1; l < r; l >>= 1, r >>= 1) {
            if (l & 1) {
                res = gcd(res, seg[l++]);
            }
            if (r & 1) {
                res = gcd(res, seg[--r]);
            }
        }
        return res;
    }

    void shiftDiff(int i, long long x) {
        diff[i] += x;
        fenAdd(i, x);
        if (i >= 1) {
            segSet(i, llabs(diff[i]));
        }
    }
};

// EXAMPLE IN USE:
// Row GCD (CF 1458A): gcd(a[0] + b, a[1] + b, ...) for each b
// RangeAddRangeGcd rg(a);
// for (long long b : bs) {
//     rg.rangeAdd(0, n - 1, b);
//     cout << rg.rangeGcd(0, n - 1) << ' ';
//     rg.rangeAdd(0, n - 1, -b);
// }