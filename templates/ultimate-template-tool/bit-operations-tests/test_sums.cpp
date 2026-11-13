// Stress tests the pair / subarray bit-sum templates against brute force.
// Run: g++ -O2 -std=c++17 test_sums.cpp -o /tmp/tsum && /tmp/tsum
#include "../bit-operations/sumOfPairXORs.cpp"
#include "../bit-operations/sumOfPairANDs.cpp"
#include "../bit-operations/sumOfPairORs.cpp"
#include "../bit-operations/sumOfSubarrayXORs.cpp"
#include "../bit-operations/sumOfSubarrayANDs.cpp"
#include "../bit-operations/sumOfSubarrayORs.cpp"
#include "../bit-operations/sumOfPairXORsMod.cpp"
#include "../bit-operations/sumOfPairANDsMod.cpp"
#include "../bit-operations/sumOfPairORsMod.cpp"
#include "../bit-operations/sumOfSubarrayXORsMod.cpp"
#include "../bit-operations/sumOfSubarrayANDsMod.cpp"
#include "../bit-operations/sumOfSubarrayORsMod.cpp"

mt19937_64 rng(3);
#define CHECK(c) if (!(c)) { cerr << "FAIL line " << __LINE__ << ": " #c << endl; exit(1); }

int main() {
    vector<long long> his = {1, 2, 8, 1000, 1LL << 40};
    for (int it = 0; it < 3000; it++) {
        long long hi = his[rng() % his.size()];
        vector<long long> arr(rng() % 12);
        for (auto& x : arr) x = rng() % hi;
        int n = arr.size();
        __int128 px = 0, pa = 0, po = 0, sx = 0, sa = 0, so = 0;
        for (int i = 0; i < n; i++) {
            for (int j = i + 1; j < n; j++) {
                px += arr[i] ^ arr[j];
                pa += arr[i] & arr[j];
                po += arr[i] | arr[j];
            }
            long long x = 0, a = -1, o = 0;
            for (int j = i; j < n; j++) {
                x ^= arr[j];
                a &= arr[j];
                o |= arr[j];
                sx += x;
                sa += a;
                so += o;
            }
        }
        CHECK(sumOfPairXORs(arr) == (long long)px);
        CHECK(sumOfPairANDs(arr) == (long long)pa);
        CHECK(sumOfPairORs(arr) == (long long)po);
        CHECK(sumOfSubarrayXORs(arr) == (long long)sx);
        CHECK(sumOfSubarrayANDs(arr) == (long long)sa);
        CHECK(sumOfSubarrayORs(arr) == (long long)so);
        for (long long mod : {1'000'000'007LL, 7LL, 1LL, (1LL << 61) - 1}) {
            CHECK(sumOfPairXORsMod(arr, mod) == (long long)(px % mod));
            CHECK(sumOfPairANDsMod(arr, mod) == (long long)(pa % mod));
            CHECK(sumOfPairORsMod(arr, mod) == (long long)(po % mod));
            CHECK(sumOfSubarrayXORsMod(arr, mod) == (long long)(sx % mod));
            CHECK(sumOfSubarrayANDsMod(arr, mod) == (long long)(sa % mod));
            CHECK(sumOfSubarrayORsMod(arr, mod) == (long long)(so % mod));
        }
    }
    vector<long long> big(200000, (1LL << 62) - 1);
    big[0] = 0;
    bool threw = false;
    try { sumOfPairXORs(big); } catch (const overflow_error&) { threw = true; }
    CHECK(threw);
    CHECK(sumOfPairXORs(vector<int>{1, 2, 3}) == 6);
    cout << "c++ sums tests passed" << endl;
}
