#include <bits/stdc++.h>
using namespace std;
using ll = long long;

// TEMPLATE BY github.com/ishaanbuildsthings PLEASE DO NOT USE

// assumes values are in 0...1e9 range; all mods in GOOD_MODS are > 1e9 to prevent value collisions; base=911 default
// for values >1e9 or negatives, give a mod bigger than the value range, compress values, or shift negatives up

// DOES NOT HAVE swapCharAt(i, newVal) - cause this version is built with some 2 stacks thing
// we can add swapCharAt but I think it makes operations O(logN) something with a seg tree

// hash convention: leftmost value is the highest power, i.e. {a,b,c} -> a*base^2 + b*base + c
// Same surface as IncrementalHashing, but backed by two stacks so arbitrary ranges are queryable.
// The deque is split into a front half (stored reversed, suffix-anchored hashes) and a back half
// (stored in order, prefix-anchored hashes). A range lands in one half or straddles both.

// IncrementalHashing h({1, 2, 3});                 // uses all defaults (911 base, random mod) (accepts vector<int> or vector<ll>)
// IncrementalHashing h(arr, 131);                  // your base, default random mod
// IncrementalHashing h(arr, 131, 1000000007);      // your base and mod

// h.hashRange(l, r) -> ll     hash of window[l..r] inclusive, 0-indexed, O(1)
// h.getHash() -> ll           hash of the whole current window, O(1)
// h.hash(a) -> ll             hash of an arbitrary array with these base/mod (for comparisons), O(len(a))
// h.addChar(v) -> void        append v on the right, O(1)
// h.popChar() -> void         drop the rightmost value, amortized O(1)
// h.addCharLeft(v) -> void    prepend v on the left, amortized O(1)
// h.popCharLeft() -> void     drop the leftmost value, amortized O(1)
// h.slideRight(v) -> void     popCharLeft + addChar (slide a fixed window right), amortized O(1)
// h.slideLeft(v) -> void      popChar + addCharLeft (slide a fixed window left), amortized O(1)
// h.rotateRight() -> void     move rightmost value to the front ({1,2,3} -> {3,1,2}), amortized O(1)
// h.rotateLeft() -> void      move leftmost value to the end ({1,2,3} -> {2,3,1}), amortized O(1)
// h.charAt(i) -> ll           value at index i, O(1)
// h.getCurrentWindow() -> vector<ll>   the current window as an array, O(n)
// h.length() -> int           current window length, O(1)

class IncrementalHashing {
public:
    // List of good prime numbers for hashing, will choose randomly if not provided
    inline static const vector<ll> GOOD_MODS = {
        1000000007LL, 1000000009LL, 1000000021LL, 1000000033LL,
        1000000087LL, 1000000093LL, 1000000097LL, 1000000103LL,
        1000000123LL, 1000000181LL, 1000000207LL, 1000000223LL,
        1000000241LL, 1000000271LL, 1000000289LL, 1000000297LL};

    // O(n) time
    // Assumes values in [0, 1e9]; every mod above is > 1e9 so raw values are safe (mod > max value keeps distinct values distinct).
    // Base is ideally prime and coprime to mod (needed so baseInv exists); base size doesn't affect correctness once mod > max value.
    // Templated so it accepts vector<int> (LeetCode's nums) or vector<ll>; stored internally as ll.
    template <class T>
    IncrementalHashing(const vector<T>& arr, ll base = 911, ll mod = -1)
        : base(base), mod(mod != -1 ? mod : GOOD_MODS[randIndex(GOOD_MODS.size())]) {
        baseInv = modpow(this->base, this->mod - 2, this->mod); // mod is prime -> Fermat inverse
        basePow = {1};                                          // base^i % mod, grown lazily
        baseInvPow = {1};                                       // baseInv^i % mod, needed to shift a front-half range down to power 0
        frontHashes = {0};                                      // frontHashes[j] = hash of the last j values of the front half
        backHashes = {0};                                       // backHashes[j] = hash of the first j values of the back half
        for (const T& v : arr) addChar((ll)v);
    }

    // Hash of an arbitrary array with these base/mod (e.g. the pattern to match against)
    // O(len) time
    template <class T>
    ll hash(const vector<T>& a) const {
        ll res = 0, b = base, m = mod;
        for (const T& v : a) res = (res * b + (ll)v) % m;
        return res;
    }

    // Appends a value on the right
    // O(1) time
    void addChar(ll v) {
        back.push_back(v);
        backHashes.push_back((backHashes.back() * base + v) % mod);
    }

    // Prepends a value on the left
    // amortized O(1) time
    void addCharLeft(ll v) {
        int power = (int)front.size();
        ensureBasePow(power);
        front.push_back(v);
        frontHashes.push_back((v * basePow[power] + frontHashes.back()) % mod);
    }

    // Removes the rightmost value
    // amortized O(1) time
    void popChar() {
        if (back.empty()) rebalance(false);
        if (!back.empty()) { back.pop_back(); backHashes.pop_back(); }
    }

    // Removes the leftmost value
    // amortized O(1) time
    void popCharLeft() {
        if (front.empty()) rebalance(true);
        if (!front.empty()) { front.pop_back(); frontHashes.pop_back(); }
    }

    // Slides a fixed-size window right: drop leftmost, add v on the right
    // amortized O(1) time
    void slideRight(ll v) { popCharLeft(); addChar(v); }

    // Slides a fixed-size window left: drop rightmost, add v on the left
    // amortized O(1) time
    void slideLeft(ll v) { popChar(); addCharLeft(v); }

    // moves rightmost value to front, like {1,2,3} -> {3,1,2}
    // amortized O(1) time
    void rotateRight() {
        if (length() < 2) return;
        ll v = charAt(length() - 1);
        popChar();
        addCharLeft(v);
    }

    // moves leftmost value to the end, like {1,2,3} -> {2,3,1}
    // amortized O(1) time
    void rotateLeft() {
        if (length() < 2) return;
        ll v = charAt(0);
        popCharLeft();
        addChar(v);
    }

    // Hash of window[l..r], inclusive, 0-indexed over the logical window
    // O(1) time
    ll hashRange(int l, int r) {
        if (l > r) return 0;
        int f = (int)front.size();
        if (r < f) {
            // frontHashes[f-l] is the suffix from l, frontHashes[f-1-r] is the suffix from r+1,
            // so the difference is window[l..r] shifted up by base^(f-1-r); divide it back down
            ensureBasePow(f - 1 - r);
            return norm(norm(frontHashes[f - l] - frontHashes[f - 1 - r]) * baseInvPow[f - 1 - r]);
        }
        if (l >= f) {
            int a = l - f, b = r - f;
            ensureBasePow(b + 1 - a);
            return norm(backHashes[b + 1] - backHashes[a] * basePow[b + 1 - a] % mod);
        }
        ensureBasePow(r - f + 1);
        ll leftPart = hashRange(l, f - 1);
        ll rightPart = hashRange(f, r);
        return norm(leftPart * basePow[r - f + 1] + rightPart);
    }

    // Hash of the whole current window
    // O(1) time
    ll getHash() { return hashRange(0, length() - 1); }

    // Value at a logical index
    // O(1) time
    ll charAt(int index) const {
        int f = (int)front.size();
        return index < f ? front[f - 1 - index] : back[index - f];
    }

    // Returns the current window as an array
    // O(n) time
    vector<ll> getCurrentWindow() const {
        vector<ll> res;
        res.reserve(front.size() + back.size());
        for (int i = (int)front.size() - 1; i >= 0; i--) res.push_back(front[i]);
        for (ll v : back) res.push_back(v);
        return res;
    }

    // Returns the length of the current window
    // O(1) time
    int length() const { return (int)front.size() + (int)back.size(); }

private:
    vector<ll> front;        // leftmost values, REVERSED: front[0] is the value nearest the middle
    vector<ll> frontHashes;
    vector<ll> back;         // rightmost values, in order
    vector<ll> backHashes;
    ll base;
    ll mod;
    ll baseInv;
    vector<ll> basePow;
    vector<ll> baseInvPow;

    // Python's % is always non-negative for a positive modulus; C++'s is not, so normalize
    ll norm(ll x) const {
        x %= mod;
        if (x < 0) x += mod;
        return x;
    }

    // Grows both power tables until index `upTo` exists
    // amortized O(1)
    void ensureBasePow(int upTo) {
        while ((int)basePow.size() <= upTo) basePow.push_back(basePow.back() * base % mod);
        while ((int)baseInvPow.size() <= upTo) baseInvPow.push_back(baseInvPow.back() * baseInv % mod);
    }

    // Splits the window in half and rebuilds both stacks, called when the side we need is empty
    // O(n) but amortized O(1) across a sequence of ops
    void rebalance(bool needFront) {
        vector<ll> window = getCurrentWindow();
        int n = (int)window.size();
        if (n == 0) return;
        int mid = needFront ? (n + 1) / 2 : n / 2;
        mid = needFront ? max(1, mid) : min(n - 1, mid);
        front.clear(); frontHashes.assign(1, 0);
        for (int i = mid - 1; i >= 0; i--) addCharLeft(window[i]);
        back.clear(); backHashes.assign(1, 0);
        for (int i = mid; i < n; i++) addChar(window[i]);
    }

    static ll modpow(ll b, ll e, ll m) {
        ll r = 1;
        b %= m;
        while (e > 0) {
            if (e & 1) r = r * b % m;
            b = b * b % m;
            e >>= 1;
        }
        return r;
    }

    static size_t randIndex(size_t sz) {
        static mt19937_64 rng(chrono::steady_clock::now().time_since_epoch().count());
        return rng() % sz;
    }
};