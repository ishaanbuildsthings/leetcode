// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/bitset/DynamicBitset.cpp
#include <bits/stdc++.h>
using namespace std;

// DynamicBitset: n bits, n chosen at runtime and able to grow and shrink (appendBit / popBit / resize). Built on its own
// array of 64-bit words, so unlike std::bitset it also gives range ops that only touch
// the words in the range.
// Bit i is index i of an array of 0s and 1s, and strings read left to right like an array:
//   "1101" -> bits 0, 1, 3 set
// Nothing wraps around and nothing overflows: a shift drops the bits pushed past either end and shifts in 0s.
// Whole-set ops (countOnes, &, |, ^, shifts, ...) cost O(n/64): the bits are packed 64 to a machine word.
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
//   for (int i = b.minIndexOfOne(); i != -1; i = b.nextOneAfter(i)) { ... }
//   for (int i = b.maxIndexOfOne(); i != -1; i = b.prevOneBefore(i)) { ... }
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

    // O(1) -- how many bits there are in total (n), not how many are 1
    int numBits() const { return n; }

    // ---- single bits: O(1), need 0 <= i < n, else throw out_of_range ----

    // O(1) -- bit i: 0 or 1
    int get(int i) const { check(i); return words[i >> 6] >> (i & 63) & 1; }

    // O(1) -- bit i = 1
    void set(int i) { check(i); words[i >> 6] |= 1ULL << (i & 63); }

    // O(1) -- bit i = 0
    void unset(int i) { check(i); words[i >> 6] &= ~(1ULL << (i & 63)); }

    // O(1) -- bit i = 1 - bit i
    void toggle(int i) { check(i); words[i >> 6] ^= 1ULL << (i & 63); }

    // O(1) -- bit i = zeroOrOne; zeroOrOne must be 0 or 1, else throws invalid_argument
    void setBit(int i, int zeroOrOne) { checkBit(zeroOrOne); zeroOrOne ? set(i) : unset(i); }

    // ---- growing and shrinking ----

    // O(1) amortized -- adds one more bit, holding zeroOrOne, past the current highest index: it becomes index n and
    // the bitset grows to n + 1 bits; zeroOrOne must be 0 or 1, else throws invalid_argument
    void appendBit(int zeroOrOne) {
        checkBit(zeroOrOne);
        if ((n & 63) == 0) {
            words.push_back(0);
        }
        n++;
        setBit(n - 1, zeroOrOne);
    }

    // O(1) -- removes the highest-index bit (index n - 1), shrinking to n - 1 bits, and returns it (0 or 1); needs
    // n >= 1, else throws out_of_range
    int popBit() {
        if (n == 0) {
            throw out_of_range("DynamicBitset: popBit on an empty bitset");
        }
        int last = get(n - 1);
        n--;
        words.resize((n + 63) >> 6);
        trim();
        return last;
    }

    // O(max(old n, newN)/64) -- changes the number of bits to newN; needs newN >= 0, else throws invalid_argument
    //   smaller: cuts off the top bits (highest indexes): "11011" resized to 3 -> "110"
    //   bigger: makes room for more 0s at the top: "110" resized to 5 -> "11000"
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
    int countOnes() const {
        int total = 0;
        for (Word w : words) {
            total += __builtin_popcountll(w);
        }
        return total;
    }

    // O(n/64) -- every bit is 0 (true when n = 0)
    bool allZeros() const {
        for (Word w : words) {
            if (w) {
                return false;
            }
        }
        return true;
    }

    // O(n/64) -- every bit is 1 (true when n = 0)
    bool allOnes() const { return countOnes() == n; }

    // ---- ranges [l, r] inclusive: O((r - l)/64 + 1) each; need 0 <= l <= r < n, else throw out_of_range ----

    // O((r - l)/64 + 1) -- bits l..r = 1
    void rangeSet(int l, int r) { checkRange(l, r); forRangeWords(l, r, [](Word& w, Word m) { w |= m; }); }

    // O((r - l)/64 + 1) -- bits l..r = 0
    void rangeUnset(int l, int r) { checkRange(l, r); forRangeWords(l, r, [](Word& w, Word m) { w &= ~m; }); }

    // O((r - l)/64 + 1) -- bits l..r flipped
    void rangeToggle(int l, int r) { checkRange(l, r); forRangeWords(l, r, [](Word& w, Word m) { w ^= m; }); }

    // O((r - l)/64 + 1) -- how many of bits l..r are 1
    int countOnesInRange(int l, int r) const {
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

    // O((r - l)/64 + 1) -- how many of bits l..r are 0
    int countZerosInRange(int l, int r) const { return (r - l + 1) - countOnesInRange(l, r); }

    // ---- searches: an index, or -1 when there is none; each costs O(distance to the answer / 64 + 1), O(n/64) at
    // worst ----

    // the smallest bit index holding a 1, or -1 if every bit is 0
    int minIndexOfOne() const { return nextOneAfter(-1); }

    // the largest bit index holding a 1, or -1 if every bit is 0
    int maxIndexOfOne() const { return prevOneBefore(n); }

    // the smallest bit index above i holding a 1, or -1; needs -1 <= i < n, else throws out_of_range
    int nextOneAfter(int i) const {
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

    // the largest bit index below i holding a 1, or -1; needs 0 <= i <= n, else throws out_of_range
    int prevOneBefore(int i) const {
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

    // the smallest bit index holding a 0, or -1 if every bit is 1
    int minIndexOfZero() const { return nextZeroAfter(-1); }

    // the smallest bit index above i holding a 0, or -1; needs -1 <= i < n, else throws out_of_range
    int nextZeroAfter(int i) const {
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

    // the largest bit index holding a 0, or -1 if every bit is 1
    int maxIndexOfZero() const { return prevZeroBefore(n); }

    // the largest bit index below i holding a 0, or -1; needs 0 <= i <= n, else throws out_of_range
    int prevZeroBefore(int i) const {
        if (i < 0 || i > n) {
            throwOutOfRange(i);
        }
        int j = i - 1;
        if (j < 0) {
            return -1;
        }
        int wi = j >> 6;
        Word w = ~words[wi] & (~0ULL >> (63 - (j & 63)));
        while (!w) {
            if (--wi < 0) {
                return -1;
            }
            w = ~words[wi];
        }
        return (wi << 6) + 63 - __builtin_clzll(w);
    }

    // O(n/64 + number of 1s) -- calls f(i) for every bit index i holding a 1, smallest bit index first
    //   DynamicBitset b("01101");
    //   b.forEachOne([&](int i) { cout << i << ' '; });   // prints 1 2 4
    template <typename F>
    void forEachOne(F f) const {
        for (int wi = 0; wi < (int)words.size(); wi++) {
            for (Word w = words[wi]; w; w &= w - 1) {
                f((wi << 6) + __builtin_ctzll(w));
            }
        }
    }

    // ---- two bitsets, used like numbers: both need the same n, else throw invalid_argument (== just compares) ----

    // O(n/64) each -- a &= b, a |= b, a ^= b change a in place, bit i = a[i] AND / OR / XOR b[i];
    // a & b, a | b, a ^ b, ~a (NOT) return a NEW bitset of the same n (one allocation)
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

    // O(n/64) -- true if any bit is 1, like a nonzero number, so these read like int masks:
    //   if (b) / if (!b)        some bit is 1 / every bit is 0
    //   if (a & b)              a and b share a 1
    //   if ((a & b) == a)       every 1 in a is also in b
    explicit operator bool() const { return !allZeros(); }

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
        forEachOne([&](int i) { s[i] = '1'; });
        return s;
    }

    // O(n/64) -- the bits as one number, bit i -> bit i, so bits 0, 1, 3 -> 11; only works when every 1 is at index 0..63,
    // else throws overflow_error (a number only has 64 bits)
    unsigned long long toNumber() const {
        for (size_t i = 1; i < words.size(); i++) {
            if (words[i]) {
                throw overflow_error("DynamicBitset: toNumber with a 1 at bit " + to_string(nextOneAfter(63)) + ", past bit 63");
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
    static void checkBit(int zeroOrOne) {
        if (zeroOrOne != 0 && zeroOrOne != 1) {
            throw invalid_argument("DynamicBitset: bit value " + to_string(zeroOrOne) + " is not 0 or 1");
        }
    }
    static void checkShift(int k) {
        if (k < 0) {
            throw invalid_argument("DynamicBitset: shift by " + to_string(k) + ", which is negative");
        }
    }
};

#include <bits/stdc++.h>
using namespace std;
using ll = long long;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n; cin >> n;
    ll res = 0;
    vector<DynamicBitset> bitsets(n);
    for (int i = 0; i < n; i++) {
        string s; cin >> s;
        DynamicBitset bs(s);
        bitsets[i] = bs;
    }
    for (int i = 0; i < n; i++) {
        for (int j = i + 1; j < n; j++) {
            ll cnt = (bitsets[i] & bitsets[j]).countOnes();
            res += cnt * (cnt - 1) / 2;
        }
    }
    cout << res;
}