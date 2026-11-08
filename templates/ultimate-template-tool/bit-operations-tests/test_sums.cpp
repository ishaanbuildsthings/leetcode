// Stress tests the pair / subarray bit-sum templates against brute force.
// Run: g++ -O2 -std=c++17 test_sums.cpp -o /tmp/tsum && /tmp/tsum
#include "../bit-operations/sumOfPairXors.cpp"
#include "../bit-operations/sumOfPairAnds.cpp"
#include "../bit-operations/sumOfPairOrs.cpp"
#include "../bit-operations/sumOfSubarrayXors.cpp"
#include "../bit-operations/sumOfSubarrayAnds.cpp"
#include "../bit-operations/sumOfSubarrayOrs.cpp"
#include "../bit-operations/sumOfPairXorsMod.cpp"
#include "../bit-operations/sumOfPairAndsMod.cpp"
#include "../bit-operations/sumOfPairOrsMod.cpp"
#include "../bit-operations/sumOfSubarrayXorsMod.cpp"
#include "../bit-operations/sumOfSubarrayAndsMod.cpp"
#include "../bit-operations/sumOfSubarrayOrsMod.cpp"

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
        CHECK(sumOfPairXors(arr) == (long long)px);
        CHECK(sumOfPairAnds(arr) == (long long)pa);
        CHECK(sumOfPairOrs(arr) == (long long)po);
        CHECK(sumOfSubarrayXors(arr) == (long long)sx);
        CHECK(sumOfSubarrayAnds(arr) == (long long)sa);
        CHECK(sumOfSubarrayOrs(arr) == (long long)so);
        for (long long mod : {1'000'000'007LL, 7LL, 1LL, (1LL << 61) - 1}) {
            CHECK(sumOfPairXorsMod(arr, mod) == (long long)(px % mod));
            CHECK(sumOfPairAndsMod(arr, mod) == (long long)(pa % mod));
            CHECK(sumOfPairOrsMod(arr, mod) == (long long)(po % mod));
            CHECK(sumOfSubarrayXorsMod(arr, mod) == (long long)(sx % mod));
            CHECK(sumOfSubarrayAndsMod(arr, mod) == (long long)(sa % mod));
            CHECK(sumOfSubarrayOrsMod(arr, mod) == (long long)(so % mod));
        }
    }
    vector<long long> big(200000, (1LL << 62) - 1);
    big[0] = 0;
    bool threw = false;
    try { sumOfPairXors(big); } catch (const overflow_error&) { threw = true; }
    CHECK(threw);
    CHECK(sumOfPairXors(vector<int>{1, 2, 3}) == 6);
    cout << "c++ sums tests passed" << endl;
}
