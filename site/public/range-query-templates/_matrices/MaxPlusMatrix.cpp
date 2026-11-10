// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/matrices/MaxPlusMatrix.cpp
#include <bits/stdc++.h>
using namespace std;

// (max, +) matrix: "multiply" adds weights, "add" takes the max. Row-vector convention like ModMatrix
// M[i][j] = weight of edge i -> j (MaxPlusMatrix::NEG_INF for no edge), any weights in the limit below (negatives fine)
// real walk weights must stay within -1e18 .. 1e18
// MaxPlusMatrix M(rows);                     from vector<vector<long long>>
// auto C = A * B;                     C[i][j] = max over k of A[i][k] + B[k][j]
// auto v = vec * M;                   v[j] = max over k of vec[k] + M[k][j] (vec[k] = best weight to reach k so far)
// auto P = M.pow(p);                  P[i][j] = heaviest walk i -> j with exactly p edges, NEG_INF if none
// auto v = M.vecPow(vec, p);          vec * M^p
// add 0-weight self-loops (M[i][i] = max(M[i][i], 0)) to get "at most p edges"
// M[i][j]                             read / write an entry
struct MaxPlusMatrix {
    static constexpr long long NEG_INF = -(LLONG_MAX / 4);
    int rows, cols;
    vector<long long> vals; // row-major

    // O(x*y) -- from a vector of rows (NEG_INF = no edge)
    MaxPlusMatrix(const vector<vector<long long>>& init) : rows(init.size()), cols(init.empty() ? 0 : init[0].size()),
        vals((size_t)rows * cols) {
        for (int i = 0; i < rows; i++) {
            for (int j = 0; j < cols; j++) vals[(size_t)i * cols + j] = clamp(init[i][j]);
        }
    }

    // O(k^2) -- the identity: 0 on the diagonal (empty walk), NEG_INF elsewhere
    static MaxPlusMatrix identity(int k) {
        MaxPlusMatrix res(k, k);
        for (int i = 0; i < k; i++) res[i][i] = 0;
        return res;
    }

    long long* operator[](int i) { return vals.data() + (size_t)i * cols; }
    const long long* operator[](int i) const { return vals.data() + (size_t)i * cols; }

    // O(x*y) -- back to vector<vector<long long>>
    vector<vector<long long>> toVector() const {
        vector<vector<long long>> res(rows, vector<long long>(cols));
        for (int i = 0; i < rows; i++) {
            for (int j = 0; j < cols; j++) res[i][j] = (*this)[i][j];
        }
        return res;
    }

    // A[x, y] * B[y, z] = C[x, z]
    // O(x*y*z)
    friend MaxPlusMatrix operator*(const MaxPlusMatrix& A, const MaxPlusMatrix& B) {
        if (A.cols != B.rows) throw invalid_argument("matmul shape mismatch: [" + to_string(A.rows) + ", "
            + to_string(A.cols) + "] * [" + to_string(B.rows) + ", " + to_string(B.cols) + "]");
        MaxPlusMatrix C(A.rows, B.cols);
        for (int i = 0; i < A.rows; i++) mulRowInto(A[i], B, C[i]);
        return C;
    }

    // vec[1, x] * M[x, y] = vec[1, y] (NEG_INF = unreachable)
    // O(x*y)
    friend vector<long long> operator*(const vector<long long>& vec, const MaxPlusMatrix& M) {
        if ((int)vec.size() != M.rows) throw invalid_argument("vecmat shape mismatch: [1, " + to_string(vec.size())
            + "] * [" + to_string(M.rows) + ", " + to_string(M.cols) + "]");
        vector<long long> row(vec.size()), res(M.cols);
        for (size_t i = 0; i < vec.size(); i++) row[i] = clamp(vec[i]);
        mulRowInto(row.data(), M, res.data());
        return res;
    }

    // M[k, k] ^ p, p >= 0 (p = 0 gives identity)
    // O(k^3 log p)
    MaxPlusMatrix pow(long long p) const {
        requireSquare(p);
        MaxPlusMatrix res = identity(rows), base = *this;
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

    // vec[1, k] * M[k, k]^p = vec[1, k], about half the work of vec * M.pow(p)
    // O(k^3 log p)
    vector<long long> vecPow(vector<long long> vec, long long p) const {
        requireSquare(p);
        vec = vec * identity(rows);
        MaxPlusMatrix base = *this;
        while (p > 0) {
            if (p & 1) vec = vec * base;
            p >>= 1;
            if (p) base = base * base;
        }
        return vec;
    }

private:
    MaxPlusMatrix(int x, int y) : rows(x), cols(y), vals((size_t)x * y, NEG_INF) {}

    static long long clamp(long long x) { return x <= NEG_INF / 2 ? NEG_INF : x; }

#pragma GCC push_options
#pragma GCC optimize("O3") // only this hot loop, so it vectorizes on GCC builds that skip that at -O2
    // out[0..B.cols) = row * B; sums of a real and a NEG_INF land past the halfway mark and get snapped back
    static void mulRowInto(const long long* row, const MaxPlusMatrix& B, long long* out) {
        int m = B.cols;
        fill(out, out + m, NEG_INF);
        for (int k = 0; k < B.rows; k++) {
            long long a = row[k];
            if (a <= NEG_INF) continue;
            const long long* brow = B[k];
            for (int j = 0; j < m; j++) out[j] = max(out[j], a + brow[j]);
        }
        for (int j = 0; j < m; j++) out[j] = clamp(out[j]);
    }
#pragma GCC pop_options

    void requireSquare(long long p) const {
        if (rows != cols) throw invalid_argument("matrix power needs a square matrix, got [" + to_string(rows) + ", "
            + to_string(cols) + "]");
        if (p < 0) throw invalid_argument("matrix power needs p >= 0");
    }
};
