#include<bits/stdc++.h>
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
            nxt++;
            z[i]++;
            pref++;
        }
        if (nxt - 1 > r) {
            l = i;
            r = nxt - 1;
        }
    }
    return z;
};

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    string s; cin >> s;
    int n = s.size();
    auto z = zFunc(s);
    for (int size = 1; size <= n; size++) {
        bool failFound = false;
        for (int j = size; j < n; j += size) {
            int remain = min(size, n - j);
            int zVal = z[j];
            if (zVal < remain) {
                failFound = true;
                break;
            }
        }
        if (!failFound) {
            cout << size << " ";
        }
    }
}