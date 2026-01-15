#include <bits/stdc++.h>
using namespace std;

int main() {
    cin.tie(nullptr);
    ios::sync_with_stdio(false);
    int ppl, wt; cin >> ppl >> wt;
    vector<int> wts(ppl); for (int i = 0; i < ppl; i++) cin >> wts[i];
    sort(wts.begin(), wts.end());
    int i = 0;
    int j = wts.size() - 1;
    int out = 0;
    while (i <= j) {
        if (wts[i] + wts[j] <= wt) {
            out++;
            i++;
            j--;
            continue;
        } else {
            j--;
            out++;
            continue;
        }
    }
    cout << out << endl;
}