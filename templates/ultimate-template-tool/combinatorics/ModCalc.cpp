// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/combinatorics/ModCalc.cpp
// template by: https://github.com/agrawalishaan/leetcode

#include <bits/stdc++.h>
using namespace std;

// n in the constructor is basically the biggest number we will operate on. So for instance finding n! % MOD.
// But also things like interleaving two sequences of length 500 and length 700 would require n=1200.
// To be safe, can always just put a big number like 1e5. n may be >= primeMod: x! % MOD is 0 from x = MOD on,
// 1/x! doesn't exist there, and nChooseK / nPermuteK / interleave still give the right answer
class ModCalc {
public:
    // O(n) time, O(n) space (two arrays of length n+1)
    // primeMod must be prime, otherwise anything using modInv may break (fermat's little theorem)
    ModCalc(int n, long long primeMod) : n(n), mod(primeMod) {
        buildFactorialsWithMod();
        buildInverseFactorialsWithMod();
    }

    // ********** STUFF WITH FACTORIALS **********

    // Gets (x! % MOD)
    // O(1) time
    long long getFactorialWithMod(int factorial) const {
        assert(0 <= factorial && factorial <= n);
        return factorialsWithMod[factorial];
    }

    // Gets (1/x! % MOD), which only exists for x < MOD
    // O(1) time
    long long getInverseFactorialWithMod(int inverseFactorial) const {
        assert(0 <= inverseFactorial && inverseFactorial <= n && inverseFactorial < mod);
        return inverseFactorialsWithMod[inverseFactorial];
    }

    // Given two sequences of length X and Y, such as "123" and "4567", find the # of ways to interleave them.
    // Note we don't care about the actual items in each sequence, we just care about the # of ways we can interleave
    // the two. We don't even get the actual sequences themselves, just their lengths.
    // O(1) time (O(log n) if length1 + length2 >= MOD)
    long long interleaveTwoSequencesWithMod(int length1, int length2) const {
        // Interleaving a sequence of length 3 and 4 would be like 7!/(3!4!), which is 7! * (1/3!) * (1/4!)
        int combinedLength = length1 + length2;
        assert(combinedLength <= n); // need the factorial array to reach combinedLength
        return nChooseKWithMod(combinedLength, length1);
    }

    // Calculates the # of ways to select k items from n unique items. Order does not matter.
    // Formula for C(n, k) = n! / (k!(n-k)!)
    // O(1) time (O(log n) if n >= MOD: Lucas, since those factorials have no inverse)
    long long nChooseKWithMod(int n, int k) const {
        if (k < 0 || k > n) return 0;
        if (n >= mod) return modMultiply(nChooseKWithMod(n % mod, k % mod), nChooseKWithMod(n / mod, k / mod));
        return modMultiply(getFactorialWithMod(n),
                           getInverseFactorialWithMod(k),
                           getInverseFactorialWithMod(n - k));
    }

    // Calculates the # of ways to select k items from n unique items. Order matters.
    // Formula for P(n, k) = n! / (n-k)!
    // O(1) time
    long long nPermuteKWithMod(int n, int k) const {
        if (k < 0 || k > n) return 0;
        if (n >= mod) {  // k consecutive numbers: 0 if one is a multiple of MOD, else the same as starting from n % MOD
            if (k > n % mod) return 0;
            n %= mod;
        }
        return modMultiply(getFactorialWithMod(n), getInverseFactorialWithMod(n - k));
    }

    // Calculate the # of ways to distribute n identical items into k distinct buckets (relates to stars and bars)
    // Formula for allowing empty buckets is C(n+k-1, k-1)
    // Formula for NOT allowing empty buckets is C(n-1, k-1)
    // O(1) time
    long long waysToPutIdenticalItemsIntoDistinctBucketsWithMod(int items, int buckets,
                                                                bool allowEmptyBuckets = true) const {
        if (buckets == 0) return items == 0 ? 1 % mod : 0;
        if (allowEmptyBuckets) return nChooseKWithMod(items + buckets - 1, buckets - 1);
        return nChooseKWithMod(items - 1, buckets - 1);
    }

    // Putting n distinct items into k distinct buckets is just k options for the first item, k for the second, etc,
    // so k^n. This is if we allow empty buckets. If we don't allow empty buckets, we need Stirling numbers of the
    // second kind.
    // O(log items) time
    long long waysToPutDistinctItemsIntoDistinctBucketsAllowingEmptyWithMod(int items, int buckets) const {
        return modPow(buckets, items);
    }

    // ********** NO FACTORIALS NEEDED **********

    // Multiplies k numbers together. Handles negative inputs.
    // O(k) time
    template <typename... Args>
    long long modMultiply(Args... nums) const {
        long long result = 1;
        ((result = result * normalize(nums) % mod), ...);
        return result;
    }

    // Calculates base^exponent % MOD
    // O(log exponent) time
    long long modPow(long long base, long long exponent) const {
        long long result = 1, cur = normalize(base);
        while (exponent > 0) {
            if (exponent & 1) result = result * cur % mod;
            cur = cur * cur % mod;
            exponent >>= 1;
        }
        return result;
    }

    // Gets 1/x % MOD. num must be coprime to MOD.
    // O(log MOD) time
    long long modInv(long long num) const { return modPow(num, mod - 2); }

private:
    int n;
    long long mod;
    vector<long long> factorialsWithMod;
    vector<long long> inverseFactorialsWithMod;

    long long normalize(long long x) const {
        x %= mod;
        return x < 0 ? x + mod : x;
    }

    // O(n) time to build a factorial mod array
    void buildFactorialsWithMod() {
        factorialsWithMod.assign(n + 1, 1); // 0 factorial is 1
        for (int factorial = 1; factorial <= n; factorial++) {
            factorialsWithMod[factorial] = factorialsWithMod[factorial - 1] * factorial % mod;
        }
    }

    // O(n) time to build an inverse factorial mod array
    void buildInverseFactorialsWithMod() {
        inverseFactorialsWithMod.assign(n + 1, 1);
        int top = (int)min((long long)n, mod - 1);  // from MOD on, x! % MOD is 0 and has no inverse
        inverseFactorialsWithMod[top] = modInv(factorialsWithMod[top]);
        for (int i = top - 1; i >= 0; i--) {
            inverseFactorialsWithMod[i] = inverseFactorialsWithMod[i + 1] * (i + 1) % mod;
        }
    }
};

class MoreAdvancedStirlingStuff {
public:
    // O(maxPossibleDistinctItemCount * maxPossibleBucketCount) time and space
    MoreAdvancedStirlingStuff(int maxPossibleDistinctItemCount, int maxPossibleBucketCount, long long mod)
        : maxPossibleDistinctItemCount(maxPossibleDistinctItemCount),
          maxPossibleBucketCount(maxPossibleBucketCount),
          mod(mod),
          modCalc(maxPossibleBucketCount, mod) {
        buildStirling2Dp();
    }

    // Calculate the # of ways to distribute n distinct items into k identical non-empty buckets. For instance with
    // items 'A' and 'B' and 2 buckets, there's only one way, since the buckets are identical.
    // This is stirling2 numbers.
    // O(1) time
    long long waysToPutDistinctItemsIntoIdenticalNonemptyBucketsWithMod(int items, int buckets) const {
        return stirling2Dp[items][buckets];
    }

    // Calculate the # of ways to distribute n distinct items into k distinct non-empty buckets.
    // O(1) time
    long long waysToPutDistinctItemsIntoDistinctNonemptyBucketsWithMod(int items, int buckets) const {
        long long waysAssumingIdenticalBuckets = stirling2Dp[items][buckets];
        long long bucketOrderings = modCalc.getFactorialWithMod(buckets);
        return modCalc.modMultiply(waysAssumingIdenticalBuckets, bucketOrderings);
    }

private:
    int maxPossibleDistinctItemCount;
    int maxPossibleBucketCount;
    long long mod;
    ModCalc modCalc; // built so we can get factorial mods
    vector<vector<long long>> stirling2Dp;

    void buildStirling2Dp() {
        stirling2Dp.assign(maxPossibleDistinctItemCount + 1, vector<long long>(maxPossibleBucketCount + 1, 0));
        stirling2Dp[0][0] = 1;
        for (int i = 1; i <= maxPossibleDistinctItemCount; i++) {
            for (int j = 1; j <= maxPossibleBucketCount; j++) {
                stirling2Dp[i][j] = (stirling2Dp[i - 1][j - 1] + j * stirling2Dp[i - 1][j]) % mod;
            }
        }
    }
};