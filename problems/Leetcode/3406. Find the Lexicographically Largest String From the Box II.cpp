// # silly arbitrage
// class Solution:
//     def answerString(self, word: str, numFriends: int) -> str:
//         return max(word[start:start+len(word) - (numFriends - 1)] for start in range(len(word))) if numFriends != 1 else word


// proper solution
static long long defaultHashFunc(char c) {
    return static_cast<long long>(c);
}

class PalindromeHashing {
public:
    /*
     * Constructor (O(n) time).
     */
    PalindromeHashing(const string& s,
                      long long base = 911,
                      long long modVal = -1,
                      function<long long(char)> hashFunc = defaultHashFunc) {
        window.assign(s.begin(), s.end());
        this->base = base;

        static random_device rd;
        static mt19937_64 eng(rd());
        static vector<long long> GOOD_MODS = {
            1000000007LL, 1000000009LL, 998244353LL, 999999937LL, 999999929LL,
            999999893LL, 999999797LL, 999999761LL, 999999757LL, 999999751LL,
            999999739LL, 999999733LL, 999999721LL, 999999697LL, 999999691LL,
            999999679LL, 999999673LL, 999999661LL, 999999649LL, 999999637LL,
            999999631LL, 999999587LL, 999999599LL, 999999577LL, 999999563LL,
            999999527LL, 999999519LL, 999999503LL, 999999491LL, 999999487LL
        };

        if (modVal == -1) {
            uniform_int_distribution<size_t> dist(0, GOOD_MODS.size() - 1);
            this->mod = GOOD_MODS[dist(eng)];
        } else {
            this->mod = modVal;
        }

        this->hashFunc = hashFunc;
        prefixHashes = buildPrefixHashes(s);
        reversePrefixHashes = buildReversePrefixHashes(s);
        basePow = precomputeBasePowers((int)s.size());
    }

    /*
     * Returns the hash of substring [left...right] (0-based indices).
     * O(1) time after precomputation
     */
    long long getHashForSubstring(int left, int right) {
        long long h = prefixHashes[right + 1]
            - (prefixHashes[left] * basePow[right - left + 1] % mod);
        if (h < 0) h += mod;
        return h;
    }

    /*
     * Returns the hash of the reversed substring [originalStringLeft...originalStringRight].
     * O(1) time after precomputation
     */
    long long getHashForReversedSubstring(int originalStringLeft, int originalStringRight) {
        int left = (int)window.size() - originalStringRight - 1;
        int right = (int)window.size() - originalStringLeft;
        long long h = reversePrefixHashes[right]
            - (reversePrefixHashes[left] * basePow[right - left] % mod);
        if (h < 0) h += mod;
        return h;
    }

    /*
     * Checks if substring [left...right] is a palindrome.
     * O(1) time with hashing
     */
    bool isPalindrome(int left, int right) {
        return getHashForSubstring(left, right) ==
               getHashForReversedSubstring(left, right);
    }

    /*
     * Returns the hash of an entire string in O(n)
     */
    long long hashString(const string& s) {
        long long res = 0;
        for (char c : s) {
            long long coeff = hashFunc(c);
            res = (res * base + coeff) % mod;
        }
        return res;
    }

    /*
     * Adds a character to the end in O(1)
     */
    void addChar(char c) {
        window.push_back(c);
        if ((int)window.size() > (int)basePow.size()) {
            basePow.push_back((basePow.back() * base) % mod);
        }
        long long frontHash = prefixHashes.back();
        frontHash = (frontHash * base + hashFunc(c)) % mod;
        prefixHashes.push_back(frontHash);

        long long revHash = reversePrefixHashes.back();
        revHash = (revHash * base + hashFunc(c)) % mod;
        reversePrefixHashes.push_back(revHash);
    }

    /*
     * Pops the last character in O(1)
     */
    void popChar() {
        if (window.empty()) return;
        window.pop_back();
        prefixHashes.pop_back();
        reversePrefixHashes.pop_back();
    }

    /*
     * Returns the hash of the entire current window in O(1)
     */
    long long getHash() {
        if (!prefixHashes.empty()) {
            return prefixHashes.back();
        }
        return 0LL;
    }

    /*
     * Returns the current window as a vector of chars in O(1)
     */
    vector<char> getCurrentWindow() {
        return window;
    }

    /*
     * Returns the length of the current window in O(1)
     */
    int length() {
        return (int)window.size();
    }

private:
    /*
     * Builds prefix hashes for s. prefixHashes[i] = hash of s[:i].
     * prefixHashes[0] = hash of empty prefix = 0
     * O(n)
     */
    vector<long long> buildPrefixHashes(const string& s) {
        vector<long long> pref(s.size() + 1, 0LL);
        for (int i = 1; i <= (int)s.size(); i++) {
            long long val = hashFunc(s[i - 1]);
            pref[i] = (pref[i - 1] * base + val) % mod;
        }
        return pref;
    }

    /*
     * Builds prefix hashes for the reversed string. So reversePrefixHashes[i]
     * is hash of reversed prefix i. O(n)
     */
    vector<long long> buildReversePrefixHashes(const string& s) {
        vector<long long> revPref(s.size() + 1, 0LL);
        for (int i = 1; i <= (int)s.size(); i++) {
            long long val = hashFunc(s[s.size() - i]);
            revPref[i] = (revPref[i - 1] * base + val) % mod;
        }
        return revPref;
    }

    /*
     * Precomputes powers of base: base^0, base^1, base^2... up to base^length.
     * O(n)
     */
    vector<long long> precomputeBasePowers(int length) {
        vector<long long> bp(length + 1, 1LL);
        for (int i = 1; i <= length; i++) {
            bp[i] = (bp[i - 1] * base) % mod;
        }
        return bp;
    }

private:
    long long base, mod;
    function<long long(char)> hashFunc;
    vector<long long> prefixHashes, reversePrefixHashes, basePow;
    vector<char> window;
};

class Solution {
public:
    string answerString(const string& word, int numFriends) {
        PalindromeHashing hasher(word);
        if (numFriends == 1) {
            return word;
        }

        int biggestSingleStringLengthAllowed = (int)word.size() - (numFriends - 1);

        auto isWord2Bigger = [&](int L1, int R1, int L2, int R2) {
            int w1 = R1 - L1 + 1;
            int w2 = R2 - L2 + 1;

            int left = 1;
            int right = min(w1, w2);
            int resLongestCommonPrefixSize = 0;

            while (left <= right) {
                int m = (left + right) / 2;
                long long word1Hash = hasher.getHashForSubstring(L1, L1 + m - 1);
                long long word2Hash = hasher.getHashForSubstring(L2, L2 + m - 1);
                if (word1Hash == word2Hash) {
                    resLongestCommonPrefixSize = m;
                    left = m + 1;
                } else {
                    right = m - 1;
                }
            }

            if (resLongestCommonPrefixSize == min(w1, w2)) {
                if (w1 >= w2) {
                    return false;
                }
                return true;
            }

            char nextChar1 = word[L1 + resLongestCommonPrefixSize];
            char nextChar2 = word[L2 + resLongestCommonPrefixSize];
            return (nextChar2 > nextChar1);
        };

        int resL = 0;
        int resR = biggestSingleStringLengthAllowed - 1;

        if (numFriends == 2) {
            for (int size = 1; size <= biggestSingleStringLengthAllowed; size++) {
                int L1Here = 0;
                int R1Here = size - 1;
                if (isWord2Bigger(resL, resR, L1Here, R1Here)) {
                    resL = L1Here;
                    resR = R1Here;
                }
            }
            for (int size = 1; size <= biggestSingleStringLengthAllowed; size++) {
                int L1Here = (int)word.size() - size;
                int R1Here = (int)word.size() - 1;
                if (isWord2Bigger(resL, resR, L1Here, R1Here)) {
                    resL = L1Here;
                    resR = R1Here;
                }
            }
            return word.substr(resL, resR - resL + 1);
        }

        for (int left = 0; left < (int)word.size(); left++) {
            int rr = min(left + biggestSingleStringLengthAllowed - 1, (int)word.size() - 1);
            if (isWord2Bigger(resL, resR, left, rr)) {
                resL = left;
                resR = rr;
            }
        }

        return word.substr(resL, resR - resL + 1);
    }
};