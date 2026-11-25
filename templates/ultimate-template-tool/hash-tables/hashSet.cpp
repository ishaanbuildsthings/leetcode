// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/hash-tables/hashSet.cpp
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

// hash_set<K>: an unordered set, a pb_ds gp_hash_table (open addressing), much faster than std::unordered_set and
// unhackable thanks to FastHash. Every operation below is O(1) expected.
template <class K> using hash_set = gp_hash_table<K, null_type, FastHash>;

// ============================================================================ KEY TYPES
// Works out of the box for:
//   any integer type      hash_set<int>, hash_set<ll>, hash_set<unsigned>, hash_set<char>, hash_set<uint64_t>, ...
//   a pair of integers    hash_set<pair<int, int>>, hash_set<pair<ll, ll>>, hash_set<pair<int, ll>>, ...
//   string                hash_set<string>
// Anything else (tuple, vector, double, a struct) needs its own operator() added to FastHash. A tuple of 3 ints is
// usually easier as a pair<ll, int> or by packing it into one ll.
//
// ============================================================================ MAKING ONE
//   hash_set<int> seen;                                        // empty
//   hash_set<int> seen;  for (int x : arr) seen.insert(x);     // from an array (no range constructor)
//   hash_set<pair<int, int>> visited;                          // e.g. grid cells
//   hash_set<string> words;
//
// ============================================================================ ADDING AND REMOVING
//   seen.insert(5);                    // add 5 (nothing happens if it's already there)
//   bool added = seen.insert(5).second;    // true if 5 was new, false if it was already there
//   visited.insert({r, c});            // pairs: braces build the pair
//   seen.erase(5);                     // remove 5 (nothing happens if it isn't there)
//   bool removed = seen.erase(5);      // true if 5 was there and got removed
//   seen.clear();                      // remove everything
//
// ============================================================================ IS IT IN THE SET?
// There is NO .count() and NO .contains() on gp_hash_table: always compare find() against end().
//   if (seen.find(5) != seen.end()) { ... }       // 5 IS in the set
//   if (seen.find(5) == seen.end()) { ... }       // 5 is NOT in the set
//   bool has = seen.find(5) != seen.end();
//   if (visited.find({r, c}) == visited.end()) { visited.insert({r, c}); }
//
// ============================================================================ SIZE
//   int n = seen.size();               // how many keys
//   if (seen.empty()) { ... }          // no keys at all
//
// ============================================================================ LOOPING
// The order is arbitrary (it's a hash table) and can change after an insert. Don't insert or erase while looping.
//   for (int x : seen) { ... }                         // every key
//   for (auto [r, c] : visited) { ... }                // pair keys, unpacked
//   for (const string& w : words) { ... }              // strings by reference (no copy)
//   vector<int> keys(seen.begin(), seen.end());        // copy the keys out (sort them if you need an order)
//   // to erase while scanning: collect into a vector first, then erase each one afterwards
//
// ============================================================================ GOTCHAS
//   - .count(), .contains(), .reserve(), .bucket_count() don't exist (see above for find != end).
//   - The order is not insertion order and not sorted.
//   - It uses more memory than unordered_set; for a set of small ints in [0, n), a vector<char> is faster still.
