// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/matrices/GaussianElimination.cpp
#include <bits/stdc++.h>
using namespace std;

// Linear algebra mod a prime MOD (default 1e9+7, any prime < 2^32) on vector<vector<int / long long>> (negatives fine)
// determinant(M)                det of M[k, k]
// matrixRank(M)                 rank of M[x, y]
// inverse(M)                    inverse of M[k, k], empty if it is singular
// solve(A, b)                   some x with sum over j of A[i][j] * x[j] = b[i] for every row i, empty if there is none
//                               (free variables are set to 0; a solvable system has MOD^(columns - rank) solutions)
// determinant<998244353>(M)     another prime
// determinant({{1, 2}, {3, 4}}) -> MOD - 2
// inverse({{2, 0}, {0, 4}}) -> {{500000004, 0}, {0, 250000002}}
// solve({{1, 1}, {1, -1}}, {10, 2}) -> {6, 4}
// spanning trees of a graph (Kirchhoff): determinant of the Laplacian (degree on the diagonal, -1 per edge) with any
// one row and column deleted

#pragma GCC push_options
#pragma GCC optimize("O3") // only this hot loop, so it vectorizes on GCC builds that skip that at -O2
// Gauss(-Jordan) elimination on the first numVars columns of a (entries in [0, MOD)), in place
// returns the pivot column of each pivot row; pivot rows end up first, each scaled so its pivot is 1, all entries in
// [0, MOD); full: clear pivot columns in every row, not just below; det gets the determinant's running product
template <uint32_t MOD>
vector<int> gaussEliminate(vector<vector<uint64_t>>& a, int numVars, bool full, uint64_t& det) {
    // products of two values < MOD that can pile onto a value < MOD before a uint64 overflows
    constexpr uint64_t BATCH = min<uint64_t>(1 << 20,
        (UINT64_MAX - MOD) / max<uint64_t>(1, (uint64_t)(MOD - 1) * (MOD - 1)));
    auto modPow = [](uint64_t b, uint64_t e) {
        uint64_t r = 1 % MOD;
        for (b %= MOD; e; e >>= 1, b = b * b % MOD) {
            if (e & 1) r = r * b % MOD;
        }
        return r;
    };
    int n = a.size(), m = n ? a[0].size() : 0;
    vector<uint64_t> pending(n, 0); // updates since the row was last reduced
    vector<int> pivotCols;
    det = 1 % MOD;
    int r = 0;
    for (int c = 0; c < numVars && r < n; c++) {
        int piv = -1;
        for (int i = r; i < n; i++) {
            if (a[i][c] % MOD) {
                piv = i;
                break;
            }
        }
        if (piv < 0) continue;
        if (piv != r) {
            swap(a[piv], a[r]);
            swap(pending[piv], pending[r]);
            det = (MOD - det) % MOD;
        }
        uint64_t v = a[r][c] % MOD;
        det = det * v % MOD;
        uint64_t inv = modPow(v, MOD - 2);
        uint64_t* pivotRow = a[r].data();
        for (int j = 0; j < m; j++) pivotRow[j] = pivotRow[j] % MOD * inv % MOD;
        pending[r] = 0;
        for (int i = full ? 0 : r + 1; i < n; i++) {
            if (i == r) continue;
            uint64_t f = a[i][c] % MOD;
            if (!f) continue;
            uint64_t* row = a[i].data();
            if (pending[i] == BATCH) {
                for (int j = 0; j < m; j++) row[j] %= MOD;
                pending[i] = 0;
            }
            uint64_t g = MOD - f;
            for (int j = c; j < m; j++) row[j] += g * pivotRow[j]; // the pivot row is 0 left of c
            pending[i]++;
        }
        pivotCols.push_back(c);
        r++;
    }
    for (auto& row : a) {
        for (auto& x : row) x %= MOD;
    }
    return pivotCols;
}
#pragma GCC pop_options

template <uint32_t MOD, typename T>
vector<vector<uint64_t>> gaussToRows(const vector<vector<T>>& M, int extraCols) {
    vector<vector<uint64_t>> a(M.size());
    for (size_t i = 0; i < M.size(); i++) {
        a[i].resize(M[i].size() + extraCols, 0);
        for (size_t j = 0; j < M[i].size(); j++) {
            long long x = (long long)(M[i][j] % (long long)MOD);
            a[i][j] = x < 0 ? x + MOD : x;
        }
    }
    return a;
}

// det of M[k, k]
// O(k^3)
template <uint32_t MOD = 1'000'000'007, typename T = long long>
long long determinant(const vector<vector<T>>& M) {
    int k = M.size();
    for (auto& row : M) {
        if ((int)row.size() != k) throw invalid_argument("determinant needs a square matrix");
    }
    auto a = gaussToRows<MOD>(M, 0);
    uint64_t det;
    return (int)gaussEliminate<MOD>(a, k, false, det).size() == k ? det : 0;
}

// rank of M[x, y]
// O(x * y * min(x, y))
template <uint32_t MOD = 1'000'000'007, typename T = long long>
int matrixRank(const vector<vector<T>>& M) {
    if (M.empty()) return 0;
    auto a = gaussToRows<MOD>(M, 0);
    uint64_t det;
    return gaussEliminate<MOD>(a, M[0].size(), false, det).size();
}

// inverse of M[k, k] (M * inverse(M) = identity), empty if M is singular
// O(k^3)
template <uint32_t MOD = 1'000'000'007, typename T = long long>
vector<vector<long long>> inverse(const vector<vector<T>>& M) {
    int k = M.size();
    for (auto& row : M) {
        if ((int)row.size() != k) throw invalid_argument("inverse needs a square matrix");
    }
    auto a = gaussToRows<MOD>(M, k);
    for (int i = 0; i < k; i++) a[i][k + i] = 1 % MOD;
    uint64_t det;
    if ((int)gaussEliminate<MOD>(a, k, true, det).size() < k) return {};
    vector<vector<long long>> res(k, vector<long long>(k));
    for (int i = 0; i < k; i++) {
        for (int j = 0; j < k; j++) res[i][j] = a[i][k + j];
    }
    return res;
}

// some x (size = columns of A) with sum over j of A[i][j] * x[j] = b[i] for every row i, empty if there is none
// free variables are set to 0
// O(rows * columns * min(rows, columns))
template <uint32_t MOD = 1'000'000'007, typename T = long long, typename U = long long>
vector<long long> solve(const vector<vector<T>>& A, const vector<U>& b) {
    if (A.size() != b.size()) throw invalid_argument("solve needs one b value per row of A");
    int cols = A.empty() ? 0 : A[0].size();
    auto a = gaussToRows<MOD>(A, 1);
    for (size_t i = 0; i < b.size(); i++) {
        long long x = (long long)(b[i] % (long long)MOD);
        a[i][cols] = x < 0 ? x + MOD : x;
    }
    uint64_t det;
    vector<int> pivotCols = gaussEliminate<MOD>(a, cols, true, det);
    for (size_t i = pivotCols.size(); i < a.size(); i++) {
        if (a[i][cols]) return {}; // a 0 = nonzero row
    }
    vector<long long> x(cols, 0);
    for (size_t i = 0; i < pivotCols.size(); i++) x[pivotCols[i]] = a[i][cols];
    return x;
}
