// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/matrices/MatPowQueries.cpp
#include <bits/stdc++.h>
using namespace std;

// MatPowQueries is at the bottom: many vec * M^p queries against one fixed M
// MatPowQueries pq(M, maxPower);          precompute M^1, M^2, M^4, ... up to maxPower
// pq.query(vec, p)                        vec * M^p, 0 <= p <= maxPower
// entry (M^p)[i][j]: pq.query(row i of the identity, p)[j]

// Matrix with entries mod MOD (default 1e9+7, any MOD < 2^32). Row-vector convention: vec[1, x] * M[x, y] = vec[1, y]
// ModMatrix M({{1, 1}, {1, 0}});            from vector<vector<int / long long>>, negatives fine (stored in [0, MOD))
// ModMatrix<998244353> M2(rows);            another mod
// auto I = ModMatrix<>::identity(3);
// auto Z = ModMatrix<>::zeros(2, 3);
// auto C = A * B;                           A[x, y] * B[y, z] = C[x, z]
// auto v = vec * M;                         vector<long long> {a, b} * M -> {a', b'}
// auto P = M.pow(p);                        M[k, k] ^ p
// auto v = M.vecPow(vec, p);                vec * M^p
// auto S = M.powSum(p);                     I + M + M^2 + ... + M^(p-1)
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

    // O(k^2) -- the k x k identity
    static ModMatrix identity(int k) {
        ModMatrix res(k, k);
        for (int i = 0; i < k; i++) res[i][i] = 1 % MOD;
        return res;
    }

    // O(x*y) -- an x by y matrix of zeros
    static ModMatrix zeros(int x, int y) { return ModMatrix(x, y); }

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

    bool operator==(const ModMatrix& other) const {
        return rows == other.rows && cols == other.cols && vals == other.vals;
    }

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

    // I + M + M^2 + ... + M^(p-1) for M[k, k], p >= 0 (p = 0 gives zeros)
    // e.g. vec * M.powSum(p) sums vec * M^i over 0 <= i < p (walks of length < p)
    // O(k^3 log p)
    ModMatrix powSum(long long p) const {
        requireSquare("matrix power sum", p);
        ModMatrix power = identity(rows); // M^c
        ModMatrix total(rows, rows);      // I + ... + M^(c-1)
        for (int bit = 62; bit >= 0; bit--) {
            if (!(p >> bit) && bit) continue;
            total = total + total * power; // c -> 2c
            power = power * power;
            if ((p >> bit) & 1) {           // c -> c + 1
                total = total + power;
                power = power * (*this);
            }
        }
        return total;
    }

    // O(x*y) -- entrywise sum
    ModMatrix operator+(const ModMatrix& other) const {
        if (rows != other.rows || cols != other.cols) throw invalid_argument(shapeError("add", rows, cols, other.rows,
            other.cols));
        ModMatrix res(rows, cols);
        for (size_t i = 0; i < vals.size(); i++) {
            uint64_t sum = (uint64_t)vals[i] + other.vals[i];
            res.vals[i] = sum >= MOD ? sum - MOD : sum;
        }
        return res;
    }

    // O(x*y) -- entrywise difference
    ModMatrix operator-(const ModMatrix& other) const {
        if (rows != other.rows || cols != other.cols) throw invalid_argument(shapeError("sub", rows, cols, other.rows,
            other.cols));
        ModMatrix res(rows, cols);
        for (size_t i = 0; i < vals.size();
            i++) res.vals[i] = vals[i] >= other.vals[i] ? vals[i] - other.vals[i] : vals[i] + (MOD - other.vals[i]);
        return res;
    }

    // O(x*y) -- the transpose, M[x, y] -> T[y, x]
    ModMatrix transpose() const {
        ModMatrix res(cols, rows);
        for (int i = 0; i < rows; i++) {
            for (int j = 0; j < cols; j++) res[j][i] = (*this)[i][j];
        }
        return res;
    }

private:
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
    static constexpr uint64_t BATCH = min<uint64_t>(1 << 20,
        (UINT64_MAX - MOD) / max<uint64_t>(1, (uint64_t)(MOD - 1) * (MOD - 1)));

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
        if (rows != cols) throw invalid_argument(string(what) + " needs a square matrix, got [" + to_string(rows)
            + ", " + to_string(cols) + "]");
        if (p < 0) throw invalid_argument(string(what) + " needs p >= 0");
    }

    static string shapeError(const char* what, long long r1, long long c1, long long r2, long long c2) {
        return string(what) + " shape mismatch: [" + to_string(r1) + ", " + to_string(c1) + "] with [" + to_string(r2)
            + ", " + to_string(c2) + "]";
    }
};


// Many vec * M^p queries for one fixed M[k, k] (different vectors and / or powers)
// MatPowQueries pq(ModMatrix({{1, 1}, {1, 0}}), (long long)1e18);
// pq.query(vector<long long>{1, 0}, 10) -> {89, 55}
template <uint32_t MOD = 1'000'000'007>
struct MatPowQueries {
    vector<ModMatrix<MOD>> powers; // powers[b] = M^(2^b)
    long long maxPower;

    // O(k^3 log maxPower) -- stores M^(2^b) for every 2^b <= maxPower
    MatPowQueries(const ModMatrix<MOD>& M, long long maxPower) : maxPower(maxPower) {
        if (M.rows != M.cols) throw invalid_argument("MatPowQueries needs a square matrix");
        powers.push_back(M);
        while ((int)powers.size() < 62 && (1LL << powers.size()) <= maxPower) powers.push_back(powers.back()
            * powers.back());
    }

    // vec[1, k] * M^p = vec[1, k], 0 <= p <= maxPower
    // O(k^2 log p)
    template <typename T = long long>
    vector<long long> query(const vector<T>& vec, long long p) const {
        if (p < 0 || p > maxPower) throw invalid_argument("query power " + to_string(p) + " outside [0, "
            + to_string(maxPower) + "]");
        vector<long long> res = vector<long long>(vec.begin(), vec.end()) * ModMatrix<MOD>::identity(powers[0].rows);
        for (int b = 0; p; b++, p >>= 1) {
            if (p & 1) res = res * powers[b];
        }
        return res;
    }
};
