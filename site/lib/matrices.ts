import type { FillIn } from "@/components/TemplatePicker";

// The matrix templates (templates/matrices/): one class or a few functions each, on the Matrices tab. Ops are written
// Python-style; the C++ spelling follows in parentheses where it differs. Shapes: A[x, y], B[y, z], square M[k, k].
const GITHUB = "https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/matrices/";

export const MATRIX_MULTIPLICATION: FillIn[] = [
  {
    label: "Mod matrix O(k³ log p) power",
    title: "Entries mod MOD (default 1e9+7, any mod in C++ via ModMatrix<MOD>). Row vectors: vec @ M. Multiply, power, vec @ M^p, I + M + ... + M^(p-1)",
    folder: "_matrices",
    file: "ModMatrix",
    ops: [
      ["M = ModMatrix(rows)", "x*y"],
      ["ModMatrix.identity(k) / zeros(x, y)", "x*y"],
      ["A @ B  (C++: A * B)", "x*y*z"],
      ["vec @ M  (C++: vec * M)", "x*y"],
      ["M ** p  (C++: M.pow(p))", "k^3*log(p)"],
      ["M.vecPow(vec, p)  vec @ M^p", "k^3*log(p)"],
      ["M.powSum(p)  I + M + ... + M^(p-1)", "k^3*log(p)"],
      ["A + B, A - B", "x*y"],
      ["M.T  (C++: M.transpose())", "x*y"],
      ["M[i][j]", "1"],
    ],
    githubUrl: GITHUB,
  },
  {
    label: "Many vec @ M^p queries O(k² log p) each",
    title: "One fixed M, many vectors and / or powers: stores M^1, M^2, M^4, ... once, then each query is only vector-matrix products. Includes ModMatrix",
    folder: "_matrices",
    file: "MatPowQueries",
    ops: [
      ["pq = MatPowQueries(M, maxPower)", "k^3*log(P)"],
      ["pq.query(vec, p)  vec @ M^p", "k^2*log(p)"],
    ],
    note: "(M^p)[i][j] is pq.query(row i of the identity, p)[j]",
    githubUrl: GITHUB,
  },
  {
    label: "Min-plus matrix: shortest walk with exactly p edges",
    title: "(min, +) product: M ** p gives the cheapest walk i -> j using exactly p edges (INF if none). Negative weights fine. 0 self-loops make it \"at most p\"",
    folder: "_matrices",
    file: "MinPlusMatrix",
    ops: [
      ["M = MinPlusMatrix(rows)  (INF = no edge)", "x*y"],
      ["A @ B  (C++: A * B)", "x*y*z"],
      ["vec @ M  (C++: vec * M)", "x*y"],
      ["M ** p  (C++: M.pow(p))", "k^3*log(p)"],
      ["M.vecPow(vec, p)", "k^3*log(p)"],
    ],
    variant: {
      label: "Max-plus",
      title: "(max, +) instead: the heaviest walk with exactly p edges, NEG_INF if none",
      storageKey: "templatePicker.maxPlus.MinPlusMatrix",
      on: {
        label: "Max-plus matrix: heaviest walk with exactly p edges",
        file: "MaxPlusMatrix",
        ops: [
          ["M = MaxPlusMatrix(rows)  (NEG_INF = no edge)", "x*y"],
          ["A @ B  (C++: A * B)", "x*y*z"],
          ["vec @ M  (C++: vec * M)", "x*y"],
          ["M ** p  (C++: M.pow(p))", "k^3*log(p)"],
          ["M.vecPow(vec, p)", "k^3*log(p)"],
        ],
      },
    },
    githubUrl: GITHUB,
  },
  {
    label: "Boolean matrix (bitset): reachability, walks of exactly p steps",
    title: "Rows packed 64 per word. M ** p: is there a walk of exactly p edges i -> j. closure(): reachable in 0+ steps. Build from a 0/1 matrix or directed edges",
    folder: "_matrices",
    file: "BoolMatrix",
    ops: [
      ["M = BoolMatrix(rows)", "x*y"],
      ["BoolMatrix.fromEdges(n, edges)", "k^2/64+N"],
      ["A @ B  (C++: A * B)", "x*y*z/64"],
      ["vec @ M  (C++: vec * M)", "x*y/64"],
      ["M ** p  (C++: M.pow(p))", "k^3/64*log(p)"],
      ["M.closure()", "k^3/64"],
      ["M.get(i, j) / M.set(i, j, bit)", "1"],
    ],
    githubUrl: GITHUB,
  },
];

export const LINEAR_ALGEBRA: FillIn[] = [
  {
    label: "Linear recurrence nth term O(d² log n) + Berlekamp-Massey",
    title: "a[i] = c[0]·a[i-1] + ... + c[d-1]·a[i-d], 0-indexed: the matrix-power answer without the d x d matrix. Berlekamp-Massey finds the recurrence from 2d terms",
    folder: "_matrices",
    file: "LinearRecurrence",
    ops: [
      ["nthTerm(coeffs, initial, n)", "d^2*log(n)"],
      ["berlekampMassey(seq) -> coeffs", "L^2"],
      ["guessNthTerm(seq, n)", "L^2+d^2*log(n)"],
    ],
    note: "berlekampMassey and guessNthTerm need MOD prime; L = len(seq)",
    githubUrl: GITHUB,
  },
  {
    label: "Gaussian elimination mod p: determinant, rank, inverse, solve",
    title: "On plain lists of lists, MOD prime. inverse / solve return None (C++: empty) when there is none. Determinant of a Laplacian minor counts spanning trees",
    folder: "_matrices",
    file: "GaussianElimination",
    ops: [
      ["determinant(M)", "k^3"],
      ["matrixRank(A)", "x*y*min(x,y)"],
      ["inverse(M) -> M⁻¹ or None", "k^3"],
      ["solve(A, b) -> x or None", "x*y*min(x,y)"],
    ],
    githubUrl: GITHUB,
  },
];
