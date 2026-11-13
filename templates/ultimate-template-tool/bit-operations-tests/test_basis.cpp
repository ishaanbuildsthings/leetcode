// Stress tests XorBasis.cpp and RangeXorBasis.cpp against brute force.
// Run: g++ -O2 -std=c++17 test_basis.cpp -o /tmp/tb && /tmp/tb
#include "../bit-operations/XorBasis.cpp"
#include "../bit-operations/RangeXorBasis.cpp"

mt19937_64 rng(1);
long long rnd(long long hi) { return (long long)(rng() % (unsigned long long)hi); }
const long long MOD = 1'000'000'007;
#define CHECK(c) if (!(c)) { cerr << "FAIL line " << __LINE__ << ": " #c << endl; exit(1); }

vector<long long> subsetXors(const vector<long long>& vals) {
    vector<long long> res = {0};
    for (long long x : vals) {
        int m = res.size();
        for (int i = 0; i < m; i++) res.push_back(res[i] ^ x);
    }
    return res;
}

void checkBasis(const XorBasis& basis, const vector<long long>& vals, long long hi) {
    auto all = subsetXors(vals);
    set<long long> spanSet(all.begin(), all.end());
    vector<long long> span(spanSet.begin(), spanSet.end());
    CHECK(basis.size() == (long long)vals.size());
    CHECK(basis.countDistinctSubsetXors() == span.size());
    auto bv = basis.basis();
    auto bAll = subsetXors(bv);
    CHECK(set<long long>(bAll.begin(), bAll.end()) == spanSet);
    CHECK(is_sorted(bv.rbegin(), bv.rend()));
    CHECK(basis.basisSize() == (int)bv.size());
    CHECK(basis.maxSubsetXor() == span.back());
    for (long long k = 0; k < (long long)span.size() + 2; k++) {
        CHECK(basis.kthSmallestDistinctSubsetXor(k) == (k < (long long)span.size() ? span[k] : -1));
    }
    vector<long long> every = all;
    sort(every.begin(), every.end());
    for (long long k = 0; k < (long long)every.size() + 2; k++) {
        CHECK(basis.kthSmallestSubsetXor(k) == (k < (long long)every.size() ? every[k] : -1));
    }
    long long mn = -1;
    for (size_t i = 1; i < all.size(); i++) mn = (mn == -1 ? all[i] : min(mn, all[i]));
    CHECK(basis.minNonEmptySubsetXor() == mn);
    for (int t = 0; t < 10; t++) {
        long long x = rnd(hi * 2);
        CHECK(basis.doesSubsetXorEqualToXExist(x) == (bool)spanSet.count(x));
        long long mx = 0, lo = LLONG_MAX;
        for (long long s : span) { mx = max(mx, x ^ s); lo = min(lo, x ^ s); }
        CHECK(basis.maxXorOfXAndSubsetXor(x) == mx);
        CHECK(basis.minXorOfXAndSubsetXor(x) == lo);
        CHECK(basis.countSubsetsWithXorEqualToXMod(x, MOD) == (long long)count(all.begin(), all.end(), x) % MOD);
    }
}

int main() {
    vector<long long> his = {1, 2, 4, 16, 64, 1LL << 40, LLONG_MAX};
    for (int it = 0; it < 3000; it++) {
        long long hi = his[rnd(his.size())];
        XorBasis basis;
        vector<long long> vals;
        int cnt = rnd(10);
        for (int i = 0; i < cnt; i++) {
            long long x = rnd(hi);
            auto all = subsetXors(vals);
            bool could = find(all.begin(), all.end(), x) != all.end();
            CHECK(basis.insert(x) == !could);
            vals.push_back(x);
        }
        checkBasis(basis, vals, hi == LLONG_MAX ? LLONG_MAX / 2 : hi);
        CHECK(XorBasis(vals).basis() == basis.basis());
    }
    vector<long long> rhis = {1, 2, 8, 32, 1LL << 50, LLONG_MAX};
    for (int it = 0; it < 2000; it++) {
        long long hi = rhis[rnd(rhis.size())];
        int n = 1 + rnd(8);
        vector<long long> arr(n);
        for (auto& x : arr) x = rnd(hi);
        RangeXorBasis rxb(arr);
        for (int l = 0; l < n; l++) {
            for (int r = l; r < n; r++) {
                auto all = subsetXors(vector<long long>(arr.begin() + l, arr.begin() + r + 1));
                set<long long> span(all.begin(), all.end());
                CHECK(rxb.maxSubsetXorInRange(l, r) == *span.rbegin());
                CHECK(rxb.countDistinctSubsetXorsInRange(l, r) == span.size());
                CHECK((1ULL << rxb.basisSizeInRange(l, r)) == span.size());
                for (int t = 0; t < 4; t++) {
                    long long x = rnd(hi == LLONG_MAX ? hi : hi * 2);
                    CHECK(rxb.doesSubsetXorEqualToXExistInRange(l, r, x) == (bool)span.count(x));
                    long long mx = 0;
                    for (long long s : span) mx = max(mx, x ^ s);
                    CHECK(rxb.maxXorOfXAndSubsetXorInRange(l, r, x) == mx);
                }
            }
        }
        bool threw = false;
        try { rxb.maxSubsetXorInRange(0, n); } catch (const out_of_range&) { threw = true; }
        CHECK(threw);
    }
    vector<int> ints = {3, 10, 5};
    CHECK(XorBasis(ints).maxXorOfXAndSubsetXor(4) == 14);
    CHECK(RangeXorBasis(vector<int>{3, 10, 5, 6}).maxSubsetXorInRange(1, 3) == 15);
    cout << "c++ basis tests passed" << endl;
}
