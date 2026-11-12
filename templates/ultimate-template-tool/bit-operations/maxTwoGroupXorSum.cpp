// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/bit-operations/maxTwoGroupXorSum.cpp
#include <bits/stdc++.h>
using namespace std;

// max of XOR(A) + XOR(B) over every split of arr into two non-empty groups A and B (each value in exactly one)
// Why it works: with T = XOR of every value, XOR(B) = XOR(A) ^ T. A bit set in T is in exactly one of the two, so it
// adds 2^bit whatever the split; a bit clear in T is in both or in neither. So clear T's bits in every value, take the
// largest XOR M of a subset of what's left (a XOR basis), and the answer is T + 2 * M.
// Values must be >= 0 (long long); needs at least 2 values. The answer is unsigned: it can pass 2^63.
// maxTwoGroupXorSum(vector<long long>{1, 2, 3}) -> 6   // {1, 2} and {3}: 3 + 3
// O(N * B)
unsigned long long maxTwoGroupXorSum(const vector<long long>& arr) {
    if (arr.size() < 2) throw invalid_argument("maxTwoGroupXorSum: needs at least 2 values");
    long long total = 0;
    for (long long v : arr) {
        if (v < 0) throw invalid_argument("maxTwoGroupXorSum: a value is negative");
        total ^= v;
    }
    long long pivots[63] = {};  // pivots[b] = the basis value whose highest set bit is b, or 0
    for (long long v : arr) {
        long long x = v & ~total;
        for (int b = 62; b >= 0 && x; b--) {
            if (!(x >> b & 1)) continue;
            if (!pivots[b]) {
                pivots[b] = x;
                break;
            }
            x ^= pivots[b];
        }
    }
    long long best = 0;
    for (int b = 62; b >= 0; b--) best = max(best, best ^ pivots[b]);
    // (best > 0 comes from a non-empty subset that isn't every value: all of them XOR to 0 once T's bits are cleared)
    return (unsigned long long)total + 2ULL * (unsigned long long)best;
}
