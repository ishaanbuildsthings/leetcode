// Stress tests for the C++ matrix templates against brute force:
// g++ -std=c++17 -O2 -fsanitize=address,undefined test_matrices.cpp -o t && ./t
#include "../ModMatrix.cpp"
#include "../MinPlusMatrix.cpp"
#include "../MaxPlusMatrix.cpp"
#include "../BoolMatrix.cpp"
#include "../LinearRecurrence.cpp"

mt19937_64 rng(12345);
long long rnd(long long lo, long long hi) { return uniform_int_distribution<long long>(lo, hi)(rng); }
using VV = vector<vector<long long>>;

VV randMat(int r, int c, long long lo, long long hi, double zeroRate) {
    VV m(r, vector<long long>(c));
    for (auto& row : m) {
        for (auto& x : row) x = (rnd(0, 999) < zeroRate * 1000) ? 0 : rnd(lo, hi);
    }
    return m;
}
long long md(long long x, long long mod) { x %= mod; return x < 0 ? x + mod : x; }
VV naiveMul(const VV& A, const VV& B, long long mod) {
    VV C(A.size(), vector<long long>(B[0].size(), 0));
    for (size_t i = 0; i < A.size(); i++)
        for (size_t k = 0; k < B.size(); k++)
            for (size_t j = 0; j < B[0].size(); j++) C[i][j] = (C[i][j] + (__int128)md(A[i][k], mod) * md(B[k][j], mod)) % mod;
    return C;
}
VV naivePow(const VV& M, int p, long long mod) {
    int k = M.size();
    VV R(k, vector<long long>(k, 0));
    for (int i = 0; i < k; i++) R[i][i] = 1 % mod;
    while (p--) R = naiveMul(R, M, mod);
    return R;
}
#define CHECK(c) do { if (!(c)) { cerr << "FAIL line " << __LINE__ << ": " #c << endl; exit(1); } } while (0)

template <uint32_t MOD>
void testModMatrix() {
    for (int it = 0; it < 300; it++) {
        int x = rnd(1, 40), y = rnd(1, 40), z = rnd(1, 40);
        VV A = randMat(x, y, -1e12, 1e12, 0.3), B = randMat(y, z, -1e12, 1e12, 0.3);
        CHECK((ModMatrix<MOD>(A) * ModMatrix<MOD>(B)).toVector() == naiveMul(A, B, MOD));
        vector<long long> vec(x);
        for (auto& v : vec) v = rnd(-1e15, 1e15);
        CHECK(vec * ModMatrix<MOD>(A) == naiveMul(VV{vec}, A, MOD)[0]);
        int k = rnd(1, 12), p = rnd(0, 12);
        VV M = randMat(k, k, -1e12, 1e12, 0.3);
        VV want = naivePow(M, p, MOD);
        ModMatrix<MOD> MM(M);
        CHECK(MM.pow(p).toVector() == want);
        vector<long long> v(k);
        for (auto& t : v) t = rnd(-50, 50);
        CHECK(MM.vecPow(v, p) == naiveMul(VV{v}, want, MOD)[0]);
    }
}

template <typename Mat>
void testTropical(long long INF, bool isMin) {
    auto better = [&](long long a, long long b) { return isMin ? min(a, b) : max(a, b); };
    for (int it = 0; it < 400; it++) {
        int k = rnd(1, 6), p = rnd(0, 5);
        VV M(k, vector<long long>(k));
        for (auto& r : M) for (auto& x : r) x = rnd(0, 9) < 4 ? INF : rnd(-50, 50);
        VV want(k, vector<long long>(k, INF));
        int total = 1;
        for (int i = 0; i < p; i++) total *= k;
        for (int s = 0; s < k; s++) {
            for (int code = 0; code < total; code++) {
                int cur = s, c = code; long long w = 0; bool ok = true;
                for (int t = 0; t < p; t++) {
                    int nxt = c % k; c /= k;
                    if (M[cur][nxt] == INF) { ok = false; break; }
                    w += M[cur][nxt]; cur = nxt;
                }
                if (ok) want[s][cur] = want[s][cur] == INF ? w : better(want[s][cur], w);
            }
        }
        CHECK(Mat(M).pow(p).toVector() == want);
        vector<long long> start(k, INF); start[0] = 0;
        CHECK(Mat(M).vecPow(start, p) == want[0]);
    }
}

void testBool() {
    for (int it = 0; it < 300; it++) {
        int x = rnd(1, 200), y = rnd(1, 200), z = rnd(1, 130);
        vector<vector<int>> A(x, vector<int>(y)), B(y, vector<int>(z));
        for (auto& r : A) for (auto& v : r) v = rnd(0, 99) < 5;
        for (auto& r : B) for (auto& v : r) v = rnd(0, 99) < 30;
        auto got = (BoolMatrix(A) * BoolMatrix(B)).toVector();
        for (int i = 0; i < x; i++) for (int j = 0; j < z; j++) {
            int w = 0;
            for (int k = 0; k < y; k++) w |= A[i][k] & B[k][j];
            CHECK(got[i][j] == w);
        }
        vector<int> vec(y);
        for (auto& v : vec) v = rnd(0, 9) < 2;
        auto gv = vec * BoolMatrix(B);
        for (int j = 0; j < z; j++) { int w = 0; for (int k = 0; k < y; k++) w |= vec[k] & B[k][j]; CHECK(gv[j] == w); }
        int n = rnd(1, 70), p = rnd(0, 6);
        vector<vector<int>> edges;
        for (int e = rnd(0, 150); e--;) edges.push_back({(int)rnd(0, n - 1), (int)rnd(0, n - 1)});
        auto M = BoolMatrix::fromEdges(n, edges);
        auto adj = M.toVector();
        vector<vector<int>> cur(n, vector<int>(n, 0));
        for (int i = 0; i < n; i++) cur[i][i] = 1;
        for (int t = 0; t < p; t++) {
            vector<vector<int>> nx(n, vector<int>(n, 0));
            for (int i = 0; i < n; i++) for (int k = 0; k < n; k++) if (cur[i][k]) for (int j = 0; j < n; j++) nx[i][j] |= adj[k][j];
            cur = nx;
        }
        CHECK(M.pow(p).toVector() == cur);
        auto R = M.closure().toVector();
        for (int s = 0; s < n; s++) {
            vector<int> seen(n, 0), st{s}; seen[s] = 1;
            while (!st.empty()) { int u = st.back(); st.pop_back(); for (int w = 0; w < n; w++) if (adj[u][w] && !seen[w]) seen[w] = 1, st.push_back(w); }
            CHECK(R[s] == seen);
        }
    }
}

template <uint32_t MOD>
void testLinearRecurrence() {
    for (int it = 0; it < 300; it++) {
        int d = rnd(1, 30);
        vector<long long> coeffs(d), init(d), seq;
        for (auto& c : coeffs) c = rnd(-1e9, 1e9);
        for (auto& c : init) c = rnd(-1e9, 1e9), seq.push_back(md(c, MOD));
        for (int i = d; i < 150; i++) {
            long long s = 0;
            for (int j = 0; j < d; j++) s = (s + (__int128)md(coeffs[j], MOD) * seq[i - 1 - j]) % MOD;
            seq.push_back(s);
        }
        for (int t = 0; t < 15; t++) { int n = rnd(0, 149); CHECK(nthTerm<MOD>(coeffs, init, n) == seq[n]); }
    }
}

int main() {
    testModMatrix<1'000'000'007>(); testModMatrix<998244353>(); testModMatrix<7>(); testModMatrix<2>(); testModMatrix<4294967291u>(); testModMatrix<1u << 31>();
    cout << "ModMatrix ok" << endl;
    testTropical<MinPlusMatrix>(MinPlusMatrix::INF, true);
    testTropical<MaxPlusMatrix>(MaxPlusMatrix::NEG_INF, false);
    cout << "MinPlusMatrix + MaxPlusMatrix ok" << endl;
    testBool();
    cout << "BoolMatrix ok" << endl;
    testLinearRecurrence<1'000'000'007>(); testLinearRecurrence<998244353>(); testLinearRecurrence<7>(); testLinearRecurrence<2>(); testLinearRecurrence<4294967291u>();
    cout << "LinearRecurrence ok" << endl;
}
