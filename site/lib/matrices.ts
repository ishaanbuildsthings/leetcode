import type { FillIn } from "@/components/TemplatePicker";

// The matrix templates (templates/ultimate-template-tool/matrices/): one function each, on the Matrices tab. Standard
// math: a matrix product is row times column, A[x, y] @ B[y, z] = C[x, z]; a vector times a matrix is the vector
// against every column, vec[1, x] @ M[x, y] = res[1, y]. Every function takes the mod.
const GITHUB = "https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/matrices/";

export const MATRICES: FillIn[] = [
  {
    label: "matMul(A, B, mod) O(x·y·z)",
    title: "A[x, y] @ B[y, z] = C[x, z], mod mod: C[i][j] = row i of A times column j of B",
    folder: "_matrices",
    file: "matMul",
    ops: [["matMul(A, B, mod) -> C, with A[x, y], B[y, z], C[x, z]", "x*y*z"]],
    githubUrl: GITHUB,
  },
  {
    label: "vecMatMul(vec, M, mod) O(x·y)",
    title: "vec[1, x] @ M[x, y] = res[1, y], mod mod: res[j] = vec times column j of M",
    folder: "_matrices",
    file: "vecMatMul",
    ops: [["vecMatMul(vec, M, mod) -> res, with vec[x], M[x, y], res[y]", "x*y"]],
    githubUrl: GITHUB,
  },
  {
    label: "matPow(M, p, mod) O(x³·log p)",
    title: "M[x, x] ^ p, mod mod (p = 0 gives the identity)",
    folder: "_matrices",
    file: "matPow",
    ops: [["matPow(M, p, mod) -> M^p, with M[x, x]", "x^3*log(p)"]],
    githubUrl: GITHUB,
  },
];
