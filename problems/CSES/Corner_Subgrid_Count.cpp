#include <bits/stdc++.h>
using namespace std;
#pragma GCC target("popcnt")

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    vector<bitset<3000>> bs;
    int n; cin >> n;
    for (int i = 0; i < n; i++) {
        string s; cin >> s; bs.emplace_back(s);
    }
    long long out = 0;
    for (int r1 = 0; r1 < n; r1++) {
        for (int r2 = r1 + 1; r2 < n; r2++) {
            bitset<3000> AND = bs[r1] & bs[r2];
            int count =  AND.count();
            out += (count * (count - 1)) / 2;
        }
    }
    cout << out << '\n';
}


