# Stress tests matMul.py, vecMatMul.py and matPow.py against plain big-integer math. Run: python3 test_matrices.py
import os, random

SRC = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
ns = {}
for f in ("matMul", "vecMatMul", "matPow"):
    exec(open(os.path.join(SRC, f + ".py")).read(), ns)
matMul, vecMatMul, matPow = ns["matMul"], ns["vecMatMul"], ns["matPow"]
rng = random.Random(5)


def mul(A, B):  # exact, no mod
    return [[sum(A[i][k] * B[k][j] for k in range(len(B))) for j in range(len(B[0]) if B
        else 0)] for i in range(len(A))]


def rand(r, c, hi):
    return [[rng.randint(-hi, hi) for _ in range(c)] for _ in range(r)]


for trial in range(3000):
    mod = rng.choice([1, 2, 7, 10**9 + 7, 998244353, 2**31, 2**61 - 1])
    x, y, z = rng.randint(1, 6), rng.randint(1, 6), rng.randint(1, 6)
    hi = rng.choice([3, 10**9, 10**18])
    A, B = rand(x, y, hi), rand(y, z, hi)
    assert matMul(A, B, mod) == [[v % mod for v in row] for row in mul(A, B)]
    vec = [rng.randint(-hi, hi) for _ in range(x)]
    assert vecMatMul(vec, A, mod) == [v % mod for v in mul([vec], A)[0]]
    M, p = rand(x, x, hi), rng.randint(0, 12)
    want = [[int(i == j) for j in range(x)] for i in range(x)]
    for _ in range(p):
        want = mul(want, M)
    assert matPow(M, p, mod) == [[v % mod for v in row] for row in want]
assert matPow([[1, 1], [1, 0]], 10, 10**9 + 7) == [[89, 55], [55, 34]]
assert matPow([[2]], 10**18, 10**9 + 7) == [[pow(2, 10**18, 10**9 + 7)]]
for bad in (lambda: matMul([[1, 2]], [[1, 2]], 7), lambda: vecMatMul([1], [[1], [2]], 7),
            lambda: matPow([[1, 2]], 2, 7), lambda: matPow([[1]], -1, 7)):
    try:
        bad()
        assert False
    except ValueError:
        pass
print("matMul, vecMatMul, matPow (Python): all agree with exact math")
