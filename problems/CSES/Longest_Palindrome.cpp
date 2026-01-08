#include<bits/stdc++.h>
using namespace std;

const int MAX_N = 1000000;
const long long BASE = 27;
const int MOD = 1000000000 + 7;
int basePowMod[MAX_N]; // base^power % MOD
string s;

void initPow() {
    basePowMod[0] = 1;
    for (int power = 1; power < MAX_N; power++) {
        long long newV = (basePowMod[power - 1] * BASE) % MOD;
        basePowMod[power] = newV;
    }
}

vector<long long> buildPfHash(string s) {
    vector<long long> pfHash;
    long long hash = 0;
    for (auto c : s) {
        int coeff = c - 'a' + 1;
        hash *= BASE;
        hash += coeff;
        hash %= MOD;
        pfHash.push_back(hash);
    }
    return pfHash;
};

long long getHash(int l, int r, vector<long long>& pfHash) {
    long long rightHash = pfHash[r];
    long long leftHash = l != 0 ? pfHash[l - 1] : 0;
    long long leftShifted = (leftHash * basePowMod[r - l + 1]) % MOD;
    long long newHash = rightHash - leftShifted;
    if (newHash < 0) {
        newHash += MOD;
    }
    return newHash;
};


// 1 |2 0 2| 3 4 5 6 7
//    < < <
long long getRevHash(int l, int r, vector<long long>& revHash) {
    int n = s.size();
    int r2 = n - l - 1;
    int l2 = n - r - 1;
    // cout << "rev hash l and r: " << l2 << " " << r2 << endl;
    return getHash(l2, r2, revHash);
};

int main() {
    initPow();
    cin.tie(nullptr);
    ios::sync_with_stdio(false);
    cin >> s;
    string rev = s;
    reverse(rev.begin(), rev.end());
    auto pfHash = buildPfHash(s);
    auto revHash = buildPfHash(rev);
    int L = -1;
    int R = -1;
    // odd length palindromes
    for (int i = 0; i < s.size(); i++) {
        int leftWings = i;
        int rightWings = s.size() - i - 1;
        int maxWings = min(leftWings, rightWings);
        // binary search
        int left = 0;
        int right = maxWings;
        int L2 = -1;
        int R2 = -1;
        while (left <= right) {
            int m = (left + right) / 2;
            int left2 = i - m;
            int right2 = i + m;
            if (getHash(left2, right2, pfHash) == getRevHash(left2, right2, revHash)) {
                L2 = left2;
                R2 = right2;
                left = m + 1;
            } else {
                right = m - 1;
            }
        }
        int nsize = R2 - L2 + 1;
        if (nsize >= (R - L + 1)) {
            L = L2;
            R = R2;
        }
    }
    // even length palindromes
    for (int i = 0; i < s.size() - 1; i++) {
        if (s[i] != s[i + 1]) {
            continue;
        }
        int leftWings = i;
        int rightWings = s.size() - i - 2;
        int maxWings = min(leftWings, rightWings);
        // binary search
        int left = 0;
        int right = maxWings;
        int L2 = -1;
        int R2 = -1;
        while (left <= right) {
            int m = (right + left) / 2;
            int left2 = i - m;
            int right2 = i + m + 1;
            if (getHash(left2, right2, pfHash) == getRevHash(left2, right2, revHash)) {
                L2 = left2;
                R2 = right2;
                left = m + 1;
            } else {
                right = m - 1;
            }
        }
        int nsize = R2 - L2 + 1;
        if (nsize >= (R - L + 1)) {
            L = L2;
            R = R2;
        }
    }
    for (int i = L; i <= R; i++) {
        cout << s[i];
    }
}