#include <bits/stdc++.h>
using namespace std;
using ll = long long;

// Palindrome hashing over a string via prefix + reversed-prefix rolling hashes.

// Works out of the box for all ASCII strings uses base=911, random mod

// PalindromeHashing h("abacaba");                    // uses all defaults
// PalindromeHashing h("abacaba", 131);               // your base, default mod
// PalindromeHashing h("abacaba", 131, 1000000007);   // your base and mod


// h.isPalindrome(l, r); -> bool
// h.getHashForSubstring(l, r); -> ll
// h.getHashForReversedSubstring(l, r); -> ll
// h.addChar(c); -> void     appends a char to the end, but breaks palindromic work(?) since reverse hashes are not maintained
// h.popChar(); -> void      pops the last char, breaks palindromic work(?) since reverse hashes are not maintained
// h.getHash(); -> ll        the overall hash
// h.getCurrentWindow(); -> string     just returns the current string O(n) as we return by value
// h.length(); -> int         how long is our window
// h.longestPalindromeCenteredAroundI(i); -> pair<int,int> gives us L and R for the longest centered around i, O(logN)
// h.longestPalindromeCenteredAroundIAndIPlusOne(i); -> pair<int,int> gives us L and R for the longest centered around [i...i+1] or {i+1,i} if invalid center, O(logN)


class PalindromeHashing {
public:
    // List of good prime numbers for hashing, will choose randomly if not provided
    inline static const vector<ll> GOOD_MODS = {
        1000000007LL, 1000000009LL, 1000000021LL, 1000000033LL,
        1000000087LL, 1000000093LL, 1000000097LL, 1000000103LL,
        1000000123LL, 1000000181LL, 1000000207LL, 1000000223LL,
        1000000241LL, 1000000271LL, 1000000289LL, 1000000297LL};

    // O(n) time
    // Base is ideally prime, and bigger than the max value hashFunc can output, otherwise we can get collisions e.g. base=3, [1,1] collides with [4]. Base should also be coprime to mod I think?
    // mod=-1 is a temporary C++ thing, if we don't pass a mod in then it detects this and picks a random one from above
    PalindromeHashing(const string& str, ll base = 911, ll mod = -1,
                      function<ll(char)> hashFunc = [](char c) { return (ll)c; })
        : window(str), base(base),
          mod(mod != -1 ? mod : GOOD_MODS[randIndex(GOOD_MODS.size())]),
          hashFunc(hashFunc) {
        prefixHashes = buildPrefixHashes(str);               // O(n) time
        reversePrefixHashes = buildReversePrefixHashes(str); // O(n) time
        basePow = precomputeBasePowers((int)str.size());     // O(n) time
    }

    // Gets the hash of a substring [left...right] using math
    // O(1) time
    ll getHashForSubstring(int left, int right) const {
        return norm(prefixHashes[right + 1] - prefixHashes[left] * basePow[right - left + 1]);
    }

    // Gets the hash of a reversed section of the string, uses the original string indices
    // O(1) time
    ll getHashForReversedSubstring(int originalStringLeft, int originalStringRight) const {
        int n = (int)window.size();
        int left = n - originalStringRight - 1;
        int right = n - originalStringLeft;
        return norm(reversePrefixHashes[right] - reversePrefixHashes[left] * basePow[right - left]);
    }

    // O(1) time
    bool isPalindrome(int left, int right) const {
        return getHashForSubstring(left, right) == getHashForReversedSubstring(left, right);
    }

    // Longest odd-length palindrome centered at i. Returns inclusive {l, r} (always valid, >= {i, i}).
    // O(log n) time
    pair<int, int> longestPalindromeCenteredAroundI(int i) const {
        int n = (int)window.size();
        int lo = 1, hi = min(i + 1, n - i), best = 1; // best = radius (chars on each side incl. center)
        while (lo <= hi) {
            int m = (lo + hi) / 2;
            if (isPalindrome(i - m + 1, i + m - 1)) { best = m; lo = m + 1; }
            else hi = m - 1;
        }
        return {i - best + 1, i + best - 1};
    }
 
    // Longest even-length palindrome centered between i and i+1. Returns inclusive {l, r},
    // or an empty range (l > r, i.e. {i+1, i}) if s[i] != s[i+1].
    // O(log n) time
    pair<int, int> longestPalindromeCenteredAroundIAndIPlusOne(int i) const {
        int n = (int)window.size();
        int lo = 1, hi = min(i + 1, n - i - 1), best = 0; // best = radius (chars on each side of the gap)
        while (lo <= hi) {
            int m = (lo + hi) / 2;
            if (isPalindrome(i - m + 1, i + m)) { best = m; lo = m + 1; }
            else hi = m - 1;
        }
        return {i - best + 1, i + best};
    }
 

    // Adds a character to the end of the string and updates hashes
    // O(1) time
    void addChar(char c) {
        window.push_back(c);
        if ((int)window.size() > (int)basePow.size())
            basePow.push_back(norm(basePow.back() * base));
        prefixHashes.push_back(norm(prefixHashes.back() * base + hashFunc(c)));
        reversePrefixHashes.push_back(norm(reversePrefixHashes.back() * base + hashFunc(c)));
    }

    // Removes the last character from the string and updates hashes
    // O(1) time
    void popChar() {
        if (window.empty()) return;
        window.pop_back();
        prefixHashes.pop_back();
        reversePrefixHashes.pop_back();
    }

    // Gets the hash of the entire window
    // O(1) time
    ll getHash() const { return prefixHashes.back(); }

    // Returns the current window
    // O(1) time
    string getCurrentWindow() const { return window; }

    // Returns the length of the current window
    // O(1) time
    int length() const { return (int)window.size(); }

private:
    string window;
    ll base;
    ll mod;
    function<ll(char)> hashFunc; // The output coefficient for a single char, like ord('a')
    vector<ll> prefixHashes;
    vector<ll> reversePrefixHashes;
    vector<ll> basePow;

    // Python's % always returns non-negative for a positive modulus; C++'s does not, so normalize
    ll norm(ll x) const {
        x %= mod;
        if (x < 0) x += mod;
        return x;
    }

    static size_t randIndex(size_t n) {
        static mt19937_64 rng(chrono::steady_clock::now().time_since_epoch().count());
        return rng() % n;
    }

    // Builds the prefix hashes of the string, prefixHashes[i] is for string[:i], so prefixHashes[0] is for the empty string
    // O(n) time
    vector<ll> buildPrefixHashes(const string& str) {
        int n = (int)str.size();
        vector<ll> prefixHashes(n + 1, 0);
        for (int i = 1; i <= n; i++)
            prefixHashes[i] = norm(prefixHashes[i - 1] * base + hashFunc(str[i - 1]));
        return prefixHashes;
    }

    // Builds the prefix hashes of the reversed string, so reversedPrefixHashes[2] is the hash of the first two character prefix, but that prefix is reversed. reversedPrefixHashes[0] is for the empty string
    // string = 'abc', reverse prefixes are 'a', 'ba', 'cba'
    // O(n) time
    vector<ll> buildReversePrefixHashes(const string& str) {
        int n = (int)str.size();
        vector<ll> reversePrefixHashes(n + 1, 0);
        for (int i = 1; i <= n; i++)
            reversePrefixHashes[i] = norm(reversePrefixHashes[i - 1] * base + hashFunc(str[n - i]));
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