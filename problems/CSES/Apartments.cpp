#include <bits/stdc++.h>
using namespace std;

int main() {
    cin.tie(nullptr);
    ios::sync_with_stdio(false);
    int numPpl, numApt, maxDiff; cin >> numPpl >> numApt >> maxDiff;
    vector<int> desires(numPpl); for (int i = 0; i < numPpl; i++) cin >> desires[i];
    vector<int> apts(numApt); for (int i = 0; i < numApt; i++) cin >> apts[i];
    sort(apts.begin(), apts.end());
    sort(desires.begin(), desires.end());
    int i = desires.size() - 1;
    int j = apts.size() - 1;
    int out = 0;
    while (j >= 0 && i >= 0) {
        int desireSurplus = desires[i] - apts[j];
        if (desireSurplus > maxDiff) {
            i--;
            continue;
        }
        if (desireSurplus < -maxDiff) {
            j--;
            continue;
        }
        out++;
        i--;
        j--;
    }
    cout << out;
}