// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/matrices/BoolMatrix.cpp
#include <bits/stdc++.h>
using namespace std;

// Boolean matrix stored as packed 64-bit words per row, so ops run 64 entries at a time (any size, set at runtime)
// Row-vector convention like ModMatrix. As a graph: M[i][j] = 1 means an edge i -> j
// BoolMatrix M(rows);                       from vector<vector<int>> (any nonzero = 1)
// auto M = BoolMatrix::fromEdges(n, edges); directed {a, b} edges, labels 0..n-1
// auto C = A * B;                           C[i][j] = OR over k of (A[i][k] AND B[k][j])
// auto v = vec * M;                         vector<int> of 0/1 (a set of nodes) -> nodes one step away from it
// auto P = M.pow(p);                        P[i][j] = 1 if some walk i -> j has exactly p edges
// auto R = M.closure();                     R[i][j] = 1 if j is reachable from i in 0 or more steps (R[i][i] = 1)
// M.get(i, j) / M.set(i, j, bit)
// M.toVector()                              back to vector<vector<int>> of 0/1
// BoolMatrix::fromEdges(3, {{0, 1}, {1, 2}}).closure().toVector() -> {{1, 1, 1}, {0, 1, 1}, {0, 0, 1}}
struct BoolMatrix {
    int rows, cols, words; // words per row
    vector<uint64_t> bits;

    // O(x*y) -- from a vector of rows
    template <typename T = int>
    BoolMatrix(const vector<vector<T>>& init) : BoolMatrix(init.size(), init.empty() ? 0 : init[0].size()) {
        for (int i = 0; i < rows; i++) {
            for (int j = 0; j < cols; j++) {
                if (init[i][j]) set(i, j, 1);
            }
        }
    }

    // O(n^2 / 64 + edges) -- n x n adjacency matrix of directed {a, b} edges
    static BoolMatrix fromEdges(int n, const vector<vector<int>>& edges) {
        BoolMatrix res(n, n);
        for (auto& e : edges) res.set(e[0], e[1], 1);
        return res;
    }

    // O(k^2 / 64) -- the k x k identity
    static BoolMatrix identity(int k) {
        BoolMatrix res(k, k);
        for (int i = 0; i < k; i++) res.set(i, i, 1);
        return res;
    }

    // O(1) -- entry [i][j] as 0 / 1
    int get(int i, int j) const { return row(i)[j >> 6] >> (j & 63) & 1; }

    // O(1) -- set entry [i][j] to bit (0 / 1)
    void set(int i, int j, int bit) {
        uint64_t mask = 1ULL << (j & 63);
        if (bit) row(i)[j >> 6] |= mask;
        else row(i)[j >> 6] &= ~mask;
    }

    // O(x*y) -- back to vector<vector<int>> of 0/1
    vector<vector<int>> toVector() const {
        vector<vector<int>> res(rows, vector<int>(cols));
        for (int i = 0; i < rows; i++) {
            for (int j = 0; j < cols; j++) res[i][j] = get(i, j);
        }
        return res;
    }

    bool operator==(const BoolMatrix& other) const { return rows == other.rows && cols == other.cols && bits == other.bits; }

    // A[x, y] * B[y, z] = C[x, z]
    // O(x*y*z / 64)
    friend BoolMatrix operator*(const BoolMatrix& A, const BoolMatrix& B) {
        if (A.cols != B.rows) throw invalid_argument("matmul shape mismatch: [" + to_string(A.rows) + ", " + to_string(A.cols) + "] * [" + to_string(B.rows) + ", " + to_string(B.cols) + "]");
        BoolMatrix C(A.rows, B.cols);
        for (int i = 0; i < A.rows; i++) mulRowInto(A.row(i), A.words, B, C.row(i));
        return C;
    }

    // vec[1, x] * M[x, y] = vec[1, y], vec of 0/1
    // O(x*y / 64)
    friend vector<int> operator*(const vector<int>& vec, const BoolMatrix& M) {
        if ((int)vec.size() != M.rows) throw invalid_argument("vecmat shape mismatch: [1, " + to_string(vec.size()) + "] * [" + to_string(M.rows) + ", " + to_string(M.cols) + "]");
        vector<uint64_t> in((M.rows + 63) / 64), out(M.words);
        for (int k = 0; k < M.rows; k++) {
            if (vec[k]) in[k >> 6] |= 1ULL << (k & 63);
        }
        mulRowInto(in.data(), in.size(), M, out.data());
        vector<int> res(M.cols);
        for (int j = 0; j < M.cols; j++) res[j] = out[j >> 6] >> (j & 63) & 1;
        return res;
    }

    // M[k, k] ^ p, p >= 0 (p = 0 gives identity)
    // O(k^3 log p / 64)
    BoolMatrix pow(long long p) const {
        requireSquare("matrix power");
        if (p < 0) throw invalid_argument("matrix power needs p >= 0");
        BoolMatrix res = identity(rows), base = *this;
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

    // reflexive transitive closure of M[k, k]: R[i][j] = 1 if j is reachable from i in 0 or more steps
    // O(k^3 / 64)
    BoolMatrix closure() const {
        requireSquare("closure");
        BoolMatrix reach = *this;
        for (int i = 0; i < rows; i++) reach.set(i, i, 1);
        for (int k = 0; k < rows; k++) { // Warshall: allow k as a middle stop
            const uint64_t* rk = reach.row(k);
            for (int i = 0; i < rows; i++) {
                if (i == k || !reach.get(i, k)) continue;
                uint64_t* ri = reach.row(i);
                for (int w = 0; w < words; w++) ri[w] |= rk[w];
            }
        }
        return reach;
    }

private:
    BoolMatrix(int x, int y) : rows(x), cols(y), words((y + 63) / 64), bits((size_t)x * words, 0) {}

    uint64_t* row(int i) { return bits.data() + (size_t)i * words; }
    const uint64_t* row(int i) const { return bits.data() + (size_t)i * words; }

#pragma GCC push_options
#pragma GCC optimize("O3") // only this hot loop, so it vectorizes on GCC builds that skip that at -O2
    // out = OR of B's rows k over the set bits k of in (in has inWords words)
    static void mulRowInto(const uint64_t* in, int inWords, const BoolMatrix& B, uint64_t* out) {
        for (int w = 0; w < inWords; w++) {
            for (uint64_t x = in[w]; x; x &= x - 1) {
                const uint64_t* bk = B.row(w * 64 + __builtin_ctzll(x));
                for (int j = 0; j < B.words; j++) out[j] |= bk[j];
            }
        }
    }
#pragma GCC pop_options

    void requireSquare(const char* what) const {
        if (rows != cols) throw invalid_argument(string(what) + " needs a square matrix, got [" + to_string(rows) + ", " + to_string(cols) + "]");
    }
};
