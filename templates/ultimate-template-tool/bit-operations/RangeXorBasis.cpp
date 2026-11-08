// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/bit-operations/RangeXorBasis.cpp
#include <bits/stdc++.h>
using namespace std;

// RangeXorBasis: XOR basis questions about any subarray arr[l..r] (inclusive), answered online. Values must be >= 0
// (long long). Keeps, for every prefix, a basis that prefers the most recent elements; the basis values whose element
// is at index >= l make exactly the subset XORs of arr[l..r].
// N = arr.size(), B = number of bits in max(arr). Invalid ranges and negative values throw.
//
// RangeXorBasis rxb(vector<int>{3, 10, 5, 6});
// rxb.maxXorInRange(1, 3) -> 15   // 10 ^ 5
// rxb.canMakeInRange(0, 1, 9) -> true   // 3 ^ 10
struct RangeXorBasis {
    int n = 0;
    int B = 0;
    // block i (indexes i*B .. i*B + B - 1) is the basis after arr[0..i]: vals[i*B + b] = the basis value whose highest
    // set bit is b (0 if none), poss[i*B + b] = the index of the newest element it uses (-1 if none)
    vector<long long> vals;
    vector<int> poss;

    // O(N * B) time and space
    template <class T>
    explicit RangeXorBasis(const vector<T>& arr) : n((int)arr.size()) {
        long long mx = 0;
        for (auto x : arr) {
            if (x < 0) {
                throw invalid_argument("RangeXorBasis: value " + to_string((long long)x) + " is negative");
            }
            mx = max(mx, (long long)x);
        }
        B = mx ? 64 - __builtin_clzll(mx) : 0;
        vals.assign((size_t)n * B, 0);
        poss.assign((size_t)n * B, -1);
        vector<long long> curVals(B, 0);
        vector<int> curPoss(B, -1);
        for (int i = 0; i < n; i++) {
            long long x = arr[i];
            int pos = i;
            for (int b = B - 1; b >= 0; b--) {
                if (!(x >> b & 1)) {
                    continue;
                }
                if (!curVals[b]) {
                    curVals[b] = x;
                    curPoss[b] = pos;
                    break;
                }
                if (curPoss[b] < pos) {
                    swap(curVals[b], x);
                    swap(curPoss[b], pos);
                }
                x ^= curVals[b];
            }
            copy(curVals.begin(), curVals.end(), vals.begin() + (size_t)i * B);
            copy(curPoss.begin(), curPoss.end(), poss.begin() + (size_t)i * B);
        }
    }

    // largest XOR of any subset of arr[l..r] (the empty subset gives 0)
    // O(B)
    long long maxXorInRange(int l, int r) const {
        return maxXorWithInRange(l, r, 0);
    }

    // largest x ^ (XOR of some subset of arr[l..r])
    // O(B)
    long long maxXorWithInRange(int l, int r, long long x) const {
        check(l, r);
        if (x < 0) {
            throw invalid_argument("RangeXorBasis::maxXorWithInRange: " + to_string(x) + " is negative");
        }
        size_t base = (size_t)r * B;
        for (int b = B - 1; b >= 0; b--) {
            if (poss[base + b] >= l && !(x >> b & 1)) {
                x ^= vals[base + b];
            }
        }
        return x;
    }

    // true if some subset of arr[l..r] XORs to exactly x (x = 0 is always true: the empty subset)
    // O(B)
    bool canMakeInRange(int l, int r, long long x) const {
        check(l, r);
        if (x < 0 || (B < 63 && (x >> B))) {
            return false;
        }
        size_t base = (size_t)r * B;
        for (int b = B - 1; b >= 0; b--) {
            if (x >> b & 1) {
                if (poss[base + b] < l) {
                    return false;
                }
                x ^= vals[base + b];
            }
        }
        return true;
    }

    // size of the basis of arr[l..r] (how many of its values are independent)
    // O(B)
    int rankInRange(int l, int r) const {
        check(l, r);
        size_t base = (size_t)r * B;
        int res = 0;
        for (int b = 0; b < B; b++) {
            if (poss[base + b] >= l) {
                res++;
            }
        }
        return res;
    }

    // number of distinct values the subsets of arr[l..r] make, counting 0 from the empty subset: 2^rank
    // O(B)
    unsigned long long countDistinctXorsInRange(int l, int r) const {
        return 1ULL << rankInRange(l, r);
    }

private:
    void check(int l, int r) const {
        if (!(0 <= l && l <= r && r < n)) {
            throw out_of_range("RangeXorBasis: range [" + to_string(l) + ", " + to_string(r) + "] is not inside [0, "
                               + to_string(n - 1) + "] with l <= r");
        }
    }
};
