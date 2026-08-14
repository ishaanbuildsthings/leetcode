#include <bits/stdc++.h>
using namespace std;
using ll = long long;

// Palindrome hashing over an integer array via prefix + reversed-prefix rolling hashes.

// assumes values are in 0...1e9 range
// all mods in GOOD_MODS are > 1e9 to prevent value collisions
// base=911 is default

// for values >1e9 or negatives, give a mod bigger than the value range, compress values, or shift negatives up

// PalindromeHashing h({1, 2, 3, 2, 1});                 // uses all defaults (accepts vector<int> or vector<ll>)
// PalindromeHashing h(arr, 131);                        // your base, default mod
// PalindromeHashing h(arr, 131, 1000000007);            // your base and mod


// h.isPalindrome(l, r) -> bool
// h.getHashForSubstring(l, r) -> ll
// h.getHashForReversedSubstring(l, r) -> ll
// h.addChar(v) -> void     appends a value to the end, but breaks palindromic work(?) since reverse hashes are not maintained
// h.popChar() -> void      pops the last value, breaks palindromic work(?) since reverse hashes are not maintained
// h.getHash() -> ll        the overall hash
// h.getCurrentWindow() -> vector<ll>   just returns the current array O(n) as we return by value
// h.length() -> int        how long is our window
// h.longestPalindromeCenteredAroundI(i) -> pair<int,int> gives us L and R for the longest centered around i, O(logN)
// h.longestPalindromeCenteredAroundIAndIPlusOne(i) -> pair<int,int> gives us L and R for the longest centered around [i...i+1] or {i+1,i} if invalid center, O(logN)

// unlike the python version, no manual inlining is needed: with -O2 the compiler inlines the in-class
// methods and hoists the vector accesses, so the clean isPalindrome-based structure is already fast.


class PalindromeHashing {
public:
    // List of good prime numbers for hashing, will choose randomly if not provided
    inline static const vector<ll> GOOD_MODS = {
        1000000007LL, 1000000009LL, 1000000021LL, 1000000033LL,
        1000000087LL, 1000000093LL, 1000000097LL, 1000000103LL,
        1000000123LL, 1000000181LL, 1000000207LL, 1000000223LL,
        1000000241LL, 1000000271LL, 1000000289LL, 1000000297LL};

    // O(n) time
    // Assumes values in [0, 1e9]; every mod above is > 1e9 so raw values are safe (mod > max value keeps distinct values distinct).
    // Base is ideally prime and coprime to mod; base size doesn't affect correctness once mod > max value.
    // Templated so it accepts vector<int> (LeetCode's nums) or vector<ll>; stored internally as ll.
    template <class T>
    PalindromeHashing(const vector<T>& arr, ll base = 911, ll mod = -1)
        : base(base), mod(mod != -1 ? mod : GOOD_MODS[randIndex(GOOD_MODS.size())]) {
        window.assign(arr.begin(), arr.end());
        n = (int)window.size();
        prefixHashes = buildPrefixHashes();               // O(n) time
        reversePrefixHashes = buildReversePrefixHashes();  // O(n) time
        basePow = precomputeBasePowers(n);                 // O(n) time
    }

    // Gets the hash of a subarray [left...right] using math
    // O(1) time
    ll getHashForSubstring(int left, int right) const {
        return norm(prefixHashes[right + 1] - prefixHashes[left] * basePow[right - left + 1]);
    }

    // Gets the hash of a reversed section of the array, uses the original array indices
    // O(1) time
    ll getHashForReversedSubstring(int originalLeft, int originalRight) const {
        int left = n - originalRight - 1;
        int right = n - originalLeft;
        return norm(reversePrefixHashes[right] - reversePrefixHashes[left] * basePow[right - left]);
    }

    // O(1) time
    bool isPalindrome(int left, int right) const {
        return getHashForSubstring(left, right) == getHashForReversedSubstring(left, right);
    }

    // Longest odd-length palindrome centered at i. Returns inclusive {l, r} (always valid, >= {i, i}).
    // O(log n) time
    pair<int, int> longestPalindromeCenteredAroundI(int i) const {
        int lo = 1, hi = min(i + 1, n - i), best = 1; // best = radius (values on each side incl. center)
        while (lo <= hi) {
            int m = (lo + hi) / 2;
            if (isPalindrome(i - m + 1, i + m - 1)) { best = m; lo = m + 1; }
            else hi = m - 1;
        }
        return {i - best + 1, i + best - 1};
    }

    // Longest even-length palindrome centered between i and i+1. Returns inclusive {l, r},
    // or an empty range (l > r, i.e. {i+1, i}) if arr[i] != arr[i+1].
    // O(log n) time
    pair<int, int> longestPalindromeCenteredAroundIAndIPlusOne(int i) const {
        if (i + 1 >= n || window[i] != window[i + 1]) return {i + 1, i}; // O(1) short-circuit: no even palindrome here
        int lo = 1, hi = min(i + 1, n - i - 1), best = 0; // best = radius (values on each side of the gap)
        while (lo <= hi) {
            int m = (lo + hi) / 2;
            if (isPalindrome(i - m + 1, i + m)) { best = m; lo = m + 1; }
            else hi = m - 1;
        }
        return {i - best + 1, i + best};
    }

    // Adds a value to the end of the array and updates hashes
    // O(1) time
    void addChar(ll v) {
        window.push_back(v);
        n++;
        if (n > (int)basePow.size())
            basePow.push_back(norm(basePow.back() * base));
        prefixHashes.push_back(norm(prefixHashes.back() * base + v));
        reversePrefixHashes.push_back(norm(reversePrefixHashes.back() * base + v));
    }

    // Removes the last value from the array and updates hashes
    // O(1) time
    void popChar() {
        if (n == 0) return;
        window.pop_back();
        n--;
        prefixHashes.pop_back();
        reversePrefixHashes.pop_back();
    }

    // Gets the hash of the entire window
    // O(1) time
    ll getHash() const { return prefixHashes.back(); }

    // Returns the current window
    // O(n) time (copies the array)
    vector<ll> getCurrentWindow() const { return window; }

    // Returns the length of the current window
    // O(1) time
    int length() const { return n; }

private:
    vector<ll> window;
    int n;
    ll base;
    ll mod;
    vector<ll> prefixHashes;
    vector<ll> reversePrefixHashes;
    vector<ll> basePow;

    // Python's % always returns non-negative for a positive modulus; C++'s does not, so normalize
    ll norm(ll x) const {
        x %= mod;
        if (x < 0) x += mod;
        return x;
    }

    static size_t randIndex(size_t sz) {
        static mt19937_64 rng(chrono::steady_clock::now().time_since_epoch().count());
        return rng() % sz;
    }

    // Builds the prefix hashes of the array, prefixHashes[i] is for arr[:i], so prefixHashes[0] is for the empty array
    // O(n) time
    vector<ll> buildPrefixHashes() {
        vector<ll> prefixHashes(n + 1, 0);
        for (int i = 1; i <= n; i++)
            prefixHashes[i] = norm(prefixHashes[i - 1] * base + window[i - 1]);
        return prefixHashes;
    }

    // Builds the prefix hashes of the reversed array, so reversedPrefixHashes[2] is the hash of the first two element prefix, but that prefix is reversed. reversedPrefixHashes[0] is for the empty array
    // arr = [a, b, c], reverse prefixes are [a], [b, a], [c, b, a]
    // O(n) time
    vector<ll> buildReversePrefixHashes() {
        vector<ll> reversePrefixHashes(n + 1, 0);
        for (int i = 1; i <= n; i++)
            reversePrefixHashes[i] = norm(reversePrefixHashes[i - 1] * base + window[n - i]);
        return reversePrefixHashes;
    }

    // Precompute powers of base, so base^0 % MOD, base^1 % MOD, base^2 % MOD, ...
    // O(n) time
    vector<ll> precomputeBasePowers(int length) {
        vector<ll> basePow(length + 1, 1);
        for (int i = 1; i <= length; i++)
            basePow[i] = norm(basePow[i - 1] * base);
        return basePow;
    }
};