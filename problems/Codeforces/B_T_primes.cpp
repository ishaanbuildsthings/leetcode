#include <bits/stdc++.h>
using namespace std;

static long long isqrtll(long long x) {
    long long r = (long long) sqrtl((long double)x);
    while ((__int128)(r + 1) * (r + 1) <= x) r++;
    while ((__int128)r * r > x) r--;
    return r;
}
static bool isPerfectSquare(long long x) {
    if (x < 0) return false;
    long long r = isqrtll(x);
    return (__int128)r * r == x;
}

int main() {
    cin.tie(nullptr);
    ios::sync_with_stdio(false);
    int n; cin >> n;
    vector<long long> A(n); for (int i = 0; i < n; i++) cin >> A[i];
    long long mx = *max_element(A.begin(), A.end());
    long long ROOT = sqrt(mx) + 5;
    vector<int> isPrime(ROOT, 1); // 1 means it is prime
    isPrime[0] = 0;
    isPrime[1] = 0;
    for (long long div = 2; div < ROOT; div++) {
        if (!isPrime[div]) continue;
        for (long long mult = div * div; mult < ROOT; mult += div) {
            isPrime[mult] = 0;
        }
    }
    for (auto x : A) {
        if (isPerfectSquare(x) && isPrime[isqrtll(x)]) {
            cout << "YES" << endl;
        } else {
            cout << "NO" << endl;
        }
    }
}