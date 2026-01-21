// Solution 1, use deterministic rabin miller to quickly prime check in logN, increment and test all
// #include <bits/stdc++.h>
// using namespace std;

// // TEMPLATE BY ishaanbuildsthings on github
// using namespace std;

// using __int128_t = __int128_t;

// // (a*b) % mod without overflow
// long long modMul(long long a, long long b, long long mod) {
//     return (long long)((__int128)a * b % mod);
// }

// long long modPow(long long a, long long e, long long mod) {
//     long long r = 1 % mod;
//     a %= mod;
//     while (e > 0) {
//         if (e & 1) r = modMul(r, a, mod);
//         a = modMul(a, a, mod);
//         e >>= 1;
//     }
//     return r;
// }

// bool _checkBase(long long n, long long a, long long d, int s) {
//     long long x = modPow(a, d, n);
//     if (x == 1 || x == n - 1) return true;
//     for (int i = 1; i < s; i++) {
//         x = modMul(x, x, n);
//         if (x == n - 1) return true;
//     }
//     return false;
// }

// // Deterministic miller rabin for long long to check if it is prime, O(B * logN), it uses that weird fermat theorem remainder thing, B = 7 for long long
// bool isPrimeLL(long long n) {
//     if (n < 2) return false;
//     for (long long p : {2,3,5,7,11,13,17,19,23,29,31,37}) {
//         if (n == p) return true;
//         if (n % p == 0) return false;
//     }

//     long long d = n - 1;
//     int s = 0;
//     while ((d & 1) == 0) { d >>= 1; s++; }

//     // deterministic for 64-bit
//     for (long long a : {2LL, 325LL, 9375LL, 28178LL, 450775LL, 9780504LL, 1795265022LL}) {
//         if (a % n == 0) return true;
//         if (!_checkBase(n, a, d, s)) return false;
//     }
//     return true;
// }

// // Deterministic miller rabin for long long to check if it is prime, O(B * logN), it uses that weird fermat theorem remainder thing, B = 5 for int
// bool isPrimeInt(int n) {
//     if (n < 2) return false;
//     for (int p : {2,3,5,7,11,13,17,19,23,29,31,37}) {
//         if (n == p) return true;
//         if (n % p == 0) return false;
//     }

//     long long N = n;
//     long long d = N - 1;
//     int s = 0;
//     while ((d & 1) == 0) { d >>= 1; s++; }

//     // enough for 32-bit
//     for (long long a : {2LL, 3LL, 5LL, 7LL, 11LL}) {
//         if (a % N == 0) return true;
//         if (!_checkBase(N, a, d, s)) return false;
//     }
//     return true;
// }


// int main() {
//     ios::sync_with_stdio(false);
//     cin.tie(nullptr);
//     int t; cin >> t;
//     while (t--) {
//         long long n; cin >> n;
//         long long v = n + 1;
//         while (true) {
//             if (isPrimeLL(v)) {
//                 cout << v << endl;
//                 break;
//             }
//             v++;
//         }
//     }
// }

// Solution 2, build a segmented sieve from N:N+2000 and locate the first prime
#include <bits/stdc++.h>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    long long MAX_VALUE = 1000000000000;
    // Build the sieve from 1 to root MAX_VALUE to get those primes
    // Build a second sieve for n:n+2000 which we need to mark
    // For each number in root MAX_VALUE we mark all factors in n:n+2000
    // This takes root MAX_VALUE time * 2000 per test
    long long MX = ((long long) sqrt(MAX_VALUE)) + 5;
    vector<int> isPrime(MX, 1);
    isPrime[0] = 0;
    isPrime[1] = 0;
    for (int div = 2; div < MX; div++) {
        if (!isPrime[div]) continue;
        for (long long mult = 1LL * div * div; mult < MX; mult += div) {
            isPrime[mult] = 0;
        }
    }
    vector<int> primes;
    for (int number = 0; number < MX; number++) {
        if (isPrime[number]) {
            primes.push_back(number);
        }
    }
    int t; cin >> t;
    while (t--) {
        long long n; cin >> n;
        // say n=100
        // we are at prime=3
        // fulls is 33
        // start is 99
        // now start is 102
        vector<long long> segSieve(2000, 1); // segSieve[i] = 1 means n+i is prime, so n...n+1999 is in range
        for (int prime : primes) {
            long long fulls = n / prime;
            long long start = fulls * prime;
            if (start < n) {
                start += prime;
            }
            // Annoying edge case I missed
            if (start == prime) {
                start *= 2;
            }
            while (start <= n + 1999) {
                segSieve[start - n] = 0;
                start += prime;
            }
        }

        for (long long number = n + 1; number < n + 2000; number++) {
            if (segSieve[number - n] == 1) {
                cout << number << endl;
                break;
            }
        }
    }
}