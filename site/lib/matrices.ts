import type { FillIn } from "@/components/TemplatePicker";

// The matrix templates (templates/matrices/): one class or a few functions each, on the Matrices tab. Ops are written
// Python-style; the C++ spelling follows in parentheses where it differs. Shapes: A[x, y], B[y, z], square M[k, k].
const GITHUB = "https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/matrices/";

export const MATRIX_MULTIPLICATION: FillIn[] = [
  {
    label: "Mod matrix: multiply, power, vector × matrix",
    title: "Entries mod MOD (default 1e9+7, any mod in C++ via ModMatrix<MOD>). Row vectors: vec @ M, so vec @ M^p steps a state p times",
    folder: "_matrices",
    file: "ModMatrix",
    ops: [
      ["M = ModMatrix(rows)", "x*y"],
      ["A @ B  (C++: A * B)", "x*y*z"],
      ["M ** p  (C++: M.pow(p))", "k^3*log(p)"],
      ["vec @ M  (C++: vec * M)", "x*y"],
      ["M.vecPow(vec, p)  vec @ M^p", "k^3*log(p)"],
      ["M[i][j]", "1"],
    ],
    githubUrl: GITHUB,
  },
  {
    label: "Min-plus matrix: shortest walk with exactly p edges",
    title: "M ** p gives the cheapest walk i -> j using exactly p edges (INF if none). Negative weights fine. 0-weight self-loops turn it into \"at most p\"",
    folder: "_matrices",
    file: "MinPlusMatrix",
    ops: [
      ["M = MinPlusMatrix(rows)  (INF = no edge)", "x*y"],
      ["A @ B  (C++: A * B)", "x*y*z"],
      ["vec @ M  (C++: vec * M)", "x*y"],
      ["M ** p  (C++: M.pow(p))", "k^3*log(p)"],
      ["M.vecPow(vec, p)  vec @ M^p", "k^3*log(p)"],
    ],
    githubUrl: GITHUB,
  },
  {
    label: "Max-plus matrix: longest walk with exactly p edges",
    title: "M ** p gives the heaviest walk i -> j using exactly p edges (NEG_INF if none). Walks can repeat nodes. 0-weight self-loops turn it into \"at most p\"",
    folder: "_matrices",
    file: "MaxPlusMatrix",
    ops: [
      ["M = MaxPlusMatrix(rows)  (NEG_INF = no edge)", "x*y"],
      ["A @ B  (C++: A * B)", "x*y*z"],
      ["vec @ M  (C++: vec * M)", "x*y"],
      ["M ** p  (C++: M.pow(p))", "k^3*log(p)"],
      ["M.vecPow(vec, p)  vec @ M^p", "k^3*log(p)"],
    ],
    githubUrl: GITHUB,
  },
];

export const LINEAR_ALGEBRA: FillIn[] = [
  {
    label: "Linear recurrence nth term O(d² log n)",
    title: "a[i] = c[0]·a[i-1] + ... + c[d-1]·a[i-d], 0-indexed, mod MOD: the matrix-power answer without building the d x d matrix",
    folder: "_matrices",
    file: "LinearRecurrence",
    ops: [["nthTerm(coeffs, initial, n)", "d^2*log(n)"]],
    githubUrl: GITHUB,
  },
];
