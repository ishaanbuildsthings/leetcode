#include <bits/stdc++.h>
using namespace std;

// returns a z-function array for a string
vector<int> zFunction(string text) {
    vector<int> z(text.size());
    int l = 0;
    int r = 0;
    for (int i = 1; i < text.size(); i++) {
        // if we are inside the zbox, we could re-use some prior z value
        if (i <= r) {
            int k = i - l;
            z[i] = min(r - i + 1, z[k]);
            // if (z[i] == z[k] && z[i] < r - i + 1) continue; // This optional line shows if z[k] was the true minimum, z[i] cannot actually be greater and the code after becomes unnecessary
        }

        int nxt = z[i] + i;
        int pref = z[i];
        while (nxt < text.size() && text[nxt] == text[pref]) {
            z[i]++;
            nxt++;
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
    cin.tie(nullptr);
    ios::sync_with_stdio(false);
    string s; cin >> s;
    auto z = zFunction(s);    
    int n = s.size();

    vector<int> frq(n + 1, 0);
    for (auto x : z) frq[x]++;

    int lessThanSizes = 0;

    int longestPf = -1;
    for (int i = n - 1; i >= 0; i--) {
        int length = n - i;
        lessThanSizes += frq[length - 1];
        if (z[i] < length) continue;
        // how many occurences of length or more exist
        
        int lengthOrMore = n - lessThanSizes;
        if (lengthOrMore >= 2) {
            longestPf = length;
        }
    }
    if (longestPf == -1) {
        cout << "Just a legend";
    } else {
        for (int i = 0; i < longestPf; i++) cout << s[i];
    }
}