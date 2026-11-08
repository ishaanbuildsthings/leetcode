// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/bitset/FixedBitset.cpp
#include <bits/stdc++.h>
using namespace std;

// FixedBitset<N>: N bits, N fixed at compile time. A thin wrapper over std::bitset<N> with clearer names.
// Bit i is index i of an array of 0s and 1s, and strings read left to right like an array:
//   "1101" -> bits 0, 1, 3 set        (std::bitset parses and prints the other way round)
// N must be a compile-time constant, so size it to the largest the problem allows (FixedBitset<100001>).
// Nothing wraps around and nothing overflows: a shift drops the bits pushed past either end and shifts in 0s.
// Whole-set ops (countOnes, &, |, ^, shifts, ...) cost O(N/64): the bits are packed 64 to a machine word.
// Every method inlines, so this compiles to the same code as std::bitset itself; single-bit ops add one bounds
// check that throws out_of_range.
// Needs GCC or Clang with libstdc++ (LeetCode, Codeforces): the searches use its _Find_first / _Find_next.
// Needs cheap range ops or a size only known at runtime? Use DynamicBitset.
//
// FixedBitset<8> a;                   // 00000000
// FixedBitset<8> b("1101");           // 11010000   (bits 0, 1, 3)
// FixedBitset<64> c(0b1011ULL);       // bits 0, 1, 3   (bit i of the mask -> bit i)
//
// Subset sum, sums up to 100000:
//   FixedBitset<100001> reach("1");   // only sum 0 is reachable
//   for (int w : weights) reach.orWithShiftedUp(w);   // reach |= reach << w
//   reach.get(target)
//
// Visit every set bit, smallest first / largest first:
//   for (int i = b.minIndexOfOne(); i != -1; i = b.nextOneAfter(i)) { ... }
//   for (int i = b.maxIndexOfOne(); i != -1; i = b.prevOneBefore(i)) { ... }
template <size_t N>
struct FixedBitset {
    bitset<N> bits;

    // O(1) -- all N bits 0
    FixedBitset() {}

    // O(N) -- s[i] is bit i, bits from s.size() up are 0; needs s.size() <= N and only '0' / '1', else throws
    // invalid_argument
    explicit FixedBitset(const string& s) {
        if (s.size() > N) {
            throw invalid_argument("FixedBitset: string of length " + to_string(s.size()) + " is longer than N = " + to_string(N));
        }
        for (size_t i = 0; i < s.size(); i++) {
            if (s[i] == '1') {
                bits[i] = 1;
            } else if (s[i] != '0') {
                throw invalid_argument("FixedBitset: string has a character other than '0' / '1' at index " + to_string(i));
            }
        }
    }

    // O(N/64) -- bit i is bit i of mask (bits 64 and up are 0)
    explicit FixedBitset(unsigned long long mask) : bits(mask) {}

    // O(1) -- how many bits there are in total (N), not how many are 1
    static constexpr int numBits() { return (int)N; }

    // ---- single bits: O(1), need 0 <= i < N, else throw out_of_range ----

    // O(1) -- bit i: 0 or 1
    int get(int i) const { check(i); return bits[i] ? 1 : 0; }

    // O(1) -- bit i = 1
    void set(int i) { check(i); bits[i] = 1; }

    // O(1) -- bit i = 0
    void unset(int i) { check(i); bits[i] = 0; }

    // O(1) -- bit i = 1 - bit i
    void toggle(int i) { check(i); bits.flip(i); }

    // O(1) -- bit i = zeroOrOne; zeroOrOne must be 0 or 1, else throws invalid_argument
    void setBit(int i, int zeroOrOne) { check(i); checkBit(zeroOrOne); bits[i] = zeroOrOne; }

    // ---- whole set ----

    // O(N/64) -- every bit = 1
    void setAll() { bits.set(); }

    // O(N/64) -- every bit = 0
    void unsetAll() { bits.reset(); }

    // O(N/64) -- every bit flipped
    void toggleAll() { bits.flip(); }

    // O(N/64) -- how many bits are 1
    int countOnes() const { return (int)bits.count(); }

    // O(N/64) -- every bit is 0
    bool allZeros() const { return bits.none(); }

    // O(N/64) -- every bit is 1
    bool allOnes() const { return bits.all(); }

    // ---- ranges [l, r] inclusive: O(N/64) each (whole-set masks, not just the range); need 0 <= l <= r < N, else
    // throw out_of_range ----

    // O(N/64) -- bits l..r = 1
    void rangeSet(int l, int r) { checkRange(l, r); bits |= rangeMask(l, r); }

    // O(N/64) -- bits l..r = 0
    void rangeUnset(int l, int r) { checkRange(l, r); bits &= ~rangeMask(l, r); }

    // O(N/64) -- bits l..r flipped
    void rangeToggle(int l, int r) { checkRange(l, r); bits ^= rangeMask(l, r); }

    // O(N/64) -- how many of bits l..r are 1
    int countOnesInRange(int l, int r) const { checkRange(l, r); return (int)((bits >> l) << (N - 1 - (r - l))).count(); }

    // O(N/64) -- how many of bits l..r are 0
    int countZerosInRange(int l, int r) const { return (r - l + 1) - countOnesInRange(l, r); }

    // ---- searches: an index, or -1 when there is none ----

    // O(N/64) -- the smallest bit index holding a 1, or -1 if every bit is 0
    int minIndexOfOne() const { size_t i = bits._Find_first(); return i < N ? (int)i : -1; }

    // O(N/64) -- the smallest bit index above i holding a 1, or -1; needs -1 <= i < N, else throws out_of_range
    // (nextOneAfter(-1) is minIndexOfOne())
    int nextOneAfter(int i) const {
        if (i < -1 || i >= (int)N) {
            throwOutOfRange(i);
        }
        if (i == -1) {
            return minIndexOfOne();
        }
        size_t j = bits._Find_next(i);
        return j < N ? (int)j : -1;
    }

    // O(N/64) -- the smallest bit index holding a 0, or -1 if every bit is 1
    int minIndexOfZero() const { size_t i = (~bits)._Find_first(); return i < N ? (int)i : -1; }

    // O(N/64) -- the smallest bit index above i holding a 0, or -1; needs -1 <= i < N, else throws out_of_range
    int nextZeroAfter(int i) const {
        if (i < -1 || i >= (int)N) {
            throwOutOfRange(i);
        }
        bitset<N> flipped = ~bits;
        size_t j = i == -1 ? flipped._Find_first() : flipped._Find_next(i);
        return j < N ? (int)j : -1;
    }

    // O(N/64) -- the largest bit index holding a 1, or -1 if every bit is 0
    int maxIndexOfOne() const { return prevBefore((int)N, true); }

    // O(N/64) -- the largest bit index below i holding a 1, or -1; needs 0 <= i <= N, else throws out_of_range
    // (prevOneBefore(N) is maxIndexOfOne())
    int prevOneBefore(int i) const {
        if (i < 0 || i > (int)N) {
            throwOutOfRange(i);
        }
        return prevBefore(i, true);
    }

    // O(N/64) -- the largest bit index holding a 0, or -1 if every bit is 1
    int maxIndexOfZero() const { return prevBefore((int)N, false); }

    // O(N/64) -- the largest bit index below i holding a 0, or -1; needs 0 <= i <= N, else throws out_of_range
    int prevZeroBefore(int i) const {
        if (i < 0 || i > (int)N) {
            throwOutOfRange(i);
        }
        return prevBefore(i, false);
    }

    // O(N/64 + number of 1s) -- calls f(i) for every bit index i holding a 1, smallest bit index first
    template <typename F>
    void forEachOne(F f) const {
        for (size_t i = bits._Find_first(); i < N; i = bits._Find_next(i)) {
            f((int)i);
        }
    }

    // ---- two sets ----

    // O(N/64) -- every 1 in this is also a 1 in other
    bool isSubsetOf(const FixedBitset& other) const { return (bits & ~other.bits).none(); }

    // O(N/64) -- some bit is 1 in both
    bool intersects(const FixedBitset& other) const { return (bits & other.bits).any(); }

    // O(N/64) each -- a & b, a | b, a ^ b, ~a return a NEW bitset (same N), bit i = a[i] AND / OR / XOR b[i], or NOT a[i];
    // a &= b, a |= b, a ^= b change a in place
    FixedBitset operator&(const FixedBitset& o) const { return make(bits & o.bits); }
    FixedBitset operator|(const FixedBitset& o) const { return make(bits | o.bits); }
    FixedBitset operator^(const FixedBitset& o) const { return make(bits ^ o.bits); }
    FixedBitset operator~() const { return make(~bits); }
    FixedBitset& operator&=(const FixedBitset& o) { bits &= o.bits; return *this; }
    FixedBitset& operator|=(const FixedBitset& o) { bits |= o.bits; return *this; }
    FixedBitset& operator^=(const FixedBitset& o) { bits ^= o.bits; return *this; }
    bool operator==(const FixedBitset& o) const { return bits == o.bits; }
    bool operator!=(const FixedBitset& o) const { return bits != o.bits; }

    // ---- shifts: O(N/64), need k >= 0, else throw invalid_argument; k >= N gives all 0 ----

    // O(N/64) -- b << k: bit i moves to i + k (toward the end); bits past N - 1 drop off, bits 0..k-1 become 0
    FixedBitset operator<<(int k) const { checkShift(k); return make(bits << k); }
    FixedBitset& operator<<=(int k) { checkShift(k); bits <<= k; return *this; }

    // O(N/64) -- b >> k: bit i moves to i - k (toward the start); bits below 0 drop off, the top k become 0
    FixedBitset operator>>(int k) const { checkShift(k); return make(bits >> k); }
    FixedBitset& operator>>=(int k) { checkShift(k); bits >>= k; return *this; }

    // O(N/64) -- this |= this << k, the subset-sum / knapsack step
    void orWithShiftedUp(int k) { checkShift(k); bits |= bits << k; }

    // ---- conversions ----

    // O(N) -- s[i] is bit i, length N (array order, not std::bitset's)
    string toString() const {
        string s(N, '0');
        for (size_t i = 0; i < N; i++) {
            if (bits[i]) {
                s[i] = '1';
            }
        }
        return s;
    }

    // O(N/64) -- the bits as one number, bit i -> bit i, so bits 0, 1, 3 -> 11; only works when every 1 is at index 0..63,
    // else throws overflow_error (a number only has 64 bits)
    unsigned long long toNumber() const { return bits.to_ullong(); }

    // ---- internals ----
    // std::bitset has no backward search, so this reads its words directly: libstdc++ (and libc++) store a bitset as
    // just an array of unsigned long, bit i in bit (i % width) of word i / width
    using RawWord = unsigned long;
    static constexpr int RAW_BITS = sizeof(RawWord) * 8;
    int prevBefore(int i, bool wantOne) const {
        int j = i - 1;
        if (j < 0) {
            return -1;
        }
        const RawWord* raw = reinterpret_cast<const RawWord*>(&bits);
        int wi = j / RAW_BITS;
        RawWord w = (wantOne ? raw[wi] : ~raw[wi]) & (~RawWord(0) >> (RAW_BITS - 1 - j % RAW_BITS));
        while (!w) {
            if (--wi < 0) {
                return -1;
            }
            w = wantOne ? raw[wi] : ~raw[wi];
        }
        return wi * RAW_BITS + RAW_BITS - 1 - __builtin_clzl(w);
    }
    static FixedBitset make(const bitset<N>& b) { FixedBitset res; res.bits = b; return res; }
    static bitset<N> rangeMask(int l, int r) { return (~bitset<N>() >> (N - 1 - (r - l))) << l; }
    [[noreturn]] static void throwOutOfRange(int i) {
        throw out_of_range("FixedBitset: index " + to_string(i) + " is outside [0, " + to_string(N) + ")");
    }
    static void check(int i) {
        if ((unsigned)i >= N) {
            throwOutOfRange(i);
        }
    }
    static void checkRange(int l, int r) {
        if (l < 0 || r >= (int)N || l > r) {
            throw out_of_range("FixedBitset: range [" + to_string(l) + ", " + to_string(r) + "] is not inside [0, " + to_string(N) + ")");
        }
    }
    static void checkBit(int zeroOrOne) {
        if (zeroOrOne != 0 && zeroOrOne != 1) {
            throw invalid_argument("FixedBitset: bit value " + to_string(zeroOrOne) + " is not 0 or 1");
        }
    }
    static void checkShift(int k) {
        if (k < 0) {
            throw invalid_argument("FixedBitset: shift by " + to_string(k) + ", which is negative");
        }
    }
};
