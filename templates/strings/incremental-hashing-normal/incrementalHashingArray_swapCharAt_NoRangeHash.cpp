#include <bits/stdc++.h>
using namespace std;
using ll = long long;

// TEMPLATE BY github.com/ishaanbuildsthings PLEASE DO NOT USE


// assumes values are in 0...1e9 range; all mods in GOOD_MODS are > 1e9 to prevent value collisions; base=911 default
// for values >1e9 or negatives, give a mod bigger than the value range, compress values, or shift negatives up

// IncrementalHashing h({1, 2, 3});                 // uses all defaults (911 base, random mod) (accepts vector<int> or vector<ll>)
// IncrementalHashing h(arr, 131);                  // your base, default random mod
// IncrementalHashing h(arr, 131, 1000000007);      // your base and mod


// h.getHash() -> ll           hash of the whole current window, O(1)
// h.hash(a) -> ll             hash of an arbitrary array with these base/mod (for comparisons), O(len(a))
// h.addChar(v) -> void        append v on the right, O(1)
// h.popChar() -> void         drop the rightmost value, O(1)
// h.addCharLeft(v) -> void    prepend v on the left, O(1)
// h.popCharLeft() -> void     drop the leftmost value, O(1)
// h.slideRight(v) -> void     popCharLeft + addChar (slide a fixed window right), O(1)
// h.slideLeft(v) -> void      popChar + addCharLeft (slide a fixed window left), O(1)
// h.swapCharAt(i, v) -> void  replace value at index i, O(1) (std::deque has O(1) random access)
// h.getCurrentWindow() -> vector<ll>   the current window as an array, O(n)
// h.length() -> int           current window length, O(1)
// h.rotateRight() -> void     move rightmost value to the front ({1,2,3} -> {3,1,2}), O(1)
// h.rotateLeft() -> void      move leftmost value to the end ({1,2,3} -> {2,3,1}), O(1)


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
        window.assign(arr.begin(), arr.end()); // converts to ll
        baseInv = modpow(this->base, this->mod - 2, this->mod); // mod is prime -> Fermat inverse
        basePow = {1};                                          // base^0 % mod, grown lazily
        hashValue = 0;
        ll b = this->base, m = this->mod;
        for (ll v : window) hashValue = (hashValue * b + v) % m;
        ensureBasePow((int)window.size());
    }

    // Hash of the whole current window
    // O(1) time
    ll getHash() const { return hashValue; }

    // Hash of an arbitrary array with these base/mod (e.g. the pattern to match against)
    // O(len) time
    template <class T>
    ll hash(const vector<T>& a) const {
        ll res = 0, b = base, m = mod;
        for (const T& v : a) res = (res * b + (ll)v) % m;
        return res;
    }

    // Appends a value on the right and updates the hash
    // O(1) time
    void addChar(ll v) {
        window.push_back(v);
        hashValue = (hashValue * base + v) % mod;
        if ((int)basePow.size() <= (int)window.size()) // keep basePow one ahead of the window
            basePow.push_back(basePow.back() * base % mod);
    }

    // Removes the rightmost value and updates the hash
    // O(1) time
    void popChar() {
        if (window.empty()) return;
        ll v = window.back();
        window.pop_back();
        hashValue = norm((hashValue - v) * baseInv);
    }

    // Prepends a value on the left and updates the hash
    // O(1) time
    void addCharLeft(ll v) {
        window.push_front(v);
        int k = (int)window.size() - 1; // power of the new leftmost value = old length
        hashValue = (v * basePow[k] + hashValue) % mod;
        if ((int)basePow.size() <= (int)window.size()) // keep basePow one ahead of the window
            basePow.push_back(basePow.back() * base % mod);
    }

    // Removes the leftmost value and updates the hash
    // O(1) time
    void popCharLeft() {
        if (window.empty()) return;
        ll v = window.front();
        window.pop_front();
        hashValue = norm(hashValue - v * basePow[(int)window.size()]);
    }

    // Slides a fixed-size window right: drop leftmost, add v on the right
    // O(1) time
    void slideRight(ll v) {
        popCharLeft();
        addChar(v);
    }

    // Slides a fixed-size window left: drop rightmost, add v on the left
    // O(1) time
    void slideLeft(ll v) {
        popChar();
        addCharLeft(v);
    }

    // Replaces the value at index and updates the hash
    // O(1) time (std::deque random access is O(1))
    void swapCharAt(int index, ll newVal) {
        if (index < 0 || index >= (int)window.size())
            throw out_of_range("Index out of range");
        int power = (int)window.size() - 1 - index;
        ll oldVal = window[index];
        window[index] = newVal;
        hashValue = norm(hashValue + (newVal - oldVal) * basePow[power]);
    }

    // Returns the current window as an array
    // O(n) time
    vector<ll> getCurrentWindow() const {
        return vector<ll>(window.begin(), window.end());
    }

    // Returns the length of the current window
    // O(1) time
    int length() const { return (int)window.size(); }

    // moves rightmost value to front, like {1,2,3} -> {3,1,2}
    // O(1) time
    void rotateRight() {
        if (window.size() < 2) return;
        ll v = window.back();
        window.pop_back();
        window.push_front(v);
        // divide out v from the right, then re-add it at power n-1
        ll hv = norm((hashValue - v) * baseInv);
        hashValue = norm(hv + norm(v * basePow[(int)window.size() - 1]));
    }

    // moves leftmost value to the end, like {1,2,3} -> {2,3,1}
    // O(1) time
    void rotateLeft() {
        if (window.size() < 2) return;
        ll v = window.front();
        window.pop_front();
        window.push_back(v);
        // subtract v from the top power, shift left, re-add at power 0
        ll hv = norm(hashValue * base);
        hashValue = norm(hv + norm(v * (1 - basePow[(int)window.size()])));
    }

private:
    deque<ll> window;
    ll base;
    ll mod;
    ll baseInv;
    ll hashValue;
    vector<ll> basePow;

    // Python's % is always non-negative for a positive modulus; C++'s is not, so normalize
    ll norm(ll x) const {
        x %= mod;
        if (x < 0) x += mod;
        return x;
    }

    // Grows basePow until index `upTo` exists
    // amortized O(1)
    void ensureBasePow(int upTo) {
        while ((int)basePow.size() <= upTo)
            basePow.push_back(basePow.back() * base % mod);
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