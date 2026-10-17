// SOLUTION 1, INCLUSION EXCLUSION OVER BITMASKS OF PRIMES

// #include <bits/stdc++.h>
// using namespace std;

// int main() {
//     ios::sync_with_stdio(false);
//     cin.tie(nullptr);
//     int n; cin >> n;
//     vector<int> A(n); for (int i = 0; i < n; i++) cin >> A[i];

//     int mx = *max_element(A.begin(), A.end());

//     vector<int> spf(mx + 1, 0);
//     spf[0] = 1;
//     spf[1] = 1;
//     for (int i = 2; i <= mx; i++) {
//         if (spf[i] == 0) {
//             spf[i] = i;
//             for (int mult = i; mult <= mx; mult += i) {
//                 if (spf[mult] == 0) spf[mult] = i;
//             }
//         }
//     }

//     auto primeFactorize = [&](int v) -> vector<pair<int,int>> {
//         vector<pair<int,int>> res; // holds (p1, e1), ...
//         int curr = v;
//         while (curr != 1) {
//             int p = spf[curr];
//             int e = 0;
//             while (curr % p == 0) {
//                 curr /= p;
//                 e++;
//             }
//             // cerr << "pushing p: " << p << " e: " << e << '\n';
//             res.push_back({p, e});
//         }
//         return res;
//     };

   

//     // vector<vector<int>> numToDivs(mx + 1);
//     // for (int fac = 2; fac <= mx; fac++) {
//     //     for (int mult = fac; mult <= mx; mult += fac) {
//     //         numToDivs[mult].push_back(fac);
//     //     }
//     // }

//     vector<int> factorToNumsDivisibleByFactor(mx + 1, 0);
//     for (int i = 0; i < n; i++) {
//         int v = A[i];
//         for (int fac = 1; fac < sqrt(v); fac++) {
//             if (v % fac == 0) {
//                 factorToNumsDivisibleByFactor[fac]++;
//                 factorToNumsDivisibleByFactor[v / fac]++;
//             }
//         }
//         int r = sqrtl(v);
//         bool isSquare = (r * r == v);
//         if (isSquare) {
//             factorToNumsDivisibleByFactor[r]++;
//         }
//     }

//     long long res = 0;
//     for (int i = 0; i < n; i++) {
//         int v = A[i];
//         if (v == 1) {
//             res += n - 1;
//             // cerr << "RES NOW: " << res << " FROM 1" << endl;
//             continue;
//         }
//         // cerr << "-------" << '\n';
//         // cerr << "v: " << v << '\n';
//         auto primeFacs = primeFactorize(v);
//         // how many numbers share a prime factor with this?
//         int shared = 0;
//         int numFacs = primeFacs.size();
//         // cerr << "num facs: " << numFacs << '\n';
//         // cerr << "first fac: " << primeFacs[0].first << '\n';
//         int fmask = (1 << numFacs) - 1;
//         for (int mask = 1; mask <= fmask; mask++) {
//             int parity = __builtin_popcount(mask) & 1; // adding if 1, otherwise subtract
//             int prod = 1;
//             for (int b = 0; b < numFacs; b++) {
//                 if (mask & (1 << b)) {
//                     prod *= primeFacs[b].first;
//                 }
//             }
//             // cerr << "prod: " << prod << '\n';
//             if (parity) {
//                 shared += factorToNumsDivisibleByFactor[prod];
//             } else {
//                 shared -= factorToNumsDivisibleByFactor[prod];
//             }
//         }
//         shared -= 1; // dedupe itself
//         // cerr << "SHARED: " << shared << '\n';
//         int notShared = n - shared - 1;
//         // cerr << "NOT SHARED: " << notShared << '\n';
//         res += notShared;
//         // cerr << "res now: " << res << '\n';
//     }
//     cout << (res / 2) << '\n';

// }


// SOLUTION 2, MOBIUS INVERSION which is # of pairs whose gcd is exactly X
#include<bits/stdc++.h>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n; cin >> n;
    vector<int>A(n); for (int i = 0; i < n; i++) cin >> A[i];
    int mx = *max_element(A.begin(), A.end());
    vector<long long> frq(mx + 1);
    for (int i = 0; i < n; i++) {
        frq[A[i]]++;
    }
    vector<long long> divisBy(mx + 1);
    for (int fac = 1; fac <= mx; fac++) {
        for (int mult = fac; mult <= mx; mult += fac) {
            divisBy[fac] += frq[mult];
        }
    }
    vector<long long> gcdExact(mx + 1);
    for (int fac = mx; fac >= 1; fac--) {
        gcdExact[fac] = divisBy[fac] * (divisBy[fac] - 1) / 2;
        for (int mult = 2 * fac; mult <= mx; mult += fac) {
            gcdExact[fac] -= gcdExact[mult];
        }
    }
    cout << gcdExact[1];
}