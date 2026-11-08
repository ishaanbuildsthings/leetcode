// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/bit-operations/XorBasis.cpp
#include <bits/stdc++.h>
using namespace std;

// XorBasis: every value you can make by XORing together some subset of the inserted values (a linear basis over bits).
// The empty subset counts, so 0 can always be made. Values are long long and must be >= 0 (up to 2^63 - 1); a
// negative value throws invalid_argument.
// B = number of bits in the largest value inserted, N = number of values inserted.
//
// XorBasis basis;          // nothing inserted yet
// XorBasis basis(arr);     // inserts every value of arr (a vector of int / long long)
//
// Max subset XOR:                 XorBasis(arr).maxXor()
// Number of distinct subset XORs: XorBasis(arr).countDistinctXors()
// Subsets whose XOR is exactly k: XorBasis(arr).countSubsetsMakingMod(k, 1'000'000'007)
struct XorBasis {
    // pivots[b] = the basis value whose highest set bit is b, or 0 if none. Kept fully reduced: bit b is set in no
    // other basis value, which is what makes kthSmallestXor work
    long long pivots[63] = {};
    int topBit = -1;   // highest b with pivots[b] != 0
    int numPivots = 0;
    long long numInserted = 0;

    XorBasis() {}

    // O(N * B)
    template <class T>
    explicit XorBasis(const vector<T>& arr) {
        for (auto x : arr) {
            insert(x);
        }
    }

    // inserts x; returns true if x couldn't be made before (the basis grew), else false
    // O(B)
    bool insert(long long x) {
        if (x < 0) {
            throw invalid_argument("XorBasis::insert: " + to_string(x) + " is negative");
        }
        numInserted++;
        for (int b = min(topBit, highestBit(x)); b >= 0; b--) {
            if ((x >> b & 1) && pivots[b]) {
                x ^= pivots[b];
            }
        }
        if (x == 0) {
            return false;
        }
        int top = highestBit(x);
        for (int b = top + 1; b <= topBit; b++) {
            if (pivots[b] >> top & 1) {
                pivots[b] ^= x;
            }
        }
        pivots[top] = x;
        topBit = max(topBit, top);
        numPivots++;
        return true;
    }

    // true if some subset XORs to exactly x (x = 0 is always true: the empty subset)
    // O(B)
    bool canMake(long long x) const {
        return x >= 0 && minXorWith(x) == 0;
    }

    // largest XOR of any subset (0 if nothing inserted)
    // XorBasis(vector<int>{3, 10, 5}).maxXor() -> 15   // 10 ^ 5
    // O(B)
    long long maxXor() const {
        return maxXorWith(0);
    }

    // largest x ^ (XOR of some subset)
    // XorBasis(vector<int>{3, 10, 5}).maxXorWith(4) -> 14   // 4 ^ 10
    // O(B)
    long long maxXorWith(long long x) const {
        if (x < 0) {
            throw invalid_argument("XorBasis::maxXorWith: " + to_string(x) + " is negative");
        }
        for (int b = topBit; b >= 0; b--) {
            if (pivots[b] && !(x >> b & 1)) {
                x ^= pivots[b];
            }
        }
        return x;
    }

    // smallest x ^ (XOR of some subset)
    // XorBasis(vector<int>{3, 10, 5}).minXorWith(15) -> 0   // 15 = 10 ^ 5
    // O(B)
    long long minXorWith(long long x) const {
        if (x < 0) {
            throw invalid_argument("XorBasis::minXorWith: " + to_string(x) + " is negative");
        }
        for (int b = topBit; b >= 0; b--) {
            if (pivots[b] && (x >> b & 1)) {
                x ^= pivots[b];
            }
        }
        return x;
    }

    // smallest XOR of a non-empty subset: 0 if some non-empty subset XORs to 0, -1 if nothing inserted
    // XorBasis(vector<int>{3, 10, 5}).minNonzeroXor() -> 3
    // XorBasis(vector<int>{3, 5, 6}).minNonzeroXor() -> 0   // 3 ^ 5 ^ 6 = 0
    // O(B)
    long long minNonzeroXor() const {
        if (numInserted > numPivots) {
            return 0;
        }
        for (int b = 0; b <= topBit; b++) {
            if (pivots[b]) {
                return pivots[b];
            }
        }
        return -1;
    }

    // the kth smallest distinct value some subset makes, k 0-indexed (k = 0 -> 0, the empty subset), or -1 if
    // k >= countDistinctXors()
    // XorBasis(vector<int>{1, 2}).kthSmallestXor(3) -> 3   // the makeable values are 0, 1, 2, 3
    // O(B)
    long long kthSmallestXor(long long k) const {
        if (k < 0) {
            throw invalid_argument("XorBasis::kthSmallestXor: k = " + to_string(k) + " is negative");
        }
        if (numPivots < 63 && (k >> numPivots)) {
            return -1;
        }
        long long res = 0;
        int i = 0;
        for (int b = 0; b <= topBit; b++) {
            if (pivots[b]) {
                if (k >> i & 1) {
                    res ^= pivots[b];
                }
                i++;
            }
        }
        return res;
    }

    // number of distinct values the subsets make, counting 0 from the empty subset: 2^rank
    // XorBasis(vector<int>{3, 5, 6}).countDistinctXors() -> 4   // 0, 3, 5, 6
    // O(1)
    unsigned long long countDistinctXors() const {
        return 1ULL << numPivots;
    }

    // number of subsets of the inserted values (by position, the empty one included) whose XOR is exactly x, mod mod:
    // 2^(N - rank) if x can be made, else 0
    // XorBasis(vector<int>{3, 5, 6}).countSubsetsMakingMod(0, 1'000'000'007) -> 2   // {} and {3, 5, 6}
    // O(B + log(N))
    long long countSubsetsMakingMod(long long x, long long mod) const {
        if (!canMake(x)) {
            return 0;
        }
        long long res = 1 % mod;
        long long base = 2 % mod;
        for (long long e = numInserted - numPivots; e > 0; e >>= 1) {
            if (e & 1) {
                res = (long long)((__int128)res * base % mod);
            }
            base = (long long)((__int128)base * base % mod);
        }
        return res;
    }

    // size of the basis (how many inserted values were independent)
    // O(1)
    int rank() const {
        return numPivots;
    }

    // how many values were inserted, including ones that didn't grow the basis
    // O(1)
    long long size() const {
        return numInserted;
    }

    // the basis values, largest first (rank of them; their subset XORs make exactly the makeable values)
    // O(B)
    vector<long long> basis() const {
        vector<long long> res;
        for (int b = topBit; b >= 0; b--) {
            if (pivots[b]) {
                res.push_back(pivots[b]);
            }
        }
        return res;
    }

    // inserts everything other holds, as if other's values had been inserted here (size grows by other.size())
    // O(B^2)
    void merge(const XorBasis& other) {
        for (long long p : other.basis()) {
            insert(p);
        }
        numInserted += other.numInserted - other.numPivots;
    }

private:
    static int highestBit(long long x) {
        return x ? 63 - __builtin_clzll(x) : -1;
    }
};
