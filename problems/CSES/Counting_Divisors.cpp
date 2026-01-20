#include<bits/stdc++.h>
using namespace std;

// Solution 1, harmonic series
// int main() {
//     cin.tie(nullptr);
//     ios::sync_with_stdio(false);
//     int n; cin >> n;
//     int MAX_X = 1000000;
//     vector<int> divs(MAX_X + 1);
//     for (int number = 1; number <= MAX_X; number++) {
//         int curr = number;
//         while (curr <= MAX_X) {
//             divs[curr]++;
//             curr += number;
//         }
//     }
//     for (int i = 0; i < n; i++) {
//         int x; cin >> x;
//         cout << divs[x] << endl;
//     }
// }


// Solution 2, SPF and repeated divison, O(X log log X) to build SPF and O(N * (log log X)) for queries
// We can speed up the SPF buil to O(X)
// We can precompute the divisor counts for numbers as well so each query doesn't take log log X
// Queries take log log X because a rough estimate for the # of prime factors with (and without) multiplicity is log log X
// int main() {
//     cin.tie(nullptr);
//     ios::sync_with_stdio(false);
//     int n; cin >> n;
//     int MAX_X = 1000000;
//     vector<int>spf(MAX_X + 1, 0); // spf[num] = smallest prime factor, spf[1] = 0
//     for (int div = 2; div <= MAX_X; div++) {
//         if (spf[div]) continue;
//         spf[div] = div;
//         for (int mult = 2 * div; mult <= MAX_X; mult += div) {
//             if (spf[mult] == 0) {
//                 spf[mult] = div;
//             }
//         }
//     }
//     for (int i = 0; i < n; i++) {
//         int v; cin >> v;
//         int ans = 1; // factor of 1
//         while (v > 1) {
//             int p = spf[v]; // current smallest prime factor, see how many times it occurs
//             int occurs = 0;
//             while (v % p == 0) {
//                 occurs++;
//                 v /= p;
//             }
//             ans *= (occurs + 1);
//         }
//         cout << ans << endl;
//     }
// }

// Solution 3, build SPF in O(X log log X) (can be faster) then precompute div counts from 1 to X
int main() {
    cin.tie(nullptr);
    ios::sync_with_stdio(false);
    int n; cin >> n;
    int MAX_X = 1000000;
    vector<int> spf(MAX_X + 1, 0); // spf[num] -> smallest prime factor
    for (int div = 2; div <= MAX_X; div++) { // could stop at rootX here but then spf[number] -> 0 means it is prime, not itself
        if (spf[div]) continue;
        spf[div] = div;
        for (long long mult = 1LL * div * div; mult <= MAX_X; mult += div) { // div * div optimization here but doesn't change complexity I believe
            if (spf[mult] == 0) {
                spf[mult] = div;
            }
        }
    }

    vector<int> divCount(MAX_X + 1, 1);
    vector<int> spfPower(MAX_X + 1, 0);
    for (int number = 2; number <= MAX_X; number++) {
        int prime = spf[number];
        int reduced = number / prime;
        // if this number only has 1 copy of its smallest prime factor
        if (spf[reduced] != prime) {
            divCount[number] = 2 * divCount[reduced];
            spfPower[number] = 1;
        } else {
            // this number has multiple copies of its smallest prime factor
            spfPower[number] = spfPower[reduced] + 1;
            int old = divCount[reduced] / ( spfPower[reduced] + 1);
            int newFac = old * (spfPower[number] + 1);
            divCount[number] = newFac;
        }
    }

    for (int i = 0; i < n; i++) {
        int x; cin >> x;
        cout << divCount[x] << endl;
    }
}


// 2 * 3 * 2 * 3 = 36

// spf[36] = 2
// divCount[36] = 1 2 3 4 6 9 12 18 36 = 9
// spfPower[36] = 2

// solving for 72
// spf[72] = 2
// spfPower[72] = 3

// we need divisors 36 had before any powers of 2
// current 36 has 3 options for powers of 2: 2^0 2^1 2^2
// and 3 options for powers of 3: 3^0 3^1 3^2
// That forms 3x3 = 9 options
// So before a 2 was introduced we had only (1, 3, 9) as options
// But we are adding on 1*2, 3*2, 9*2 and 1*2^2, 3*2^2, 9*2^2 as options for a total of 9 factors
// Yes the presence of the 2 adds only 6 options, but to go back from 9->3 factors we divide by 3, not 2

