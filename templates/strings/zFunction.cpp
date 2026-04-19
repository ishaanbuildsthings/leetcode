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