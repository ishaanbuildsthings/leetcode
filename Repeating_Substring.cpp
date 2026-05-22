#include <bits/stdc++.h>
using namespace std;
using ll = long long;

const ll BASE = 911;
const ll MOD = 999999527;
const ll MAX_N = 100000;
ll basePow[MAX_N + 1];

struct Hasher {
    ll hashVal = 0;
    ll size = 0;

    ll getHash() { return hashVal; }
    void addRight(char c) {
        ll coeff = c - 'a' + 1;
        hashVal *= BASE;
        hashVal += coeff;
        hashVal %= MOD;
        size++;
    }
    void popLeft(char c) {
        ll leftPow = size - 1;
        ll coeff = c - 'a' + 1;
        ll lost = (coeff * basePow[leftPow]) % MOD;
        hashVal -= lost;
        if (hashVal < 0) hashVal += MOD;
        size--;
    }
};

void init() {
    basePow[0] = 1;
    for (int p = 1; p <= MAX_N; p++) {
        ll npow = (basePow[p - 1] * BASE) % MOD;
        basePow[p] = npow;
    }
}

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    init();
    int resL = -1;
    int resR = -1;
    string s; cin >> s;
    int n = s.size();

    int l = 1;
    int r = n;
    while (l <= r) {
        int m = (l + r) / 2;
        // cerr << "length: " << m << endl;
        Hasher h;
        set<ll> seenHashes;
        for (int right = 0; right < m; right++) {
            h.addRight(s[right]);
        }
        int found = 0;
        seenHashes.insert(h.getHash());
        for (int right = m; right < n; right++) {
            h.addRight(s[right]);
            h.popLeft(s[right - m]);
            if (seenHashes.count(h.getHash())) {
                resL = right - m + 1;
                resR = right;
                found = 1;
            }
            seenHashes.insert(h.getHash());
        }
        if (found) {
            l = m + 1;
        } else {
            r = m - 1;
        }

    }
    if (resL == -1) {
        cout << -1 << endl;
    } else {
        for (int i = resL; i <= resR; i++) cout << s[i];
    }
}