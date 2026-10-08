#include <bits/stdc++.h>
using namespace std;

const long long MOD = 1'000'000'007;

// Entries can be int or long long, and may be negative: anything in (-MOD, MOD) works.
// All outputs are long long in [0, MOD).

// A[x, y] @ B[y, z] = C[x, z]
// O(x*y*z)
template <typename T1, typename T2>
vector<vector<long long>> matMul(const vector<vector<T1>>& A, const vector<vector<T2>>& B) {
    int rows = A.size();
    int mid = B.size();
    int cols = B[0].size();
    vector<vector<long long>> C(rows, vector<long long>(cols, 0));
    for (int i = 0; i < rows; i++) {
        for (int k = 0; k < mid; k++) {
            long long a = A[i][k];
            if (a == 0) continue;
            for (int j = 0; j < cols; j++) {
                C[i][j] = (C[i][j] + a * B[k][j]) % MOD;
            }
        }
        for (int j = 0; j < cols; j++) {
            if (C[i][j] < 0) C[i][j] += MOD;
        }
    }
    return C;
}

// vec[1, x] @ mat[x, y] = vec[1, y]
// O(x*y)
template <typename T1, typename T2>
vector<long long> vecMatMul(const vector<T1>& vec, const vector<vector<T2>>& M) {
    int rows = M.size();
    int cols = M[0].size();
    vector<long long> result(cols, 0);
    for (int i = 0; i < rows; i++) {
        long long a = vec[i];
        if (a == 0) continue;
        for (int j = 0; j < cols; j++) {
            result[j] = (result[j] + a * M[i][j]) % MOD;
        }
    }
    for (int j = 0; j < cols; j++) {
        if (result[j] < 0) result[j] += MOD;
    }
    return result;
}

// mat[x, x] ^ power, power >= 0, power 0 gives identity
// O(x^3) * log(power)
template <typename T>
vector<vector<long long>> matPow(const vector<vector<T>>& M, long long p) {
    int size = M.size();
    vector<vector<long long>> base(size, vector<long long>(size, 0));
    vector<vector<long long>> result(size, vector<long long>(size, 0));
    for (int i = 0; i < size; i++) {
        result[i][i] = 1;
        for (int j = 0; j < size; j++) {
            base[i][j] = M[i][j];
        }
    }
    while (p > 0) {
        if (p & 1) {
            result = matMul(result, base);
        }
        base = matMul(base, base);
        p >>= 1;
    }
    return result;
}