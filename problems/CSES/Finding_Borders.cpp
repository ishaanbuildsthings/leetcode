// // Soluition 1, rolling hash
// #include<bits/stdc++.h>
// using namespace std;

// const int BASE = 26;
// const int MOD = 1000000000 + 7;
// const int MAX_N = 1000000 + 5;
// long long basePowMod[MAX_N];

// void initPow() {
//     basePowMod[0] = 1;
//     for (int power = 1; power < MAX_N; power++) {
//         long long newPow = (basePowMod[power - 1] * BASE) % MOD;
//         basePowMod[power] = newPow;
//     }
// }

// struct Hasher {
//     long long hashVal = 0;
//     int windowSize = 0;
//     void addRight(char c) {
//         hashVal *= BASE;
//         hashVal += c - 'a';
//         hashVal %= MOD;
//         windowSize++;
//     }

//     int size() { return windowSize; }
//     long long hash() { return hashVal; }

//     void addLeft(char c) {
//         int power = size();
//         long long contribution = ((c - 'a') * basePowMod[power]) % MOD;
//         hashVal += contribution;
//         hashVal %= MOD;
//         windowSize++;
//     }
// };

// int main() {
//     ios::sync_with_stdio(false);
//     cin.tie(nullptr);
//     initPow();
//     string s;
//     cin >> s;
//     int n = s.size();
//     Hasher h1, h2;
//     int out = 0;
//     for (int i = 0; i < n - 1; i++) {
//         h1.addRight(s[i]);
//         h2.addLeft(s[n - i - 1]);
//         if (h1.hash() == h2.hash()) {
//             cout << i + 1 << " ";
//         }
//         out += h1.hash() == h2.hash();
//     }
// }

// Solution 2, z-function
#include <bits/stdc++.h>
using namespace std;

vector<int> zFunc(string text) {
    int n = text.size();
    vector<int> z(n);
    int l = 0;
    int r = 0;
    for (int i = 1; i < n; i++) {
        if (i <= r) {
            int k = i - l;
            z[i] = min(z[k], r - i + 1);
        }
        int nxt = i + z[i];
        int pref = z[i];
        while (nxt < n && text[nxt] == text[pref]) {
            z[i]++;
            nxt++;
            pref++;
        }
        if (nxt - 1 >= r) {
            l = i;
            r = nxt - 1;
        }
    }
    return z;
}

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    string s; cin >> s;
    auto z = zFunc(s);
    int n = s.size();
    for (int i = n - 1; i > 0; i--) {
        if (z[i] == n - i) {
            cout << n - i << " ";
        }
    }
}