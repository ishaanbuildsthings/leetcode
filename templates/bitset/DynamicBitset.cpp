// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/bitset/DynamicBitset.cpp
#include <bits/stdc++.h>
using namespace std;

// DynamicBitset: n bits, n chosen at runtime and able to grow and shrink (append / pop / resize). Built on its own
// array of 64-bit words, so unlike std::bitset it also gives lastSet / prevSetBefore and range ops that only touch
// the words in the range.
// Bit i is index i of an array of 0s and 1s, and strings read left to right like an array:
//   "1101" -> bits 0, 1, 3 set
// Nothing wraps around and nothing overflows: a shift drops the bits pushed past either end and shifts in 0s.
// Whole-set ops (count, &, |, ^, shifts, ...) cost O(n/64): the bits are packed 64 to a machine word.
// Invalid calls (an index outside [0, n), sets of different sizes, a negative shift) throw with a message.
//
// DynamicBitset a(8);                 // 00000000
// DynamicBitset b("1101");            // 1101   (n = 4: bits 0, 1, 3)
// DynamicBitset c(n, true);           // n bits, all 1
//
// Subset sum, sums up to total:
//   DynamicBitset reach(total + 1);
//   reach.set(0);
//   for (int w : weights) reach.orWithShiftedUp(w);   // reach |= reach << w, in place, no temporary
//   reach.get(target)
//
// Visit every set bit, smallest first / largest first:
//   for (int i = b.firstSet(); i != -1; i = b.nextSetAfter(i)) { ... }
//   for (int i = b.lastSet(); i != -1; i = b.prevSetBefore(i)) { ... }
struct DynamicBitset {
    using Word = unsigned long long;
    int n = 0;
    vector<Word> words;   // bit i is bit (i % 64) of words[i / 64]; bits at n and above are always 0

    // O(n/64) -- n bits, all equal to fill; needs n >= 0, else throws invalid_argument
    explicit DynamicBitset(int n = 0, bool fill = false) : n(n) {
        if (n < 0) {
            throw invalid_argument("DynamicBitset: size " + to_string(n) + " is negative");
        }
        words.assign((n + 63) >> 6, fill ? ~0ULL : 0ULL);
        trim();
    }

    // O(n) -- n = s.size(), s[i] is bit i; needs only '0' / '1', else throws invalid_argument
    explicit DynamicBitset(const string& s) : DynamicBitset((int)s.size()) {
        for (int i = 0; i < n; i++) {
            if (s[i] == '1') {
                words[i >> 6] |= 1ULL << (i & 63);
            } else if (s[i] != '0') {
                throw invalid_argument("DynamicBitset: string has a character other than '0' / '1' at index " + to_string(i));
            }
        }
    }

    // O(1) -- n
    int size() const { return n; }

    // ---- single bits: O(1), need 0 <= i < n, else throw out_of_range ----

    // O(1) -- bit i, true / false
    bool get(int i) const { check(i); return words[i >> 6] >> (i & 63) & 1; }

    // O(1) -- bit i = 1
    void set(int i) { check(i); words[i >> 6] |= 1ULL << (i & 63); }

    // O(1) -- bit i = 0
    void unset(int i) { check(i); words[i >> 6] &= ~(1ULL << (i & 63)); }

    // O(1) -- bit i = 1 - bit i
    void toggle(int i) { check(i); words[i >> 6] ^= 1ULL << (i & 63); }

    // O(1) -- bit i = on
    void assign(int i, bool on) { on ? set(i) : unset(i); }

    // ---- growing and shrinking ----

    // O(1) amortized -- adds a bit = on at the end (it becomes bit n, then n grows by 1)
    void append(bool on) {
        if ((n & 63) == 0) {
            words.push_back(0);
        }
        n++;
        assign(n - 1, on);
    }

    // O(1) -- removes the last bit (bit n - 1) and returns it; needs n >= 1, else throws out_of_range
    bool pop() {
        if (n == 0) {
            throw out_of_range("DynamicBitset: pop on an empty bitset");
        }
        bool last = get(n - 1);
        n--;
        words.resize((n + 63) >> 6);
        trim();
        return last;
    }

    // O(max(old n, newN)/64) -- keeps bits 0..min(n, newN)-1; new bits are 0; needs newN >= 0, else throws
    // invalid_argument
    void resize(int newN) {
        if (newN < 0) {
            throw invalid_argument("DynamicBitset: size " + to_string(newN) + " is negative");
        }
        n = newN;
        words.resize((n + 63) >> 6, 0);
        trim();
    }

    // ---- whole set ----

    // O(n/64) -- every bit = 1
    void setAll() { fill(words.begin(), words.end(), ~0ULL); trim(); }

    // O(n/64) -- every bit = 0
    void unsetAll() { fill(words.begin(), words.end(), 0ULL); }

    // O(n/64) -- every bit flipped
    void toggleAll() {
        for (Word& w : words) {
            w = ~w;
        }
        trim();
    }

    // O(n/64) -- how many bits are 1
    int count() const {
        int total = 0;
        for (Word w : words) {
            total += __builtin_popcountll(w);
        }
        return total;
    }

    // O(n/64) -- some bit is 1
    bool hasAny() const {
        for (Word w : words) {
            if (w) {
                return true;
            }
        }
        return false;
    }

    // O(n/64) -- every bit is 0 (true when n = 0)
    bool isEmpty() const { return !hasAny(); }

    // O(n/64) -- every bit is 1 (true when n = 0)
    bool isFull() const { return count() == n; }

    // ---- ranges [l, r] inclusive: O((r - l)/64 + 1) each; need 0 <= l <= r < n, else throw out_of_range ----

    // O((r - l)/64 + 1) -- bits l..r = 1
    void rangeSet(int l, int r) { checkRange(l, r); forRangeWords(l, r, [](Word& w, Word m) { w |= m; }); }

    // O((r - l)/64 + 1) -- bits l..r = 0
    void rangeUnset(int l, int r) { checkRange(l, r); forRangeWords(l, r, [](Word& w, Word m) { w &= ~m; }); }

    // O((r - l)/64 + 1) -- bits l..r flipped
    void rangeToggle(int l, int r) { checkRange(l, r); forRangeWords(l, r, [](Word& w, Word m) { w ^= m; }); }

    // O((r - l)/64 + 1) -- how many of bits l..r are 1
    int countRange(int l, int r) const {
        checkRange(l, r);
        int lw = l >> 6, rw = r >> 6;
        Word lowMask = ~0ULL << (l & 63), highMask = ~0ULL >> (63 - (r & 63));
        if (lw == rw) {
            return __builtin_popcountll(words[lw] & lowMask & highMask);
        }
        int total = __builtin_popcountll(words[lw] & lowMask) + __builtin_popcountll(words[rw] & highMask);
        for (int i = lw + 1; i < rw; i++) {
            total += __builtin_popcountll(words[i]);
        }
        return total;
    }

    // ---- searches: an index, or -1 when there is none; each costs O(distance to the answer / 64 + 1), O(n/64) at
    // worst ----

    // the smallest i with bit i = 1, or -1
    int firstSet() const { return nextSetAfter(-1); }

    // the largest i with bit i = 1, or -1
    int lastSet() const { return prevSetBefore(n); }

    // the smallest j > i with bit j = 1, or -1; needs -1 <= i < n, else throws out_of_range
    int nextSetAfter(int i) const {
        if (i < -1 || i >= n) {
            throwOutOfRange(i);
        }
        int j = i + 1;
        if (j >= n) {
            return -1;
        }
        int wi = j >> 6;
        Word w = words[wi] & (~0ULL << (j & 63));
        while (!w) {
            if (++wi == (int)words.size()) {
                return -1;
            }
            w = words[wi];
        }
        return (wi << 6) + __builtin_ctzll(w);
    }

    // the largest j < i with bit j = 1, or -1; needs 0 <= i <= n, else throws out_of_range
    int prevSetBefore(int i) const {
        if (i < 0 || i > n) {
            throwOutOfRange(i);
        }
        int j = i - 1;
        if (j < 0) {
            return -1;
        }
        int wi = j >> 6;
        Word w = words[wi] & (~0ULL >> (63 - (j & 63)));
        while (!w) {
            if (--wi < 0) {
                return -1;
            }
            w = words[wi];
        }
        return (wi << 6) + 63 - __builtin_clzll(w);
    }

    // the smallest i with bit i = 0, or -1 (the mex of the set)
    int firstUnset() const { return nextUnsetAfter(-1); }

    // the smallest j > i with bit j = 0, or -1; needs -1 <= i < n, else throws out_of_range
    int nextUnsetAfter(int i) const {
        if (i < -1 || i >= n) {
            throwOutOfRange(i);
        }
        int j = i + 1;
        if (j >= n) {
            return -1;
        }
        int wi = j >> 6;
        Word w = ~words[wi] & (~0ULL << (j & 63));
        while (!w) {
            if (++wi == (int)words.size()) {
                return -1;
            }
            w = ~words[wi];
        }
        int res = (wi << 6) + __builtin_ctzll(w);
        return res < n ? res : -1;
    }

    // O(n/64 + count) -- f(i) for every i with bit i = 1, smallest first
    template <typename F>
    void forEachSet(F f) const {
        for (int wi = 0; wi < (int)words.size(); wi++) {
            for (Word w = words[wi]; w; w &= w - 1) {
                f((wi << 6) + __builtin_ctzll(w));
            }
        }
    }

    // ---- two sets: both need the same n, else throw invalid_argument ----

    // O(n/64) -- every 1 in this is also a 1 in other
    bool isSubsetOf(const DynamicBitset& o) const {
        checkSameSize(o);
        for (size_t i = 0; i < words.size(); i++) {
            if (words[i] & ~o.words[i]) {
                return false;
            }
        }
        return true;
    }

    // O(n/64) -- some bit is 1 in both
    bool intersects(const DynamicBitset& o) const {
        checkSameSize(o);
        for (size_t i = 0; i < words.size(); i++) {
            if (words[i] & o.words[i]) {
                return true;
            }
        }
        return false;
    }

    // O(n/64) each -- bit by bit: & and, | or, ^ xor, ~ not. The non-= forms build a new bitset (one allocation)
    DynamicBitset& operator&=(const DynamicBitset& o) { checkSameSize(o); for (size_t i = 0; i < words.size(); i++) words[i] &= o.words[i]; return *this; }
    DynamicBitset& operator|=(const DynamicBitset& o) { checkSameSize(o); for (size_t i = 0; i < words.size(); i++) words[i] |= o.words[i]; return *this; }
    DynamicBitset& operator^=(const DynamicBitset& o) { checkSameSize(o); for (size_t i = 0; i < words.size(); i++) words[i] ^= o.words[i]; return *this; }
    DynamicBitset operator&(const DynamicBitset& o) const { DynamicBitset res = *this; res &= o; return res; }
    DynamicBitset operator|(const DynamicBitset& o) const { DynamicBitset res = *this; res |= o; return res; }
    DynamicBitset operator^(const DynamicBitset& o) const { DynamicBitset res = *this; res ^= o; return res; }
    DynamicBitset operator~() const { DynamicBitset res = *this; res.toggleAll(); return res; }
    // O(n/64) -- same n and same bits (different sizes are just unequal, no throw)
    bool operator==(const DynamicBitset& o) const { return n == o.n && words == o.words; }
    bool operator!=(const DynamicBitset& o) const { return !(*this == o); }

    // ---- shifts: O(n/64), need k >= 0, else throw invalid_argument; k >= n gives all 0; n stays the same ----

    // O(n/64) -- b <<= k: bit i moves to i + k (toward the end); bits past n - 1 drop off, bits 0..k-1 become 0
    DynamicBitset& operator<<=(int k) {
        checkShift(k);
        if (k >= n) {
            unsetAll();
            return *this;
        }
        int ws = k >> 6, bs = k & 63, wc = words.size();
        if (bs == 0) {
            for (int i = wc - 1; i >= ws; i--) {
                words[i] = words[i - ws];
            }
        } else {
            for (int i = wc - 1; i > ws; i--) {
                words[i] = (words[i - ws] << bs) | (words[i - ws - 1] >> (64 - bs));
            }
            words[ws] = words[0] << bs;
        }
        fill(words.begin(), words.begin() + ws, 0ULL);
        trim();
        return *this;
    }

    // O(n/64) -- b >>= k: bit i moves to i - k (toward the start); bits below 0 drop off, the top k become 0
    DynamicBitset& operator>>=(int k) {
        checkShift(k);
        if (k >= n) {
            unsetAll();
            return *this;
        }
        int ws = k >> 6, bs = k & 63, wc = words.size();
        if (bs == 0) {
            for (int i = 0; i + ws < wc; i++) {
                words[i] = words[i + ws];
            }
        } else {
            for (int i = 0; i + ws + 1 < wc; i++) {
                words[i] = (words[i + ws] >> bs) | (words[i + ws + 1] << (64 - bs));
            }
            words[wc - ws - 1] = words[wc - 1] >> bs;
        }
        fill(words.end() - ws, words.end(), 0ULL);
        return *this;
    }

    // O(n/64) -- copies, see <<= and >>=
    DynamicBitset operator<<(int k) const { DynamicBitset res = *this; res <<= k; return res; }
    DynamicBitset operator>>(int k) const { DynamicBitset res = *this; res >>= k; return res; }

    // O(n/64) -- this |= this << k in place, with no temporary: the subset-sum / knapsack step
    void orWithShiftedUp(int k) {
        checkShift(k);
        if (k >= n) {
            return;
        }
        int ws = k >> 6, bs = k & 63, wc = words.size();
        // top word down, so each word reads lower words that have not been changed yet
        if (bs == 0) {
            for (int i = wc - 1; i >= ws; i--) {
                words[i] |= words[i - ws];
            }
        } else {
            for (int i = wc - 1; i > ws; i--) {
                words[i] |= (words[i - ws] << bs) | (words[i - ws - 1] >> (64 - bs));
            }
            words[ws] |= words[0] << bs;
        }
        trim();
    }

    // ---- conversions ----

    // O(n) -- s[i] is bit i, length n
    string toString() const {
        string s(n, '0');
        forEachSet([&](int i) { s[i] = '1'; });
        return s;
    }

    // O(n/64) -- the bits as a number, bit i -> bit i; throws overflow_error if any bit at 64 or above is 1
    unsigned long long toMask() const {
        for (size_t i = 1; i < words.size(); i++) {
            if (words[i]) {
                throw overflow_error("DynamicBitset: toMask with a 1 at bit " + to_string(nextSetAfter(63)) + ", past bit 63");
            }
        }
        return words.empty() ? 0 : words[0];
    }

    // ---- internals ----
    void trim() {
        if ((n & 63) && !words.empty()) {
            words.back() &= (1ULL << (n & 63)) - 1;
        }
    }
    // op(word, mask) on each word that bits l..r touch, mask = the part of l..r inside that word
    template <typename Op>
    void forRangeWords(int l, int r, Op op) {
        int lw = l >> 6, rw = r >> 6;
        Word lowMask = ~0ULL << (l & 63), highMask = ~0ULL >> (63 - (r & 63));
        if (lw == rw) {
            op(words[lw], lowMask & highMask);
            return;
        }
        op(words[lw], lowMask);
        for (int i = lw + 1; i < rw; i++) {
            op(words[i], ~0ULL);
        }
        op(words[rw], highMask);
    }
    [[noreturn]] void throwOutOfRange(int i) const {
        throw out_of_range("DynamicBitset: index " + to_string(i) + " is outside [0, " + to_string(n) + ")");
    }
    void check(int i) const {
        if ((unsigned)i >= (unsigned)n) {
            throwOutOfRange(i);
        }
    }
    void checkRange(int l, int r) const {
        if (l < 0 || r >= n || l > r) {
            throw out_of_range("DynamicBitset: range [" + to_string(l) + ", " + to_string(r) + "] is not inside [0, " + to_string(n) + ")");
        }
    }
    void checkSameSize(const DynamicBitset& o) const {
        if (n != o.n) {
            throw invalid_argument("DynamicBitset: sizes differ (" + to_string(n) + " vs " + to_string(o.n) + ")");
        }
    }
    static void checkShift(int k) {
        if (k < 0) {
            throw invalid_argument("DynamicBitset: shift by " + to_string(k) + ", which is negative");
        }
    }
};
