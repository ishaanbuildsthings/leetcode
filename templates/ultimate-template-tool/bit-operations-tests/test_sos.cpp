// Stress tests the SOS DP and convolution templates against brute force.
// Run: g++ -O2 -std=c++17 test_sos.cpp -o /tmp/ts && /tmp/ts
#include "../bit-operations/subsetSums.cpp"
#include "../bit-operations/supersetSums.cpp"
#include "../bit-operations/countSubsetsByAnd.cpp"
#include "../bit-operations/countSubsetsByOr.cpp"
#include "../bit-operations/countPairsByAnd.cpp"
#include "../bit-operations/countPairsByOr.cpp"
#include "../bit-operations/orConvolution.cpp"
#include "../bit-operations/andConvolution.cpp"
#include "../bit-operations/xorConvolution.cpp"
#include "../bit-operations/xorConvolutionMod.cpp"
#include "../bit-operations/countPairsByXor.cpp"

mt19937_64 rng(2);
long long rnd(long long lo, long long hi) { return lo + (long long)(rng() % (unsigned long long)(hi - lo)); }
#define CHECK(c) if (!(c)) { cerr << "FAIL line " << __LINE__ << ": " #c << endl; exit(1); }
using vl = vector<long long>;

int main() {
    for (int it = 0; it < 600; it++) {
        int B = rnd(0, 7), n = 1 << B;
        vector<long long> f(n), g(n);
        for (auto& x : f) x = rnd(-50, 50);
        for (auto& x : g) x = rnd(-50, 50);
        vl sub(n, 0), sup(n, 0), orC(n, 0), andC(n, 0), xorC(n, 0);
        for (int m = 0; m < n; m++) {
            for (int s = 0; s < n; s++) {
                if ((s & m) == s) sub[m] += f[s];
                if ((s & m) == m) sup[m] += f[s];
            }
        }
        for (int i = 0; i < n; i++) {
            for (int j = 0; j < n; j++) {
                orC[i | j] += f[i] * g[j];
                andC[i & j] += f[i] * g[j];
                xorC[i ^ j] += f[i] * g[j];
            }
        }
        CHECK(subsetSums(f) == sub);
        CHECK(supersetSums(f) == sup);
        CHECK(orConvolution(f, g) == orC);
        CHECK(andConvolution(f, g) == andC);
        CHECK(xorConvolution(f, g) == xorC);
        for (long long mod : {7LL, 1'000'000'007LL, 1LL, (1LL << 61) - 1}) {
            vl want(n);
            for (int i = 0; i < n; i++) want[i] = ((xorC[i] % mod) + mod) % mod;
            CHECK(xorConvolutionMod(f, g, mod) == want);
        }
        vector<int> arr(rnd(0, 9));
        int hi = vector<int>{1, 2, 5, 16, 40}[rnd(0, 5)];
        int mx = 0;
        for (auto& x : arr) { x = rnd(0, hi); mx = max(mx, x); }
        int m = 1;
        while (m <= mx) m <<= 1;
        vl pa(m, 0), po(m, 0), px(m, 0);
        for (size_t i = 0; i < arr.size(); i++) {
            for (size_t j = i + 1; j < arr.size(); j++) {
                pa[arr[i] & arr[j]]++;
                po[arr[i] | arr[j]]++;
                px[arr[i] ^ arr[j]]++;
            }
        }
        CHECK(countPairsByAnd(arr) == pa);
        CHECK(countPairsByOr(arr) == po);
        CHECK(countPairsByXor(arr) == px);
        for (long long mod : {1'000'000'007LL, 5LL}) {
            vl sa(m, 0), so(m, 0);
            for (int mask = 1; mask < (1 << arr.size()); mask++) {
                int a = -1, o = 0;
                for (size_t i = 0; i < arr.size(); i++) {
                    if (mask >> i & 1) { a &= arr[i]; o |= arr[i]; }
                }
                sa[a]++;
                so[o]++;
            }
            for (auto& x : sa) x %= mod;
            for (auto& x : so) x %= mod;
            CHECK(countSubsetsByAnd(arr, mod) == sa);
            CHECK(countSubsetsByOr(arr, mod) == so);
        }
    }
    bool threw = false;
    try { subsetSums(vector<int>{1, 2, 3}); } catch (const invalid_argument&) { threw = true; }
    CHECK(threw);
    threw = false;
    try { xorConvolutionMod(vector<int>{1, 2}, vector<int>{3, 4}, 10); } catch (const invalid_argument&) { threw = true; }
    CHECK(threw);
    // a big one: 2^20 entries runs fast and the convolution of counts stays exact
    vector<int> big(200000);
    for (auto& x : big) x = rnd(0, 1 << 20);
    auto t0 = chrono::steady_clock::now();
    auto pairs = countPairsByXor(big);
    long long total = accumulate(pairs.begin(), pairs.end(), 0LL);
    CHECK(total == 200000LL * 199999 / 2);
    auto ms = chrono::duration_cast<chrono::milliseconds>(chrono::steady_clock::now() - t0).count();
    cout << "c++ sos tests passed (countPairsByXor on 2e5 values < 2^20: " << ms << " ms)" << endl;
}
