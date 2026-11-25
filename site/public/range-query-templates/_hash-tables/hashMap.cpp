// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/hash-tables/hashMap.cpp
#include <bits/stdc++.h>
#include <ext/pb_ds/assoc_container.hpp>
using namespace std;
using namespace __gnu_pbds;
using ll = long long;

// Hash for the keys: splitmix64 with a random seed picked when the program starts, so anti-hash tests can't force
// collisions. Integers cost one splitmix64; pairs two; strings one per 8 characters.
struct FastHash {
    static uint64_t splitmix64(uint64_t x) {
        x += 0x9e3779b97f4a7c15ULL;
        x = (x ^ (x >> 30)) * 0xbf58476d1ce4e5b9ULL;
        x = (x ^ (x >> 27)) * 0x94d049bb133111ebULL;
        return x ^ (x >> 31);
    }
    static uint64_t seed() {
        static const uint64_t s = splitmix64(chrono::steady_clock::now().time_since_epoch().count());
        return s;
    }
    template <class T, enable_if_t<is_integral_v<T>, int> = 0>
    size_t operator()(T x) const { return splitmix64((uint64_t)x + seed()); }
    template <class A, class B>
    size_t operator()(const pair<A, B>& p) const { return splitmix64((*this)(p.first) ^ (uint64_t)p.second); }
    size_t operator()(const string& s) const {
        uint64_t h = seed() ^ s.size();
        size_t i = 0;
        for (; i + 8 <= s.size(); i += 8) {
            uint64_t chunk;
            memcpy(&chunk, s.data() + i, 8);
            h = splitmix64(h ^ chunk);
        }
        uint64_t tail = 0;
        memcpy(&tail, s.data() + i, s.size() - i);
        return splitmix64(h ^ tail);
    }
};

// hash_map<K, V>: an unordered map, a pb_ds gp_hash_table (open addressing), much faster than std::unordered_map and
// unhackable thanks to FastHash. Every operation below is O(1) expected.
template <class K, class V> using hash_map = gp_hash_table<K, V, FastHash>;

// ============================================================================ KEY AND VALUE TYPES
// Keys work out of the box for:
//   any integer type      hash_map<int, ...>, hash_map<ll, ...>, hash_map<char, ...>, hash_map<uint64_t, ...>, ...
//   a pair of integers    hash_map<pair<int, int>, ...>, hash_map<pair<ll, ll>, ...>, ...
//   string                hash_map<string, ...>
// Anything else as a key (tuple, vector, double, a struct) needs its own operator() added to FastHash.
// Values can be any type: hash_map<int, int>, hash_map<string, vector<int>>, hash_map<ll, pair<int, int>>,
// hash_map<int, hash_map<int, int>> (a map of maps works), ...
//
// ============================================================================ MAKING ONE
//   hash_map<int, int> cnt;                                    // empty
//   hash_map<int, int> cnt;  for (int x : arr) cnt[x]++;       // count occurrences
//   hash_map<string, vector<int>> positions;                   // values can be containers
//   hash_map<pair<int, int>, ll> best;                         // pair keys
//
// ============================================================================ ADDING, CHANGING, REMOVING
//   cnt[7] = 3;                         // set the value for 7 (adds 7 if it's new)
//   cnt[7]++;                           // a missing key starts at 0 (int, ll), "" (string), {} (vector), ...
//   positions["abc"].push_back(i);      // same: a missing key starts as an empty vector
//   best[{r, c}] = 10;                  // pair keys: braces build the pair
//   cnt.insert({7, 3});                 // add 7 -> 3 only if 7 isn't there yet (never overwrites)
//   cnt.erase(7);                       // remove key 7 (nothing happens if it isn't there)
//   bool removed = cnt.erase(7);        // true if 7 was there and got removed
//   cnt.clear();                        // remove everything
//
// ============================================================================ IS A KEY IN THE MAP?
// There is NO .count() and NO .contains() on gp_hash_table: always compare find() against end().
// Careful: reading cnt[k] to check ADDS k (with value 0). Use find when you only want to look.
//   if (cnt.find(7) != cnt.end()) { ... }        // 7 IS a key
//   if (cnt.find(7) == cnt.end()) { ... }        // 7 is NOT a key
//   bool has = cnt.find(7) != cnt.end();
//
// ============================================================================ READING A VALUE
//   int v = cnt[7];                     // the value, or adds 7 with value 0 first if it's missing
//   auto it = cnt.find(7);              // look without adding:
//   if (it != cnt.end()) { int v = it->second; }        // 7 IS a key: it->first is 7, it->second its value
//   else { }                                            // 7 is NOT a key (it == cnt.end()): nothing added
//   int v = it != cnt.end() ? it->second : -1;          // with a default when missing
//
// ============================================================================ SIZE
//   int n = cnt.size();                 // how many keys
//   if (cnt.empty()) { ... }            // no keys at all
//
// ============================================================================ LOOPING
// The order is arbitrary (it's a hash table) and can change after an insert. Don't insert or erase while looping.
//   for (auto& [key, value] : cnt) { ... }               // keys and values
//   for (auto& [key, value] : cnt) { value *= 2; }       // change values in place (the & matters)
//   for (auto& [key, _] : cnt) { ... }                   // just keys
//   for (auto& [_, value] : cnt) { ... }                 // just values
//   for (auto& [rc, value] : best) { auto [r, c] = rc; } // pair keys, unpacked
//   for (auto& kv : cnt) { kv.first; kv.second; }        // the same without structured bindings
//   vector<int> keys;  for (auto& [key, _] : cnt) keys.push_back(key);   // copy the keys out (sort if needed)
//   // to erase while scanning: collect the keys into a vector first, then erase each one afterwards
//
// ============================================================================ GOTCHAS
//   - .count(), .contains(), .at(), .reserve(), .bucket_count() don't exist (see above for find != end).
//   - cnt[k] on a missing key adds it, so checking with cnt[k] grows the map (and size()). Use find to look.
//   - The order is not insertion order and not sorted.
//   - It uses more memory than unordered_map; for small int keys in [0, n), a plain vector is faster still.
