#include <bits/stdc++.h>
using namespace std;
using ll = long long;

// This seg tree can basically add and pop from both left and right, swap chars at random positions, and get range hashes
// it works by creating a seg tree bigger than normal, giving padding on the left and right to "slide around in" and we maintain pointers
// most operations logN, some like popping are just O(1) since we literally just move a pointer, but if we add a char we actually need to point set
// If we don't want swapCharAt then we can use the two-stacks as a deque pour/fill trick and get O(1) everything WITH range hashing

// TEMPLATE BY github.com/ishaanbuildsthings PLEASE DO NOT USE

// works for all ascii strings

// hash convention: leftmost char is the highest power, i.e. "abc" -> a*base^2 + b*base + c
// Backed by an iterative bottom-up segment tree over a fixed buffer, with two cursors marking the
// live window inside it. An unused slot holds the value 0 and still occupies its slot, so every
// node's width is just its subtree size - that makes the merge shift a per-level constant
// (levelPow) and means no per-node length has to be stored. Padding zeros can never pollute an
// answer because hashRange only accumulates nodes lying entirely inside [left, right).
// The merge is NOT commutative, so hashRange accumulates its left-side and right-side pieces
// separately and joins them at the end.
// Unlike the 2-stacks version this DOES support swapCharAt, at the cost of O(log n) instead of
// O(1). Still slower than the 2-stacks version, so only reach for this when you actually
// need swapCharAt.
// maxLeftGrowth / maxRightGrowth are how many chars you will ever add past each end of `string`.
// They are required and they are HARD LIMITS: exceeding one throws. There is no auto-grow, so
// every op is a true O(log n) with no hidden rebuild, and the buffer never balloons.
// Note popCharLeft does NOT give the space back - a window slid right n times consumes n slots of
// right growth, so size maxRightGrowth for total slides, not for the live window length.
// Popping is O(1): it only moves a cursor and leaves the leaf stale. Safe for the same reason the
// padding is safe - a node holding a dead slot is never read, and addChar overwrites the leaf
// before it can be. The consequence is that the chars buffer holds garbage outside [left, right),
// so always slice by the cursors.
// Capacity is rounded up to a power of two, which gives leaves at cap+i and a 2*cap node array.

// RangeHashingSeg h("abc", 0, 100);                      // never prepend, append up to 100 chars
// RangeHashingSeg h("", n, n);                           // build either direction, up to n each
// RangeHashingSeg h("abc", 0, 100, 131, 1000000007);     // your base and mod

// h.hashRange(l, r) -> ll     hash of window[l..r] inclusive, 0-indexed, O(log n)
// h.getHash() -> ll           hash of the whole current window, O(log n)
// h.hash(s) -> ll             hash of an arbitrary string with these base/mod (for comparisons), O(len(s))
// h.addChar(c) -> void        append c on the right, O(log n)
// h.popChar() -> void         drop the rightmost char, O(1)
// h.popChars(cnt) -> void     drop the last cnt chars, O(1)
// h.addCharLeft(c) -> void    prepend c on the left, O(log n)
// h.popCharLeft() -> void     drop the leftmost char, O(1)
// h.popCharsLeft(cnt) -> void drop the first cnt chars, O(1)
// h.slideRight(c) -> void     popCharLeft + addChar (slide a fixed window right), O(log n)
// h.slideLeft(c) -> void      popChar + addCharLeft (slide a fixed window left), O(log n)
// h.rotateRight() -> void     move rightmost char to the front (ABC -> CAB), O(log n)
// h.rotateLeft() -> void      move leftmost char to the end (ABC -> BCA), O(log n)
// h.swapCharAt(i, c) -> void  replace char at index i, O(log n)
// h.charAt(i) -> char         char at index i, O(1)
// h.getCurrentWindow() -> string   the current window as a string, O(n)
// h.length() -> int           current window length, O(1)

class RangeHashingSeg {
public:
    // List of good prime numbers for hashing, will choose randomly if not provided
    inline static const vector<ll> GOOD_MODS = {
        1000000007LL, 1000000009LL, 1000000021LL, 1000000033LL,
        1000000087LL, 1000000093LL, 1000000097LL, 1000000103LL,
        1000000123LL, 1000000181LL, 1000000207LL, 1000000223LL,
        1000000241LL, 1000000271LL, 1000000289LL, 1000000297LL};

    // O(capacity) time
    // Base is ideally prime and coprime to mod; mod > max char value keeps distinct chars distinct.
    RangeHashingSeg(const string& s, int maxLeftGrowth, int maxRightGrowth,
                    ll base = 911, ll mod = -1)
        : base(base), mod(mod != -1 ? mod : GOOD_MODS[randIndex(GOOD_MODS.size())]) {
        basePow = {1}; // base^i % mod, grown lazily
        allocate(maxLeftGrowth, s, maxRightGrowth);
    }

    // Hash of an arbitrary string with these base/mod (e.g. the pattern to match against)
    // O(len) time
    ll hash(const string& s) const {
        ll res = 0, b = base, m = mod;
        for (char c : s) res = (res * b + (ll)c) % m;
        return res;
    }

    // Appends a char on the right
    // O(log n) time
    void addChar(char c) {
        if (right == cap) throw out_of_range("out of right growth, raise maxRightGrowth");
        pointSet(right, c);
        right++;
    }

    // Prepends a char on the left
    // O(log n) time
    void addCharLeft(char c) {
        if (left == 0) throw out_of_range("out of left growth, raise maxLeftGrowth");
        left--;
        pointSet(left, c);
    }

    // Removes the rightmost char. Just moves the cursor - the leaf is left stale on purpose, see
    // the note at the top of the file
    // O(1) time
    void popChar() {
        if (right == left) return;
        right--;
    }

    // Removes the leftmost char. Just moves the cursor, same as popChar
    // O(1) time
    void popCharLeft() {
        if (right == left) return;
        left++;
    }

    // Removes the last `count` chars in one cursor move, clamped at empty
    // O(1) time
    void popChars(int count) {
        if (count >= right - left) right = left;
        else right -= count;
    }

    // Removes the first `count` chars in one cursor move, clamped at empty
    // O(1) time
    void popCharsLeft(int count) {
        if (count >= right - left) left = right;
        else left += count;
    }

    // Slides a fixed-size window right: drop leftmost, add c on the right
    // O(log n) time
    void slideRight(char c) {
        popCharLeft();
        addChar(c);
    }

    // Slides a fixed-size window left: drop rightmost, add c on the left
    // O(log n) time
    void slideLeft(char c) {
        popChar();
        addCharLeft(c);
    }

    // moves rightmost letter to front, like ABC -> CAB
    // O(log n) time
    void rotateRight() {
        if (length() < 2) return;
        char c = chars[right - 1];
        popChar();
        addCharLeft(c);
    }

    // moves leftmost letter to the end, like ABC -> BCA
    // O(log n) time
    void rotateLeft() {
        if (length() < 2) return;
        char c = chars[left];
        popCharLeft();
        addChar(c);
    }

    // Replaces the char at a logical index
    // O(log n) time
    void swapCharAt(int index, char newChar) {
        if (index < 0 || index >= length()) throw out_of_range("Index out of range");
        pointSet(left + index, newChar);
    }

    // Hash of window[l..r], inclusive, 0-indexed over the logical window
    // Nodes picked up on the left get appended to the left accumulator, nodes picked up on the
    // right get prepended to the right accumulator; the merge is not commutative so the two
    // sides are kept apart until the final join. Node widths come from the level counter h
    // O(log n) time
    ll hashRange(int l, int r) {
        if (l > r) return 0;
        int lo = cap + left + l;
        int hi = cap + left + r + 1;
        ll lh = 0, rh = 0;
        int rlen = 0, h = 0;
        while (lo < hi) {
            if (lo & 1) {
                lh = (lh * levelPow[h] + hashes[lo]) % mod;
                lo++;
            }
            if (hi & 1) {
                hi--;
                rh = (hashes[hi] * basePow[rlen] + rh) % mod;
                rlen += 1 << h;
            }
            lo >>= 1; hi >>= 1; h++;
        }
        return (lh * basePow[rlen] + rh) % mod;
    }

    // Hash of the whole current window
    // O(log n) time
    ll getHash() {
        if (length() == 0) return 0;
        return hashRange(0, length() - 1);
    }

    // Char at a logical index
    // O(1) time
    char charAt(int index) const { return chars[left + index]; }

    // Returns the current window as a string
    // O(n) time
    string getCurrentWindow() const {
        return string(chars.begin() + left, chars.begin() + right);
    }

    // Returns the length of the current window
    // O(1) time
    int length() const { return right - left; }

private:
    vector<char> chars;   // the raw buffer; only [left, right) is live
    vector<ll> hashes;    // 2*cap nodes, leaves at cap+i
    vector<ll> basePow;   // base^i % mod
    vector<ll> levelPow;  // levelPow[h] = base^(2^h), the shift for merging two children of height h
    ll base;
    ll mod;
    int cap = 0;
    int left = 0;
    int right = 0;

    // Lays out `s` with the requested slack on each side, rounds capacity up to a power of two
    // (leaves live at cap+i, so the node array is 2*cap), and builds level by level
    // O(capacity) time
    void allocate(int leftSlack, const string& s, int rightSlack) {
        int need = leftSlack + (int)s.size() + rightSlack;
        cap = 1;
        while (cap < max(2, need)) cap *= 2;
        chars.assign(cap, 0);
        hashes.assign(2 * cap, 0);
        left = leftSlack;
        right = left + (int)s.size();
        ensureBasePow(cap);
        levelPow.clear();
        for (int h = 0; (1 << h) <= cap; h++) levelPow.push_back(basePow[1 << h]);
        for (int i = 0; i < (int)s.size(); i++) {
            chars[left + i] = s[i];
            hashes[cap + left + i] = (ll)s[i];
        }
        int h = 0;
        for (int lo = cap >> 1; lo >= 1; lo >>= 1) {
            for (int i = lo; i < (lo << 1); i++)
                hashes[i] = (hashes[2*i] * levelPow[h] + hashes[2*i+1]) % mod;
            h++;
        }
    }

    // Grows basePow until index `upTo` exists
    // amortized O(1)
    void ensureBasePow(int upTo) {
        while ((int)basePow.size() <= upTo)
            basePow.push_back(basePow.back() * base % mod);
    }

    // Writes one leaf and walks up recomputing parents; 0 means an empty slot
    // O(log n) time
    void pointSet(int pos, char c) {
        chars[pos] = c;
        int i = cap + pos;
        hashes[i] = (ll)c;
        i >>= 1;
        int h = 0;
        while (i) {
            int j = i << 1;
            hashes[i] = (hashes[j] * levelPow[h] + hashes[j+1]) % mod;
            h++;
            i >>= 1;
        }
    }

    static size_t randIndex(size_t sz) {
        static mt19937_64 rng(chrono::steady_clock::now().time_since_epoch().count());
        return rng() % sz;
    }
};