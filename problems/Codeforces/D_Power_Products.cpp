#include <bits/stdc++.h>
using namespace std;

// Something I stole from online lol
struct MyVecPairHash {
    size_t operator()(const vector<pair<int,int>>& vec) const noexcept {
        size_t h = 0;
        for (const auto& pr : vec) {
            size_t a = std::hash<int>{}(pr.first);
            size_t b = std::hash<int>{}(pr.second);

            // mix a and b into one number
            size_t combined = a ^ (b + 0x9e3779b97f4a7c15ULL + (a<<6) + (a>>2));

            // mix combined into h
            h ^= combined + 0x9e3779b97f4a7c15ULL + (h<<6) + (h>>2);
        }
        return h;
    }
};


// For a * b = x^k every prime factor must occur a multiple of k times
// For example if k=3
// 2^6 * 5^3 can be written as (2^2)^3 * 5^3 = 4^3 * 5^3 = 20^3
// If a prime ever does not have a power divisible by k we cannot re-express it
// So store numbers with their prime details mod K
// If we have a number with 2^4 we record (2, 1) remainder, and we can pair this with anything with 2 remainder
int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n, k; cin >> n >> k;
    vector<int> A(n); for (int i = 0; i < n; i++) cin >> A[i];
    int MAX_V = 100000;
    vector<int> spf(MAX_V + 1, 0); // spf[1] = 0, spf[prime] = prime
    for (int div = 2; div <= MAX_V; div++) {
        if (spf[div]) continue;
        spf[div] = div;
        for (long long mult = 1LL * div * div; mult <= MAX_V; mult += div) {
            if (spf[mult] == 0) spf[mult] = div;
        }
    }
    // 10 -> [(2, 1), (5, 1)] AFTER the removing K, so if k=3 and a power occurs 4 times, we give a power of 1
    auto primeFactorizeKRemainder = [&](int x) -> vector<pair<int,int>> {
        vector<pair<int,int>> primesWithE;
        int curr = x;
        while (curr > 1) {
            int p = spf[curr];
            int e = 0;
            while (curr % p == 0) {
                e++;
                curr /= p;
            }
            int remain = e % k;
            if (remain) {
                primesWithE.push_back({p, remain});
            }
        }
        return primesWithE;
    };

    long long out = 0;

    unordered_map<vector<pair<int,int>>, int, MyVecPairHash> frq; // maps the vector of pairs to a frequency

    for (int i = 0; i < n; i++) {
        int num = A[i];
        auto primes = primeFactorizeKRemainder(num);
        vector<pair<int,int>> inverted;
        for (auto [p, e] : primes) {
            inverted.push_back({p, k - e});
        }
        out += frq[inverted];
        frq[primes] += 1;
    }

    cout << out;
}