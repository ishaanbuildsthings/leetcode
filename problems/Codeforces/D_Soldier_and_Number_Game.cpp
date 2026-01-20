#include <bits/stdc++.h>
using namespace std;

int main() {
    cin.tie(nullptr);
    ios::sync_with_stdio(false);
    int t; cin >> t;

    int MX = 5000000;
    // for each number from 1 to 5,000,000 we need to know the spf, so we can quickly compute the # of prime factors for all numbers
    vector<int> spf(MX + 1, 0); // spf[1] = 0, spf[prime] = prime
    for (int div = 2; div <= MX; div++) {
        if (spf[div]) continue;
        spf[div] = div;
        for (long long mult = 1LL * div * div; mult <= MX; mult += div) {
            if (spf[mult] == 0) {
                spf[mult] = div;
            }
        }
    }

    auto numPrimeFactorsWithMultiplicity = [&](int num) -> int {
        int curr = num;
        int res = 0;
        while (curr > 1) {
            int p = spf[curr];
            res++;
            curr /= p;
        }
        return res;
    };

    vector<int> numPrimeFactorsWithMultiplicityArray(MX + 1);
    for (int num = 0; num <= MX; num++) {
        numPrimeFactorsWithMultiplicityArray[num] = numPrimeFactorsWithMultiplicity(num);
    }

    vector<long long> pf;
    long long curr = 0;
    for (int i = 0; i <= MX; i++) {
        curr += numPrimeFactorsWithMultiplicityArray[i];
        pf.push_back(curr);
    }

    auto query = [&](int l, int r) -> long long {
        if (l > r) {
            return 0;
        }
        if (l == 0) {
            return pf[r];
        }
        return pf[r] - pf[l - 1];
    };

    while (t--) {
        int a, b; cin >> a >> b; // given a!/b!
        // answer is the # of prime factors among all b+1, b+2, ... a
        long long result = query(b + 1, a);
        cout << result << endl;
    }
}