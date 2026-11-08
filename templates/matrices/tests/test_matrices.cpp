// Stress tests for the C++ matrix templates against brute force:
// g++ -std=c++17 -O2 -fsanitize=address,undefined test_matrices.cpp -o t && ./t
#include "../MatPowQueries.cpp"
#include "../MinPlusMatrix.cpp"
#include "../MaxPlusMatrix.cpp"
#include "../BoolMatrix.cpp"
#include "../LinearRecurrence.cpp"
#include "../GaussianElimination.cpp"

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
        auto MA = ModMatrix<MOD>(A);
        CHECK((MA - MA).toVector() == VV(x, vector<long long>(y, 0)));
        auto S2 = (MA + MA).toVector();
        for (int i = 0; i < x; i++) for (int j = 0; j < y; j++) CHECK(S2[i][j] == md(2 * md(A[i][j], MOD), MOD));
        CHECK(MA.transpose().transpose() == MA);
        int k = rnd(1, 12), p = rnd(0, 12);
        VV M = randMat(k, k, -1e12, 1e12, 0.3);
        VV want = naivePow(M, p, MOD);
        ModMatrix<MOD> MM(M);
        CHECK(MM.pow(p).toVector() == want);
        vector<long long> v(k);
        for (auto& t : v) t = rnd(-50, 50);
        CHECK(MM.vecPow(v, p) == naiveMul(VV{v}, want, MOD)[0]);
        VV S(k, vector<long long>(k, 0));
        for (int i = 0; i < p; i++) {
            VV Pi = naivePow(M, i, MOD);
            for (int a = 0; a < k; a++) for (int b = 0; b < k; b++) S[a][b] = (S[a][b] + Pi[a][b]) % MOD;
        }
        CHECK(MM.powSum(p).toVector() == S);
        MatPowQueries<MOD> pq(MM, 40);
        CHECK(pq.query(v, p) == naiveMul(VV{v}, want, MOD)[0]);
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
        vector<long long> prefix(seq.begin(), seq.begin() + 2 * d);
        auto found = berlekampMassey<MOD>(prefix);
        CHECK((int)found.size() <= d);
        for (int i = found.size(); i < 150; i++) {
            long long s = 0;
            for (size_t j = 0; j < found.size(); j++) s = (s + (__int128)found[j] * seq[i - 1 - j]) % MOD;
            CHECK(s == seq[i]);
        }
        CHECK(guessNthTerm<MOD>(prefix, 149) == seq[149]);
    }
}

template <uint32_t MOD>
int naiveRank(VV M) {
    for (auto& r : M) for (auto& x : r) x = md(x, MOD);
    int r = 0, n = M.size(), m = n ? M[0].size() : 0;
    auto inv = [](long long a) { long long res = 1, e = MOD - 2; a %= MOD; while (e) { if (e & 1) res = (__int128)res * a % MOD; a = (__int128)a * a % MOD; e >>= 1; } return res; };
    for (int c = 0; c < m && r < n; c++) {
        int piv = -1;
        for (int i = r; i < n; i++) if (M[i][c]) { piv = i; break; }
        if (piv < 0) continue;
        swap(M[r], M[piv]);
        long long iv = inv(M[r][c]);
        for (int i = 0; i < n; i++) if (i != r && M[i][c]) {
            long long f = (__int128)M[i][c] * iv % MOD;
            for (int j = 0; j < m; j++) M[i][j] = md(M[i][j] - (long long)((__int128)f * M[r][j] % MOD), MOD);
        }
        r++;
    }
    return r;
}

template <uint32_t MOD>
void testGauss() {
    for (int it = 0; it < 300; it++) {
        int k = rnd(1, 7);
        VV M = randMat(k, k, -5, 5, rnd(0, 1) ? 0.3 : 0.0);
        vector<int> perm(k); iota(perm.begin(), perm.end(), 0);
        long long brute = 0;
        do {
            int inv = 0;
            for (int i = 0; i < k; i++) for (int j = i + 1; j < k; j++) inv += perm[i] > perm[j];
            long long term = inv % 2 ? -1 : 1;
            for (int i = 0; i < k; i++) term *= M[i][perm[i]];
            brute += term;
        } while (next_permutation(perm.begin(), perm.end()));
        CHECK(determinant<MOD>(M) == md(brute, MOD));
        auto I = inverse<MOD>(M);
        if (md(brute, MOD) == 0) CHECK(I.empty());
        else {
            VV id(k, vector<long long>(k, 0));
            for (int i = 0; i < k; i++) id[i][i] = 1;
            CHECK(naiveMul(M, I, MOD) == id);
        }
        int x = rnd(1, 60), y = rnd(1, 60);
        VV A = randMat(x, y, -1e12, 1e12, vector<double>{0.0, 0.5, 0.9}[rnd(0, 2)]);
        if (x > 1 && rnd(0, 2) == 0) for (int j = 0; j < y; j++) A[x - 1][j] = A[0][j] + A[1][j];
        CHECK(matrixRank<MOD>(A) == naiveRank<MOD>(A));
        vector<long long> b(x);
        for (auto& v : b) v = rnd(-1e12, 1e12);
        auto sol = solve<MOD>(A, b);
        VV aug = A;
        for (int i = 0; i < x; i++) aug[i].push_back(b[i]);
        if (naiveRank<MOD>(aug) > naiveRank<MOD>(A)) CHECK(sol.empty());
        else {
            CHECK((int)sol.size() == y);
            for (int i = 0; i < x; i++) {
                long long s = 0;
                for (int j = 0; j < y; j++) s = (s + (__int128)md(A[i][j], MOD) * sol[j]) % MOD;
                CHECK(s == md(b[i], MOD));
            }
        }
    }
}

int main() {
    testModMatrix<1'000'000'007>(); testModMatrix<998244353>(); testModMatrix<7>(); testModMatrix<2>(); testModMatrix<4294967291u>(); testModMatrix<1u << 31>();
    cout << "ModMatrix + MatPowQueries ok" << endl;
    testTropical<MinPlusMatrix>(MinPlusMatrix::INF, true);
    testTropical<MaxPlusMatrix>(MaxPlusMatrix::NEG_INF, false);
    cout << "MinPlusMatrix + MaxPlusMatrix ok" << endl;
    testBool();
    cout << "BoolMatrix ok" << endl;
    testLinearRecurrence<1'000'000'007>(); testLinearRecurrence<998244353>(); testLinearRecurrence<7>(); testLinearRecurrence<2>(); testLinearRecurrence<4294967291u>();
    cout << "LinearRecurrence ok" << endl;
    testGauss<1'000'000'007>(); testGauss<998244353>(); testGauss<7>(); testGauss<2>(); testGauss<4294967291u>();
    cout << "GaussianElimination ok" << endl;
}
