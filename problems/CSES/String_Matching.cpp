#include<bits/stdc++.h>
using namespace std;

const int BASE = 26;
const int MOD = 998244353;
const int MAX_N = 1000000 + 5;
long long basePowMod[MAX_N]; // basePowMod[power] is (base ^ power) % MOD

void initPows() {
    basePowMod[0] = 1;
    for (int power = 1; power < MAX_N; power++) {
        basePowMod[power] = (basePowMod[power - 1] * BASE) % MOD;
    }
};

struct Hasher {
    long long windowHash = 0; // current hash value
    int windowSize = 0;

    void add(char c) {
        windowHash *= BASE;
        windowHash += c - 'a';
        windowHash %= MOD;
        windowSize++;
    };
    
    long long getHash() {
        return windowHash;
    }
    
    int getSize() {
        return windowSize;
    }
    
    void popLeft(char c) {
        int leftPower = getSize() - 1;
        long long leftContribution = ((c - 'a') * basePowMod[leftPower]) % MOD;
        windowHash -= leftContribution;
        if (windowHash < 0) windowHash += MOD;
        windowSize--;
    }
};


int main() {
    initPows();

    string haystack;
    cin >> haystack;
    string needle;
    cin >> needle;
    int n = (int)haystack.size();
    int m = (int)needle.size();
    if (m > n) {
        cout << 0 << "\n";
        return 0;
    }

    Hasher haystackHasher, needleHasher;
    for (int i = 0; i < m; i++) {
        haystackHasher.add(haystack[i]);
        needleHasher.add(needle[i]);
    }

    long long needleHash = needleHasher.getHash();
    int out = haystackHasher.getHash() == needleHash ? 1 : 0;
    for (int r = m; r < n; r++) {
        haystackHasher.add(haystack[r]);
        haystackHasher.popLeft(haystack[r-m]);
        if (haystackHasher.getHash() == needleHash) {
            out++;
        }
    }
    cout << out << "\n";
}