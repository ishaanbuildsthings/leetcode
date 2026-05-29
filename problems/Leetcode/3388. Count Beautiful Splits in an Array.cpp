struct PalindromeHashing {
    vector<int> window;
    int base;
    int mod;
    vector<long long> prefixHashes;
    vector<long long> reversePrefixHashes;
    vector<long long> basePow;

    PalindromeHashing(const vector<int>& arr, int b, int m);
    vector<long long> buildPrefixHashes(const vector<int>& arr);
    vector<long long> buildReversePrefixHashes(const vector<int>& arr);
    vector<long long> precomputeBasePowers(int length);
    long long getHashForSubstring(int left, int right);
    bool isPalindrome(int left, int right);
};

PalindromeHashing::PalindromeHashing(const vector<int>& arr, int b, int m) {
    window = arr;
    base = b;
    mod = m;
    prefixHashes = buildPrefixHashes(arr);
    reversePrefixHashes = buildReversePrefixHashes(arr);
    basePow = precomputeBasePowers((int)arr.size());
}

vector<long long> PalindromeHashing::buildPrefixHashes(const vector<int>& arr) {
    vector<long long> prefix(arr.size() + 1, 0);
    for (int i = 1; i <= (int)arr.size(); i++) {
        long long val = arr[i - 1];
        long long h = (prefix[i - 1] * base + val) % mod;
        prefix[i] = h;
    }
    return prefix;
}

vector<long long> PalindromeHashing::buildReversePrefixHashes(const vector<int>& arr) {
    vector<long long> revPrefix(arr.size() + 1, 0);
    for (int i = 1; i <= (int)arr.size(); i++) {
        long long val = arr[(int)arr.size() - i];
        long long h = (revPrefix[i - 1] * base + val) % mod;
        revPrefix[i] = h;
    }
    return revPrefix;
}

vector<long long> PalindromeHashing::precomputeBasePowers(int length) {
    vector<long long> bp(length + 1, 1);
    for (int i = 1; i <= length; i++) {
        bp[i] = (bp[i - 1] * base) % mod;
    }
    return bp;
}

long long PalindromeHashing::getHashForSubstring(int left, int right) {
    long long h = prefixHashes[right + 1] - (prefixHashes[left] * basePow[right - left + 1] % mod);
    if (h < 0) h += mod;
    return h;
}

bool PalindromeHashing::isPalindrome(int left, int right) {
    int sz = (int)window.size();
    int revLeft = sz - right - 1;
    int revRight = sz - left;
    long long h = reversePrefixHashes[revRight] - (reversePrefixHashes[revLeft] * basePow[revRight - revLeft] % mod);
    if (h < 0) h += mod;
    return getHashForSubstring(left, right) == h;
}

class Solution {
public:
    int beautifulSplits(vector<int>& nums) {
        int n = (int)nums.size();
        int res = 0;
        int MOD = 1000000007;
        PalindromeHashing hasher(nums, 911, MOD);
        for (int allLeft = 0; allLeft < (int)nums.size() - 2; allLeft++) {
            for (int allMidLeft = allLeft + 1; allMidLeft < (int)nums.size() - 1; allMidLeft++) {
                bool succeeded = false;
                int l1 = 0;
                int r1 = allLeft;
                int l2 = r1 + 1;
                int r2 = allMidLeft;
                int l3 = r2 + 1;
                int r3 = n - 1;
                int width1 = r1 - l1 + 1;
                int width2 = r2 - l2 + 1;
                int width3 = r3 - l3 + 1;
                if (width1 > width2 && width2 > width3) {
                    continue;
                }
                if (width1 <= width2) {
                    long long hashLeft = hasher.getHashForSubstring(l1, r1);
                    long long hashMid = hasher.getHashForSubstring(l2, l2 + width1 - 1);
                    if (hashLeft == hashMid) {
                        succeeded = true;
                    }
                }
                if (!succeeded && width2 <= width3) {
                    long long hashMid = hasher.getHashForSubstring(l2, r2);
                    long long hashRight = hasher.getHashForSubstring(l3, l3 + width2 - 1);
                    if (hashMid == hashRight) {
                        succeeded = true;
                    }
                }
                res += (int)succeeded;
            }
        }
        return res;
    }
};