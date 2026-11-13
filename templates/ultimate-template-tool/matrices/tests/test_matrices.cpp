// Stress tests matMul.cpp, vecMatMul.cpp and matPow.cpp against exact math (__int128 with small values).
#include "../matMul.cpp"
#include "../vecMatMul.cpp"
#include "../matPow.cpp"

#define CHECK(c)                                                    \
    if (!(c)) {                                                     \
        fprintf(stderr, "FAIL line %d: %s\n", __LINE__, #c);        \
        exit(1);                                                    \
    }

mt19937_64 rng(5);
ll rnd(ll lo, ll hi) { return lo + (ll)(rng() % (unsigned long long)(hi - lo + 1)); }
ll md(__int128 v, ll mod) { v %= mod; if (v < 0) v += mod; return (ll)v; }

int main() {
    vector<ll> mods = {1, 2, 7, 1000000007, 998244353, 1LL << 31};
    for (int trial = 0; trial < 3000; trial++) {
        ll mod = mods[rnd(0, mods.size() - 1)];
        int x = rnd(1, 6), y = rnd(1, 6), z = rnd(1, 6);
        ll hi = vector<ll>{3, 1000000000, (ll)4e18}[rnd(0, 2)];
        auto rand = [&](int r, int c) {
            vector<vector<ll>> m(r, vector<ll>(c)); for (auto& row : m) for (ll& v : row) v = rnd(-hi, hi); return m;
        };
        auto A = rand(x, y), B = rand(y, z);
        // exact reference: reduce every entry first (as math mod mod allows), then multiply in __int128
        auto ref = [&](const vector<vector<ll>>& P, const vector<vector<ll>>& Q) {
            vector<vector<ll>> R(P.size(), vector<ll>(Q.empty() ? 0 : Q[0].size()));
            for (size_t i = 0; i < P.size(); i++)
                for (size_t j = 0; j < R[i].size(); j++) {
                    __int128 s = 0;
                    for (size_t k = 0; k < Q.size(); k++) s += (__int128)md(P[i][k], mod) * md(Q[k][j], mod);
                    R[i][j] = md(s, mod);
                }
            return R;
        };
        CHECK(matMul(A, B, mod) == ref(A, B));
        vector<ll> vec(x);
        for (ll& v : vec) v = rnd(-hi, hi);
        CHECK(vecMatMul(vec, A, mod) == ref({vec}, A)[0]);
        auto M = rand(x, x);
        ll p = rnd(0, 12);
        vector<vector<ll>> want(x, vector<ll>(x, 0));
        for (int i = 0; i < x; i++) want[i][i] = 1 % mod;
        for (ll t = 0; t < p; t++) want = ref(want, M);
        CHECK(matPow(M, p, mod) == want);
    }
    CHECK(matPow({{1, 1}, {1, 0}}, 10, 1000000007) == vector<vector<ll>>({{89, 55}, {55, 34}}));
    CHECK(matMul({{1, 2}, {3, 4}}, {{5, 6}, {7, 8}}, 1000000007) == vector<vector<ll>>({{19, 22}, {43, 50}}));
    CHECK(vecMatMul({1, 2}, {{5, 6}, {7, 8}}, 1000000007) == vector<ll>({19, 22}));
    bool threw = false;
    try { matMul({{1, 2}}, {{1, 2}}, 7); } catch (const invalid_argument&) { threw = true; }
    CHECK(threw);
    printf("matMul, vecMatMul, matPow (C++): all agree with exact math\n");
}
