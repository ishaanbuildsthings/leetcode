// TEMPLATE BY ishaanbuildsthings on github

using namespace std;

using __int128_t = __int128_t;

// (a*b) % mod without overflow
long long modMul(long long a, long long b, long long mod) {
    return (long long)((__int128)a * b % mod);
}

long long modPow(long long a, long long e, long long mod) {
    long long r = 1 % mod;
    a %= mod;
    while (e > 0) {
        if (e & 1) r = modMul(r, a, mod);
        a = modMul(a, a, mod);
        e >>= 1;
    }
    return r;
}

bool _checkBase(long long n, long long a, long long d, int s) {
    long long x = modPow(a, d, n);
    if (x == 1 || x == n - 1) return true;
    for (int i = 1; i < s; i++) {
        x = modMul(x, x, n);
        if (x == n - 1) return true;
    }
    return false;
}

// Deterministic miller rabin for long long to check if it is prime, O(logN), it uses that weird fermat theorem remainder thing
bool isPrimeLL(long long n) {
    if (n < 2) return false;
    for (long long p : {2,3,5,7,11,13,17,19,23,29,31,37}) {
        if (n == p) return true;
        if (n % p == 0) return false;
    }

    long long d = n - 1;
    int s = 0;
    while ((d & 1) == 0) { d >>= 1; s++; }

    // deterministic for 64-bit
    for (long long a : {2LL, 325LL, 9375LL, 28178LL, 450775LL, 9780504LL, 1795265022LL}) {
        if (a % n == 0) return true;
        if (!_checkBase(n, a, d, s)) return false;
    }
    return true;
}

// Deterministic miller rabin for long long to check if it is prime, O(logN), it uses that weird fermat theorem remainder thing
bool isPrimeInt(int n) {
    if (n < 2) return false;
    for (int p : {2,3,5,7,11,13,17,19,23,29,31,37}) {
        if (n == p) return true;
        if (n % p == 0) return false;
    }

    long long N = n;
    long long d = N - 1;
    int s = 0;
    while ((d & 1) == 0) { d >>= 1; s++; }

    // enough for 32-bit
    for (long long a : {2LL, 3LL, 5LL, 7LL, 11LL}) {
        if (a % N == 0) return true;
        if (!_checkBase(N, a, d, s)) return false;
    }
    return true;
}
