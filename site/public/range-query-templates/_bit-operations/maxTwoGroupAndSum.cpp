// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/bit-operations/maxTwoGroupAndSum.cpp
#include <bits/stdc++.h>
using namespace std;

// max of AND(A) + AND(B) over every split of arr into two non-empty groups A and B (each value in exactly one)
// Why it works: say x = AND(A). Moving into A every other value that contains all of x's bits keeps AND(A) = x and
// leaves B smaller, so AND(B) can only grow. So some best split has A = "every value that is a supermask of x" for a
// mask x, and the answer is the best of those (or 2 * AND(all), when both groups' ANDs equal it). A count of the
// supermasks of every mask (SOS DP) gives each candidate's two ANDs bit by bit.
// B = number of bits in max(arr): 2^B masks are tried, so values up to about 2^20 fit. Values must be >= 0; needs at
// least 2 values.
// maxTwoGroupAndSum(vector<int>{3, 3, 4, 4}) -> 7   // {3, 3} and {4, 4}: 3 + 4
// O(B * 2^B + N)
template <class T>
long long maxTwoGroupAndSum(const vector<T>& arr) {
    int n = (int)arr.size();
    if (n < 2) throw invalid_argument("maxTwoGroupAndSum: needs at least 2 values");
    T mx = 0;
    for (const T& v : arr) {
        if (v < 0) throw invalid_argument("maxTwoGroupAndSum: a value is negative");
        mx = max(mx, v);
    }
    int bits = 0;
    while (bits < 31 && (T(1) << bits) <= mx) bits++;
    if ((T(1) << bits) <= mx) throw invalid_argument("maxTwoGroupAndSum: values must be below 2^31");
    int size = 1 << bits;
    vector<int> sup(size);  // sup[mask] = how many values contain every bit of mask
    for (const T& v : arr) sup[(size_t)v]++;
    for (int b = 0; b < bits; b++)
        for (int m = 0; m < size; m++)
            if (!(m >> b & 1)) sup[m] += sup[m | 1 << b];
    long long allAnd = 0;
    for (int b = 0; b < bits; b++)
        if (sup[1 << b] == n) allAnd |= 1LL << b;
    long long best = 2 * allAnd;
    for (int x = 0; x < size; x++) {
        int inA = sup[x];
        if (inA == 0 || inA == n) continue;
        long long andA = 0, andB = 0;
        for (int b = 0; b < bits; b++) {
            int withInA = sup[x | 1 << b];  // values in A with bit b
            if (withInA == inA) andA |= 1LL << b;
            if (sup[1 << b] - withInA == n - inA) andB |= 1LL << b;
        }
        best = max(best, andA + andB);
    }
    return best;
}
