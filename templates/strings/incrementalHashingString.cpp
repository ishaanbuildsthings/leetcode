#include <bits/stdc++.h>
using namespace std;
using ll = long long;

// TEMPLATE BY github.com/ishaanbuildsthings PLEASE DO NOT USE

// works for all ascii strings

// hash convention: leftmost char is the highest power, i.e. "abc" -> a*base^2 + b*base + c

// IncrementalHashing h("abc");                     // uses all defaults (911 base, random mod)
// IncrementalHashing h("abc", 131);                // your base, default random mod
// IncrementalHashing h("abc", 131, 1000000007);    // your base and mod


// h.getHash() -> ll           hash of the whole current window, O(1)
// h.hash(s) -> ll             hash of an arbitrary string with these base/mod (for comparisons), O(len(s))
// h.addChar(c) -> void        append c on the right, O(1)
// h.popChar() -> void         drop the rightmost char, O(1)
// h.addCharLeft(c) -> void    prepend c on the left, O(1)
// h.popCharLeft() -> void     drop the leftmost char, O(1)
// h.slideRight(c) -> void     popCharLeft + addChar (slide a fixed window right), O(1)
// h.slideLeft(c) -> void      popChar + addCharLeft (slide a fixed window left), O(1)
// h.swapCharAt(i, c) -> void  replace char at index i, O(1) (std::deque has O(1) random access)
// h.getCurrentWindow() -> string   the current window as a string, O(n)
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
    // Base is ideally prime and coprime to mod (needed so baseInv exists); base size doesn't affect correctness once mod > max char value (mods here are >1e9, chars are their codepoint so always safe).
    IncrementalHashing(const string& s, ll base = 911, ll mod = -1)
        : base(base), mod(mod != -1 ? mod : GOOD_MODS[randIndex(GOOD_MODS.size())]) {
        window.assign(s.begin(), s.end());
        baseInv = modpow(this->base, this->mod - 2, this->mod); // mod is prime -> Fermat inverse
        basePow = {1};                                          // base^0 % mod, grown lazily
        hashValue = 0;
        ll b = this->base, m = this->mod;
        for (char c : window) hashValue = (hashValue * b + (ll)c) % m;
        ensureBasePow((int)window.size());
    }

    // Hash of the whole current window
    // O(1) time
    ll getHash() const { return hashValue; }

    // Hash of an arbitrary string with these base/mod (e.g. the pattern to match against)
    // O(len) time
    ll hash(const string& s) const {
        ll res = 0, b = base, m = mod;
        for (char c : s) res = (res * b + (ll)c) % m;
        return res;
    }

    // Appends a char on the right and updates the hash
    // O(1) time
    void addChar(char c) {
        window.push_back(c);
        hashValue = (hashValue * base + (ll)c) % mod;
        if ((int)basePow.size() <= (int)window.size()) // keep basePow one ahead of the window
            basePow.push_back(basePow.back() * base % mod);
    }

    // Removes the rightmost char and updates the hash
    // O(1) time
    void popChar() {
        if (window.empty()) return;
        char c = window.back();
        window.pop_back();
        hashValue = norm((hashValue - (ll)c) * baseInv);
    }

    // Prepends a char on the left and updates the hash
    // O(1) time
    void addCharLeft(char c) {
        window.push_front(c);
        int k = (int)window.size() - 1; // power of the new leftmost char = old length
        hashValue = ((ll)c * basePow[k] + hashValue) % mod;
        if ((int)basePow.size() <= (int)window.size()) // keep basePow one ahead of the window
            basePow.push_back(basePow.back() * base % mod);
    }

    // Removes the leftmost char and updates the hash
    // O(1) time
    void popCharLeft() {
        if (window.empty()) return;
        char c = window.front();
        window.pop_front();
        hashValue = norm(hashValue - (ll)c * basePow[(int)window.size()]);
    }

    // Slides a fixed-size window right: drop leftmost, add c on the right
    // O(1) time
    void slideRight(char c) {
        popCharLeft();
        addChar(c);
    }

    // Slides a fixed-size window left: drop rightmost, add c on the left
    // O(1) time
    void slideLeft(char c) {
        popChar();
        addCharLeft(c);
    }

    // Replaces the char at index and updates the hash
    // O(1) time (std::deque random access is O(1))
    void swapCharAt(int index, char newChar) {
        if (index < 0 || index >= (int)window.size())
            throw out_of_range("Index out of range");
        int power = (int)window.size() - 1 - index;
        char oldChar = window[index];
        window[index] = newChar;
        hashValue = norm(hashValue + ((ll)newChar - (ll)oldChar) * basePow[power]);
    }

    // Returns the current window as a string
    // O(n) time
    string getCurrentWindow() const {
        return string(window.begin(), window.end());
    }

    // Returns the length of the current window
    // O(1) time
    int length() const { return (int)window.size(); }

private:
    deque<char> window;
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