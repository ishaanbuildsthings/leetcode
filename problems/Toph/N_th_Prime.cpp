#include <bits/stdc++.h>
using namespace std;

int main() {
    int n; cin >> n;
    vector<bool> isPrime(100000000, true);
    isPrime[0] = false;
    isPrime[1] = false;
    for (int div = 2; div < 100000000; div++) {
        if (isPrime[div] == false) continue;
        for (long long mult = 1LL * div * div; mult < 100000000; mult += div) {
            isPrime[mult] = false;
        }
    }
    int seen = 0;
    for (int number = 1; number < 100000000; number++) {
        if (isPrime[number]) seen++;
        if (seen == n) {
            cout << number;
            return 0;
        }
    }
}