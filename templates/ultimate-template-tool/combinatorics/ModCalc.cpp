// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/combinatorics/ModCalc.cpp
#include <bits/stdc++.h>
using namespace std;
using ll = long long;

// ModCalc calc;                // mod 1e9 + 7
// ModCalc calc(998244353);     // your own mod (the ops marked "mod must be prime" need a prime)
// @if nChooseKWithMod
// calc.nChooseKWithMod(5, 2) -> 10
// @endif
// @if waysToPutIdenticalItemsIntoDistinctBucketsWithMod
// calc.waysToPutIdenticalItemsIntoDistinctBucketsWithMod(3, 2, true)   -> 4   (allowEmptyBuckets = true)
// calc.waysToPutIdenticalItemsIntoDistinctBucketsWithMod(3, 2, false)  -> 2
// @endif
// @if getFactorialWithMod getInverseFactorialWithMod nChooseKWithMod nPermuteKWithMod interleaveTwoSequencesWithMod waysToPutIdenticalItemsIntoDistinctBucketsWithMod waysToPutDistinctItemsIntoDistinctBucketsWithMod
// GROWS LAZILY: no size to pick. The constructor builds nothing; the factorial tables grow inside the calls you make
// (doubling), so every call just works and later calls reuse what's built (make it static / global to share it across
// test cases). Each op below says which of its arguments makes the tables grow; growing costs O(the largest such value)
// in total.
// @endif
struct ModCalc {
    ll mod;
    // @if getFactorialWithMod getInverseFactorialWithMod nChooseKWithMod nPermuteKWithMod interleaveTwoSequencesWithMod waysToPutIdenticalItemsIntoDistinctBucketsWithMod waysToPutDistinctItemsIntoDistinctBucketsWithMod
    vector<ll> fact{1};     // fact[x] = x! % mod
    vector<ll> invFact{1};  // invFact[x] = 1 / x! % mod (0 from x = mod on: no inverse there)
    // @endif

    // O(1) -- the ops that divide (marked "mod must be prime") get inverses from Fermat's little theorem
    explicit ModCalc(ll mod = 1000000007) : mod(mod) {}

    ll power(ll base, ll exponent) const {
        ll result = 1 % mod;
        base %= mod;
        if (base < 0) base += mod;
        for (; exponent > 0; exponent >>= 1, base = base * base % mod)
            if (exponent & 1) result = result * base % mod;
        return result;
    }

    // @if getFactorialWithMod getInverseFactorialWithMod nChooseKWithMod nPermuteKWithMod interleaveTwoSequencesWithMod waysToPutIdenticalItemsIntoDistinctBucketsWithMod waysToPutDistinctItemsIntoDistinctBucketsWithMod
    void grow(ll x) {
        // afterwards the tables cover 0..x (at least doubling, so each value is built once over the instance's life)
        ll old = fact.size();
        if (x < old) return;
        ll size = max(x + 1, 2 * old);
        fact.resize(size), invFact.resize(size, 0);
        for (ll i = old; i < size; i++) fact[i] = fact[i - 1] * (i % mod) % mod;
        ll top = min(size - 1, mod - 1);
        if (top >= old) {
            invFact[top] = power(fact[top], mod - 2);
            for (ll i = top; i > old; i--) invFact[i - 1] = invFact[i] * (i % mod) % mod;
        }
    }

    // @endif
    // @if getFactorialWithMod
    // O(1) amortized, lazily grows the factorial tables when called with a bigger x than before (see the top) -- x! %
    // mod (0 once x >= mod)
    ll getFactorialWithMod(ll x) {
        if (x >= mod) return 0;
        grow(x);
        return fact[x];
    }

    // @endif
    // @if getInverseFactorialWithMod
    // O(1) amortized, lazily grows the factorial tables when called with a bigger x than before (see the top) -- 1 / x!
    // % mod; needs x < mod (x! has no inverse after that), else invalid_argument; mod must be prime
    ll getInverseFactorialWithMod(ll x) {
        if (x >= mod) throw invalid_argument("getInverseFactorialWithMod: x! has no inverse");
        grow(x);
        return invFact[x];
    }

    // @endif
    // @if nChooseKWithMod interleaveTwoSequencesWithMod waysToPutIdenticalItemsIntoDistinctBucketsWithMod waysToPutDistinctItemsIntoDistinctBucketsWithMod
    // O(1) amortized, lazily grows the factorial tables when called with a bigger n (k doesn't matter) than before (see
    // the top); O(log n) once n >= mod (Lucas) -- ways to choose k of n distinct items, order ignored;
    // 0 if k < 0 or k > n; mod must be prime
    ll nChooseKWithMod(ll n, ll k) {
        if (k < 0 || k > n) return 0;
        if (n >= mod) return nChooseKWithMod(n % mod, k % mod) * nChooseKWithMod(n / mod, k / mod) % mod;
        grow(n);
        return fact[n] * invFact[k] % mod * invFact[n - k] % mod;
    }

    // @endif
    // @if nPermuteKWithMod
    // O(1) amortized, lazily grows the factorial tables when called with a bigger n (k doesn't matter) than before (see
    // the top) -- ways to choose k of n distinct items in order; 0 if k < 0 or k > n; mod must be prime
    ll nPermuteKWithMod(ll n, ll k) {
        if (k < 0 || k > n) return 0;
        if (n >= mod) {
            // k consecutive numbers: 0 if one is a multiple of mod, else the same as starting from n % mod
            if (k > n % mod) return 0;
            n %= mod;
        }
        grow(n);
        return fact[n] * invFact[n - k] % mod;
    }

    // @endif
    // @if interleaveTwoSequencesWithMod
    // O(1) amortized, lazily grows the factorial tables when called with a bigger length1 + length2 than before (see
    // the top) -- ways to interleave a sequence of length1 items with one of length2, keeping each one's order;
    // mod must be prime
    ll interleaveTwoSequencesWithMod(ll length1, ll length2) { return nChooseKWithMod(length1 + length2, length1); }

    // @endif
    // @if waysToPutIdenticalItemsIntoDistinctBucketsWithMod
    // O(1) amortized, lazily grows the factorial tables when called with a bigger items + buckets than before (see the
    // top) -- identical items into distinct buckets (stars and bars); allowEmptyBuckets (required, no default): may a
    // bucket stay empty; mod must be prime
    ll waysToPutIdenticalItemsIntoDistinctBucketsWithMod(ll items, ll buckets, bool allowEmptyBuckets) {
        if (buckets == 0) return items == 0 ? 1 % mod : 0;
        return allowEmptyBuckets ? nChooseKWithMod(items + buckets - 1, buckets - 1) : nChooseKWithMod(items - 1,
            buckets - 1);
    }

    // @endif
    // @if waysToPutDistinctItemsIntoDistinctBucketsWithMod
    // O(log items) with allowEmptyBuckets, else O(buckets * log items) (that also lazily grows the factorial tables
    // when called with a bigger buckets than before, already inside this cost) -- distinct items into distinct buckets;
    // allowEmptyBuckets (required, no default): may a bucket stay empty (then it's buckets^items and works for any mod;
    // otherwise mod must be prime)
    ll waysToPutDistinctItemsIntoDistinctBucketsWithMod(ll items, ll buckets, bool allowEmptyBuckets) {
        if (allowEmptyBuckets) return power(buckets, items);
        ll total = 0;  // inclusion-exclusion over the buckets left empty
        for (ll empty = 0; empty <= buckets; empty++) {
            ll term = nChooseKWithMod(buckets, empty) * power(buckets - empty, items) % mod;
            total = (empty % 2 ? total - term + mod : total + term) % mod;
        }
        return total;
    }

    // @endif
    // @if modPow
    // O(log exponent) -- base^exponent % mod; works for any mod
    ll modPow(ll base, ll exponent) const { return power(base, exponent); }

    // @endif
    // @if modInv
    // O(log mod) -- 1 / x % mod; x must not be a multiple of mod, else invalid_argument; mod must be prime
    ll modInv(ll x) const {
        if (x % mod == 0) throw invalid_argument("modInv: x has no inverse");
        return power(x, mod - 2);
    }
    // @endif
};
