// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/sets/freq-buckets/template.cpp
#include <bits/stdc++.h>
using namespace std;
using ll = long long;

// @operations: add clear count countDistinct maxFreq minFreq remove size valuesWithMaxFreq valuesWithMinFreq
// @data-structure-type: freq-buckets
// @values: online
// @keys: numbers
// @tracks: none
// @complexities:
//   add: 1 expected
//   clear: N
//   count: 1 expected
//   countDistinct: 1
//   maxFreq: 1
//   minFreq: 1
//   remove: 1 expected
//   size: 1
//   valuesWithMaxFreq: N
//   valuesWithMinFreq: N
//   build: 1
// @memory:
//   layout: none
//   node: key[1*N] cnt[1*N] links[3*N]
//   tags: none
//   other: hash[4*N] buckets[4*N]
//   note: N = distinct values ever added; a hash table of at most 4*N ints and at most N + 1 buckets

// Multiset of integers (online: nothing known ahead). Add, remove, the highest and the lowest frequency are all O(1):
// values sit in buckets by how many copies they have, and the buckets that exist form a sorted linked list. Adding or
// removing one copy only ever moves a value to the neighbouring bucket, and the two frequencies are the ends of the
// list. T: int, long long, ...
template <typename T>
struct FreqBuckets {
    // each value has a slot, 1 and up
    vector<T> vals;
    vector<long long> cnt;  // copies per slot
    vector<int> bucketOf, prevInBucket, nextInBucket;  // the values of one bucket: a linked list, 0 ends it
    // bucket 0 joins the list's two ends: nextBucket[0] has the lowest frequency, prevBucket[0] the highest
    vector<long long> freq;
    vector<int> firstValue, prevBucket, nextBucket, freeBuckets;
    vector<int> table;  // open addressing from a value to its slot, 0 for an empty entry
    unsigned long long hashMultiplier = 1;  // random per instance, so no fixed input can force collisions
    int hashBits = 0;
    long long n = 0, d = 0;

    // O(1)
    FreqBuckets() {
        vals.assign(1, T());
        cnt.assign(1, 0), bucketOf.assign(1, 0), prevInBucket.assign(1, 0), nextInBucket.assign(1, 0);
        resetBuckets();
        unsigned long long seed = chrono::steady_clock::now().time_since_epoch().count() ^ (unsigned long long)(uintptr_t)this;
        seed = (seed ^ (seed >> 30)) * 0xBF58476D1CE4E5B9ULL;
        seed = (seed ^ (seed >> 27)) * 0x94D049BB133111EBULL;
        hashMultiplier = (seed ^ (seed >> 31)) | 1;
        resizeTable(4);
    }

    void resetBuckets() {
        freq.assign(1, 0), firstValue.assign(1, 0), prevBucket.assign(1, 0), nextBucket.assign(1, 0);
        freeBuckets.clear();
    }

    unsigned hashOf(T x) const {
        return unsigned((unsigned long long)(long long)x * hashMultiplier >> (64 - hashBits));
    }

    void resizeTable(int bits) {
        hashBits = bits;
        table.assign(1u << bits, 0);
        unsigned mask = (1u << bits) - 1;
        for (int slot = 1; slot < (int)vals.size(); slot++) {
            unsigned h = hashOf(vals[slot]);
            while (table[h]) h = (h + 1) & mask;
            table[h] = slot;
        }
    }

    int findSlot(T x) const {  // x's slot, 0 if it has none
        unsigned mask = (1u << hashBits) - 1;
        for (unsigned h = hashOf(x);; h = (h + 1) & mask) {
            int slot = table[h];
            if (!slot || vals[slot] == x) return slot;
        }
    }

    int makeSlot(T x) {  // for a value with no slot yet
        int slot = vals.size();
        vals.push_back(x);
        cnt.push_back(0), bucketOf.push_back(0), prevInBucket.push_back(0), nextInBucket.push_back(0);
        if (2 * vals.size() > table.size()) {
            resizeTable(hashBits + 1);  // (this places the new value too)
        } else {
            unsigned mask = (1u << hashBits) - 1, h = hashOf(x);
            while (table[h]) h = (h + 1) & mask;
            table[h] = slot;
        }
        return slot;
    }

    int newBucket(long long f, int left) {  // a bucket for frequency f, right after bucket left
        int b;
        if (!freeBuckets.empty()) {
            b = freeBuckets.back();
            freeBuckets.pop_back();
        } else {
            b = freq.size();
            freq.push_back(0), firstValue.push_back(0), prevBucket.push_back(0), nextBucket.push_back(0);
        }
        int right = nextBucket[left];
        freq[b] = f, firstValue[b] = 0;
        prevBucket[b] = left, nextBucket[b] = right;
        nextBucket[left] = prevBucket[right] = b;
        return b;
    }

    void join(int slot, int b) {
        int first = firstValue[b];
        bucketOf[slot] = b, prevInBucket[slot] = 0, nextInBucket[slot] = first;
        if (first) prevInBucket[first] = slot;
        firstValue[b] = slot;
    }

    void leave(int slot) {  // an emptied bucket leaves the list
        int b = bucketOf[slot], before = prevInBucket[slot], after = nextInBucket[slot];
        if (before) nextInBucket[before] = after;
        else firstValue[b] = after;
        if (after) prevInBucket[after] = before;
        if (!firstValue[b]) {
            int left = prevBucket[b], right = nextBucket[b];
            nextBucket[left] = right, prevBucket[right] = left;
            freeBuckets.push_back(b);
        }
        bucketOf[slot] = 0;
    }

    vector<T> valuesIn(int b) const {
        vector<T> res;
        for (int slot = firstValue[b]; slot; slot = nextInBucket[slot]) res.push_back(vals[slot]);
        return res;
    }

    // O(1 expected) -- add one copy of x
    void add(T x) {
        int slot = findSlot(x);
        if (!slot) slot = makeSlot(x);
        long long f = cnt[slot];
        int b = bucketOf[slot], up = nextBucket[b];
        if (freq[up] != f + 1) up = newBucket(f + 1, b);
        if (f) leave(slot);
        else d++;
        join(slot, up);
        cnt[slot] = f + 1;
        n++;
    }

    // O(1 expected) -- remove one copy of x if present; returns how many were removed (0 or 1)
    long long remove(T x) {
        int slot = findSlot(x);
        if (!slot || !cnt[slot]) return 0;
        long long f = cnt[slot];
        int down = prevBucket[bucketOf[slot]];
        if (f > 1 && freq[down] != f - 1) down = newBucket(f - 1, down);
        leave(slot);
        if (f > 1) join(slot, down);
        else d--;
        cnt[slot] = f - 1;
        n--;
        return 1;
    }

    // O(1 expected) -- how many copies of x
    long long count(T x) {
        int slot = findSlot(x);
        return slot ? cnt[slot] : 0;
    }

    // O(1) -- how many values (copies count)
    long long size() {
        return n;
    }

    // O(1) -- how many distinct values
    long long countDistinct() {
        return d;
    }

    // O(1) -- how many copies the most frequent value has; 0 if empty
    long long maxFreq() {
        return freq[prevBucket[0]];
    }

    // O(1) -- how many copies the least frequent value in the set has; 0 if empty
    long long minFreq() {
        return freq[nextBucket[0]];
    }

    // O(how many are tied) -- every value tied for the most copies, in no particular order; empty if the set is empty
    vector<T> valuesWithMaxFreq() {
        return valuesIn(prevBucket[0]);
    }

    // O(how many are tied) -- every value tied for the fewest copies, in no particular order; empty if the set is empty
    vector<T> valuesWithMinFreq() {
        return valuesIn(nextBucket[0]);
    }

    // O(N) -- remove everything: afterwards it is as if newly built, so reuse it
    void clear() {
        fill(cnt.begin(), cnt.end(), 0), fill(bucketOf.begin(), bucketOf.end(), 0);
        resetBuckets();
        n = d = 0;
    }
};
