// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/bitset/FixedBitset.cpp
#include <bits/stdc++.h>
using namespace std;

// FixedBitset<N>: N bits, N fixed at compile time. A thin wrapper over std::bitset<N> with clearer names.
// Bit i is index i of an array of 0s and 1s, and strings read left to right like an array:
//   "1101" -> bits 0, 1, 3 set        (std::bitset parses and prints the other way round)
// N must be a compile-time constant, so size it to the largest the problem allows (FixedBitset<100001>).
// Nothing wraps around and nothing overflows: a shift drops the bits pushed past either end and shifts in 0s.
// Whole-set ops (count, &, |, ^, shifts, ...) cost O(N/64): the bits are packed 64 to a machine word.
// Every method inlines, so this compiles to the same code as std::bitset itself; single-bit ops add one bounds
// check that throws out_of_range.
// Needs GCC or Clang with libstdc++ (LeetCode, Codeforces): the searches use its _Find_first / _Find_next.
// Needs lastSet / prevSetBefore, cheap range ops, or a size only known at runtime? Use DynamicBitset.
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
// Visit every set bit, smallest first:
//   for (int i = b.firstSet(); i != -1; i = b.nextSetAfter(i)) { ... }
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

    // O(1) -- N
    static constexpr int size() { return (int)N; }

    // ---- single bits: O(1), need 0 <= i < N, else throw out_of_range ----

    // O(1) -- bit i, true / false
    bool get(int i) const { check(i); return bits[i]; }

    // O(1) -- bit i = 1
    void set(int i) { check(i); bits[i] = 1; }

    // O(1) -- bit i = 0
    void unset(int i) { check(i); bits[i] = 0; }

    // O(1) -- bit i = 1 - bit i
    void toggle(int i) { check(i); bits.flip(i); }

    // O(1) -- bit i = on
    void assign(int i, bool on) { check(i); bits[i] = on; }

    // ---- whole set ----

    // O(N/64) -- every bit = 1
    void setAll() { bits.set(); }

    // O(N/64) -- every bit = 0
    void unsetAll() { bits.reset(); }

    // O(N/64) -- every bit flipped
    void toggleAll() { bits.flip(); }

    // O(N/64) -- how many bits are 1
    int count() const { return (int)bits.count(); }

    // O(N/64) -- some bit is 1
    bool hasAny() const { return bits.any(); }

    // O(N/64) -- every bit is 0
    bool isEmpty() const { return bits.none(); }

    // O(N/64) -- every bit is 1
    bool isFull() const { return bits.all(); }

    // ---- ranges [l, r] inclusive: O(N/64) each (whole-set masks, not just the range); need 0 <= l <= r < N, else
    // throw out_of_range ----

    // O(N/64) -- bits l..r = 1
    void rangeSet(int l, int r) { checkRange(l, r); bits |= rangeMask(l, r); }

    // O(N/64) -- bits l..r = 0
    void rangeUnset(int l, int r) { checkRange(l, r); bits &= ~rangeMask(l, r); }

    // O(N/64) -- bits l..r flipped
    void rangeToggle(int l, int r) { checkRange(l, r); bits ^= rangeMask(l, r); }

    // O(N/64) -- how many of bits l..r are 1
    int countRange(int l, int r) const { checkRange(l, r); return (int)((bits >> l) << (N - 1 - (r - l))).count(); }

    // ---- searches: an index, or -1 when there is none ----

    // O(N/64) -- the smallest i with bit i = 1, or -1
    int firstSet() const { size_t i = bits._Find_first(); return i < N ? (int)i : -1; }

    // O(N/64) -- the smallest j > i with bit j = 1, or -1; needs -1 <= i < N, else throws out_of_range
    // (nextSetAfter(-1) is firstSet())
    int nextSetAfter(int i) const {
        if (i < -1 || i >= (int)N) {
            throwOutOfRange(i);
        }
        if (i == -1) {
            return firstSet();
        }
        size_t j = bits._Find_next(i);
        return j < N ? (int)j : -1;
    }

    // O(N/64) -- the smallest i with bit i = 0, or -1 (the mex of the set)
    int firstUnset() const { size_t i = (~bits)._Find_first(); return i < N ? (int)i : -1; }

    // O(N/64) -- the smallest j > i with bit j = 0, or -1; needs -1 <= i < N, else throws out_of_range
    int nextUnsetAfter(int i) const {
        if (i < -1 || i >= (int)N) {
            throwOutOfRange(i);
        }
        bitset<N> flipped = ~bits;
        size_t j = i == -1 ? flipped._Find_first() : flipped._Find_next(i);
        return j < N ? (int)j : -1;
    }

    // O(N/64 + count) -- f(i) for every i with bit i = 1, smallest first
    template <typename F>
    void forEachSet(F f) const {
        for (size_t i = bits._Find_first(); i < N; i = bits._Find_next(i)) {
            f((int)i);
        }
    }

    // ---- two sets ----

    // O(N/64) -- every 1 in this is also a 1 in other
    bool isSubsetOf(const FixedBitset& other) const { return (bits & ~other.bits).none(); }

    // O(N/64) -- some bit is 1 in both
    bool intersects(const FixedBitset& other) const { return (bits & other.bits).any(); }

    // O(N/64) each -- bit by bit: & and, | or, ^ xor, ~ not
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

    // O(N/64) -- the bits as a number, bit i -> bit i; throws overflow_error if any bit at 64 or above is 1
    unsigned long long toMask() const { return bits.to_ullong(); }

    // ---- internals ----
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
    static void checkShift(int k) {
        if (k < 0) {
            throw invalid_argument("FixedBitset: shift by " + to_string(k) + ", which is negative");
        }
    }
};
