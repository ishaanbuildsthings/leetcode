// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/matrices/ModMatrix.cpp
#include <bits/stdc++.h>
using namespace std;

// Matrix with entries mod MOD (default 1e9+7, any MOD < 2^32). Row-vector convention: vec[1, x] * M[x, y] = vec[1, y]
// ModMatrix M({{1, 1}, {1, 0}});            from vector<vector<int / long long>>, negatives fine (stored in [0, MOD))
// ModMatrix<998244353> M2(rows);            another mod
// auto C = A * B;                           A[x, y] * B[y, z] = C[x, z]
// auto v = vec * M;                         vector<long long> {a, b} * M -> {a', b'}
// auto P = M.pow(p);                        M[k, k] ^ p
// auto v = M.vecPow(vec, p);                vec * M^p
// M[i][j]                                   read / write an entry (keep it in [0, MOD))
// fib: vector<long long>{1, 0} * ModMatrix({{1, 1}, {1, 0}}).pow(10) -> {89, 55}
template <uint32_t MOD = 1'000'000'007>
struct ModMatrix {
    int rows, cols;
    vector<uint32_t> vals; // row-major, entries in [0, MOD)

    // O(x*y) -- from a vector of rows, entries taken mod MOD
    ModMatrix(const vector<vector<long long>>& init) { assign(init); }
    template <typename T>
    ModMatrix(const vector<vector<T>>& init) { assign(init); }

    uint32_t* operator[](int i) { return vals.data() + (size_t)i * cols; }
    const uint32_t* operator[](int i) const { return vals.data() + (size_t)i * cols; }

    // O(x*y) -- back to vector<vector<long long>>
    vector<vector<long long>> toVector() const {
        vector<vector<long long>> res(rows, vector<long long>(cols));
        for (int i = 0; i < rows; i++) {
            for (int j = 0; j < cols; j++) res[i][j] = (*this)[i][j];
        }
        return res;
    }

    bool operator==(const ModMatrix& other) const { return rows == other.rows && cols == other.cols && vals == other.vals; }

    // A[x, y] * B[y, z] = C[x, z]
    // O(x*y*z)
    friend ModMatrix operator*(const ModMatrix& A, const ModMatrix& B) {
        if (A.cols != B.rows) throw invalid_argument(shapeError("matmul", A.rows, A.cols, B.rows, B.cols));
        ModMatrix C(A.rows, B.cols);
        static vector<uint64_t> acc; // scratch row, kept between calls so small matrices skip an allocation
        if ((int)acc.size() < B.cols) acc.resize(B.cols);
        for (int i = 0; i < A.rows; i++) {
            mulRowInto(A[i], B, acc.data());
            for (int j = 0; j < B.cols; j++) C[i][j] = acc[j];
        }
        return C;
    }

    // vec[1, x] * M[x, y] = vec[1, y], vec holds any ints
    // O(x*y)
    template <typename T>
    friend vector<long long> operator*(const vector<T>& vec, const ModMatrix& M) {
        if ((int)vec.size() != M.rows) throw invalid_argument(shapeError("vecmat", 1, vec.size(), M.rows, M.cols));
        vector<uint32_t> row(M.rows);
        for (int i = 0; i < M.rows; i++) {
            long long x = (long long)(vec[i] % (long long)MOD);
            row[i] = x < 0 ? x + MOD : x;
        }
        vector<uint64_t> acc(M.cols);
        mulRowInto(row.data(), M, acc.data());
        return vector<long long>(acc.begin(), acc.end());
    }

    // M[k, k] ^ p, p >= 0 (p = 0 gives identity)
    // O(k^3 log p)
    ModMatrix pow(long long p) const {
        requireSquare("matrix power", p);
        ModMatrix res = identity(rows), base = *this;
        bool first = true;
        while (p > 0) {
            if (p & 1) {
                res = first ? base : res * base;
                first = false;
            }
            p >>= 1;
            if (p) base = base * base;
        }
        return res;
    }

    // vec[1, k] * M[k, k]^p = vec[1, k], about half the work of vec * M.pow(p) (no result matrix is built)
    // O(k^3 log p)
    template <typename T = long long>
    vector<long long> vecPow(const vector<T>& vec, long long p) const {
        requireSquare("matrix power", p);
        vector<long long> res = vector<long long>(vec.begin(), vec.end()) * identity(rows);
        ModMatrix base = *this;
        while (p > 0) {
            if (p & 1) res = res * base;
            p >>= 1;
            if (p) base = base * base;
        }
        return res;
    }

private:
    static ModMatrix identity(int k) {
        ModMatrix res(k, k);
        for (int i = 0; i < k; i++) res[i][i] = 1 % MOD;
        return res;
    }

    template <typename T>
    void assign(const vector<vector<T>>& init) {
        rows = init.size();
        cols = init.empty() ? 0 : init[0].size();
        vals.assign((size_t)rows * cols, 0);
        for (int i = 0; i < rows; i++) {
            for (int j = 0; j < cols; j++) {
                long long x = (long long)(init[i][j] % (long long)MOD);
                vals[(size_t)i * cols + j] = x < 0 ? x + MOD : x;
            }
        }
    }

    ModMatrix(int x, int y) : rows(x), cols(y), vals((size_t)x * y, 0) {}

    // products of two values < MOD that can pile onto a value < MOD before a uint64 overflows
    static constexpr uint64_t BATCH = min<uint64_t>(1 << 20, (UINT64_MAX - MOD) / max<uint64_t>(1, (uint64_t)(MOD - 1) * (MOD - 1)));

#pragma GCC push_options
#pragma GCC optimize("O3") // only this hot loop, so it vectorizes on GCC builds that skip that at -O2
    // acc[0..B.cols) = row (length B.rows) * B, reduced into [0, MOD); one % per BATCH products instead of per product
    static void mulRowInto(const uint32_t* row, const ModMatrix& B, uint64_t* acc) {
        int m = B.cols;
        fill(acc, acc + m, 0);
        uint64_t pending = 0;
        for (int k = 0; k < B.rows; k++) {
            uint64_t a = row[k];
            if (!a) continue;
            const uint32_t* brow = B[k];
            for (int j = 0; j < m; j++) acc[j] += a * brow[j];
            if (++pending == BATCH) {
                for (int j = 0; j < m; j++) acc[j] %= MOD;
                pending = 0;
            }
        }
        for (int j = 0; j < m; j++) acc[j] %= MOD;
    }
#pragma GCC pop_options

    void requireSquare(const char* what, long long p) const {
        if (rows != cols) throw invalid_argument(string(what) + " needs a square matrix, got [" + to_string(rows) + ", " + to_string(cols) + "]");
        if (p < 0) throw invalid_argument(string(what) + " needs p >= 0");
    }

    static string shapeError(const char* what, long long r1, long long c1, long long r2, long long c2) {
        return string(what) + " shape mismatch: [" + to_string(r1) + ", " + to_string(c1) + "] with [" + to_string(r2) + ", " + to_string(c2) + "]";
    }
};
