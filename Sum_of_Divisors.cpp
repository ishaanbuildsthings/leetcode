#include<bits/stdc++.h>
using namespace std;

int main() {
    cin.tie(nullptr);
    ios::sync_with_stdio(false);
    long long n; cin >> n;
    int MOD = 1000000000 + 7;
    long long res = 0;
    for (long long fac = 1; fac <= n; fac++) {
        if (fac * fac > n) break;
        // how many numbers are divisible by fac
        long long divByFac = n / fac;
        res += divByFac * fac;

        
    }
}