#include<bits/stdc++.h>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int MX = 10000000;
    vector<int> spf(MX + 1); // spf[1] = 0, spf[prime] = prime
    spf[0] = 0; spf[1] = 0;
    for (int num = 2; num <= MX; num++) {
        if (spf[num]) continue;
        spf[num] = num;
        for (long long mult = 1LL * num * num; mult <= MX; mult += num) {
            if (spf[mult] == 0) spf[mult] = num;
        }
    }
    auto facSum = [&](int num) -> long long {
        int curr = num;
        long long out = 1;
        while (curr > 1) {
            int p = spf[curr];
            int geoSum = 1;
            int currPrimeToPow = 1;
            while (curr % p == 0) {
                curr /= p;
                currPrimeToPow *= p;
                geoSum += currPrimeToPow;
            }
            out *= geoSum;
        }
        return out;
    };
    vector<int> earlySum(MX + 1, -1);
    for (int number = 1; number <= MX; number++) {
        auto numFacSum = facSum(number);
        if (numFacSum <= MX && earlySum[numFacSum] == -1) {
            earlySum[numFacSum] = number;
        }
    }
    int t; cin >> t;
    while (t--) {
        int c; cin >> c;
        cout << earlySum[c] << '\n';
    }
}