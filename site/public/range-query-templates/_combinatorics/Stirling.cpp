// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/combinatorics/Stirling.cpp
#include <bits/stdc++.h>
using namespace std;
using ll = long long;

// Distinct items into buckets (Stirling numbers of the second kind):
// @if formulaIdentical formulaDistinct
//   StirlingByFormula: no setup or memory, but every call costs O(buckets * log items). Best for a few calls, or huge
//                      item counts. mod must be prime.
// @endif
// @if tableIdentical tableDistinct
//   StirlingByTable:   every call is O(1) once the table covers it; the table grows on demand (doubling), so building
//                      costs O(largest items * largest buckets) in total, and that much memory. Best for many calls.
//                      Works for any mod.
// @endif
// @if formulaIdentical formulaDistinct
// StirlingByFormula calc(998244353);     // your own mod (must be prime here)
// @endif
// @if tableIdentical tableDistinct
// StirlingByTable calc(1000);            // your own mod (any mod)
// @endif
// @if formulaIdentical tableIdentical
// calc.waysToPutDistinctItemsIntoIdenticalBucketsWithMod(3, 2, false) -> 3   {a}{bc}, {b}{ac}, {c}{ab}
// calc.waysToPutDistinctItemsIntoIdenticalBucketsWithMod(3, 2, true)  -> 4   those 3, plus {abc}{}
// @endif
// @if formulaDistinct tableDistinct
// calc.waysToPutDistinctItemsIntoDistinctBucketsWithMod(3, 2, false)  -> 6   3 times 2 bucket orders
// calc.waysToPutDistinctItemsIntoDistinctBucketsWithMod(3, 2, true)   -> 8   2^3
// @endif

// @if formulaIdentical formulaDistinct
struct StirlingByFormula {
    ll mod;
    vector<ll> fact{1}, invFact{1};

    // O(1) -- mod must be prime
    explicit StirlingByFormula(ll mod = 1000000007) : mod(mod) {}

    ll power(ll base, ll exponent) const {
        ll result = 1 % mod;
        base %= mod;
        for (; exponent > 0; exponent >>= 1, base = base * base % mod)
            if (exponent & 1) result = result * base % mod;
        return result;
    }

    void grow(ll x) {
        // factorial tables cover 0..x afterwards (doubling)
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

    ll onto(ll items, ll buckets) {
        // distinct items into distinct buckets, none empty: inclusion-exclusion over the buckets left empty
        grow(buckets);
        ll total = 0;
        for (ll empty = 0; empty <= buckets; empty++) {
            ll choose = fact[buckets] * invFact[empty] % mod * invFact[buckets - empty] % mod;
            ll term = choose * power(buckets - empty, items) % mod;
            total = (empty % 2 ? total - term + mod : total + term) % mod;
        }
        return total;
    }

    // @if formulaIdentical
    // O(buckets * log items) per call -- distinct items into identical buckets; allowEmptyBuckets (required, no
    // default): may a bucket stay empty; needs buckets < mod
    ll waysToPutDistinctItemsIntoIdenticalBucketsWithMod(ll items, ll buckets, bool allowEmptyBuckets) {
        if (!allowEmptyBuckets) return onto(items, buckets) * invFact[buckets] % mod;
        // sum over how many buckets get used: sum of i^items / i! * (alternating sum of 1/t! for t <= buckets - i)
        grow(buckets);
        vector<ll> alt(buckets + 1);
        ll running = 0;
        for (ll t = 0; t <= buckets; t++) alt[t] = running = (running + (t % 2 ? mod - invFact[t] : invFact[t])) % mod;
        ll total = 0;
        for (ll i = 0; i <= buckets; i++) total = (total + power(i, items) * invFact[i] % mod * alt[buckets - i]) % mod;
        return total;
    }

    // @endif
    // @if formulaDistinct
    // O(buckets * log items) per call (O(log items) with allowEmptyBuckets) -- distinct items into distinct buckets;
    // allowEmptyBuckets (required, no default): may a bucket stay empty; needs buckets < mod
    ll waysToPutDistinctItemsIntoDistinctBucketsWithMod(ll items, ll buckets, bool allowEmptyBuckets) {
        return allowEmptyBuckets ? power(buckets, items) : onto(items, buckets);
    }
    // @endif
};

// @endif
// @if tableIdentical tableDistinct
struct StirlingByTable {
    ll mod;
    vector<vector<ll>> table;  // table[i][j] = ways to put i distinct items into j identical non-empty buckets
    vector<vector<ll>> prefix;  // prefix[i][j] = table[i][0] + ... + table[i][j]: up to j buckets used
    vector<ll> fact;           // fact[j] = j! % mod, the orderings of j distinct buckets

    // O(1) -- any mod
    explicit StirlingByTable(ll mod = 1000000007) : mod(mod), table{{1 % mod}}, prefix{{1 % mod}}, fact{1 % mod} {}

    void grow(int items, int buckets) {
        // afterwards the table covers items x buckets; each side at least doubles when it grows, so it's rebuilt
        // O(log) times and the total cost stays O(final items * final buckets)
        int rows = table.size(), cols = table[0].size();
        if (items < rows && buckets < cols) return;
        if (items >= rows) rows = max(items + 1, 2 * rows);
        if (buckets >= cols) cols = max(buckets + 1, 2 * cols);
        table.assign(rows, vector<ll>(cols, 0));
        table[0][0] = 1 % mod;
        for (int i = 1; i < rows; i++)
            for (int j = 1; j < cols; j++) table[i][j] = (table[i - 1][j - 1] + j * table[i - 1][j]) % mod;
        prefix = table;
        for (auto& row : prefix)
            for (int j = 1; j < cols; j++) row[j] = (row[j] + row[j - 1]) % mod;
        while ((int)fact.size() < cols) fact.push_back(fact.back() * (ll)fact.size() % mod);
    }

    // @if tableIdentical
    // O(1) once the table covers (items, buckets) -- distinct items into identical buckets; allowEmptyBuckets
    // (required, no default): may a bucket stay empty
    ll waysToPutDistinctItemsIntoIdenticalBucketsWithMod(int items, int buckets, bool allowEmptyBuckets) {
        grow(items, buckets);
        return allowEmptyBuckets ? prefix[items][buckets] : table[items][buckets];
    }

    // @endif
    // @if tableDistinct
    // O(1) once the table covers (items, buckets) (O(log items) with allowEmptyBuckets) -- distinct items into distinct
    // buckets; allowEmptyBuckets (required, no default): may a bucket stay empty
    ll waysToPutDistinctItemsIntoDistinctBucketsWithMod(int items, int buckets, bool allowEmptyBuckets) {
        if (allowEmptyBuckets) {
            ll result = 1 % mod, base = buckets % mod;
            for (int e = items; e > 0; e >>= 1, base = base * base % mod)
                if (e & 1) result = result * base % mod;
            return result;
        }
        grow(items, buckets);
        return table[items][buckets] * fact[buckets] % mod;
    }
    // @endif
};
// @endif
