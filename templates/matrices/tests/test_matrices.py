# Stress tests for the Python matrix templates against brute force: python3 test_matrices.py
import os, random, itertools

HERE = os.path.dirname(os.path.abspath(__file__))


def load(name, mod=None):
    src = open(os.path.join(HERE, "..", name + ".py")).read()
    if mod is not None:
        assert "MOD = 10**9 + 7" in src
        src = src.replace("MOD = 10**9 + 7", f"MOD = {mod}", 1)
    env = {}
    exec(src, env)
    return env


def randMat(r, c, lo=-10**12, hi=10**12, zeroRate=0.3):
    return [[0 if random.random() < zeroRate else random.randint(lo, hi) for _ in range(c)] for _ in range(r)]


def naiveMul(A, B, mod):
    return [[sum(A[i][k] * B[k][j] for k in range(len(B))) % mod for j in range(len(B[0]))] for i in range(len(A))]


def naivePow(M, p, mod):
    k = len(M)
    R = [[int(i == j) % mod for j in range(k)] for i in range(k)]
    for _ in range(p):
        R = naiveMul(R, M, mod)
    return R


def testModMatrix():
    for mod in (10**9 + 7, 998244353, 7, 2, 2**31 - 1):
        env = load("MatPowQueries", mod)  # superset of ModMatrix
        ModMatrix, MatPowQueries = env["ModMatrix"], env["MatPowQueries"]
        for _ in range(150):
            x, y, z = random.randint(1, 20), random.randint(1, 20), random.randint(1, 20)
            A, B = randMat(x, y), randMat(y, z)
            assert (ModMatrix(A) @ ModMatrix(B)).rows == naiveMul(A, B, mod)
            vec = [random.randint(-10**15, 10**15) for _ in range(x)]
            assert vec @ ModMatrix(randMat(1, 1) and A) == naiveMul([vec], A, mod)[0]
            assert (ModMatrix(A) + ModMatrix(A)).rows == [[2 * v % mod for v in r] for r in A]
            assert (ModMatrix(A) - ModMatrix(A)).rows == [[0] * y for _ in range(x)]
            assert ModMatrix(A).T.rows == [[v % mod for v in c] for c in zip(*A)]
            k = random.randint(1, 12)
            M = randMat(k, k)
            p = random.randint(0, 12)
            want = naivePow(M, p, mod)
            assert (ModMatrix(M) ** p).rows == want
            v = [random.randint(-50, 50) for _ in range(k)]
            assert ModMatrix(M).vecPow(v, p) == naiveMul([v], want, mod)[0]
            S = [[0] * k for _ in range(k)]
            for i in range(p):
                Pi = naivePow(M, i, mod)
                S = [[(a + b) % mod for a, b in zip(r1, r2)] for r1, r2 in zip(S, Pi)]
            assert ModMatrix(M).powSum(p).rows == S
            pq = MatPowQueries(ModMatrix(M), 40)
            assert pq.query(v, p) == naiveMul([v], want, mod)[0]
        big = ModMatrix([[1, 1], [1, 0]])
        assert MatPowQueries(big, 10**18).query([1, 0], 10**18) == [1, 0] @ big ** 10**18 == big.vecPow([1, 0], 10**18)
    print("ModMatrix + MatPowQueries ok")


def testTropical():
    for name, inf, best in (("MinPlusMatrix", "INF", min), ("MaxPlusMatrix", "NEG_INF", max)):
        env = load(name)
        Mat, INF = env[name], env[inf]
        for _ in range(300):
            k = random.randint(1, 7)
            M = [[INF if random.random() < 0.4 else random.randint(-50, 50) for _ in range(k)] for _ in range(k)]
            p = random.randint(0, 6)
            # brute: best over all walks of exactly p edges
            want = [[INF] * k for _ in range(k)]
            for s in range(k):
                for walk in itertools.product(range(k), repeat=p):
                    nodes = (s,) + walk
                    if any(M[nodes[t]][nodes[t + 1]] == INF for t in range(p)):
                        continue
                    w = sum(M[nodes[t]][nodes[t + 1]] for t in range(p))
                    want[s][nodes[-1]] = w if want[s][nodes[-1]] == INF else best(want[s][nodes[-1]], w)
            assert (Mat(M) ** p).rows == want, (M, p)
            assert Mat(M).vecPow([0] + [INF] * (k - 1), p) == want[0]
            x = random.randint(1, 5)
            A = [[INF if random.random() < 0.3 else random.randint(-9, 9) for _ in range(x)] for _ in range(k)]
            got = (Mat(M) @ Mat(A)).rows
            for i in range(k):
                for j in range(x):
                    opts = [M[i][t] + A[t][j] for t in range(k) if M[i][t] != INF and A[t][j] != INF]
                    assert got[i][j] == (best(opts) if opts else INF)
    print("MinPlusMatrix + MaxPlusMatrix ok")


def testBool():
    BoolMatrix = load("BoolMatrix")["BoolMatrix"]
    for _ in range(300):
        x, y, z = random.randint(1, 140), random.randint(1, 140), random.randint(1, 10)
        A = [[int(random.random() < 0.05) for _ in range(y)] for _ in range(x)]
        B = [[int(random.random() < 0.3) for _ in range(z)] for _ in range(y)]
        want = [[int(any(A[i][k] and B[k][j] for k in range(y))) for j in range(z)] for i in range(x)]
        assert (BoolMatrix(A) @ BoolMatrix(B)).toLists() == want
        vec = [int(random.random() < 0.2) for _ in range(y)]
        assert vec @ BoolMatrix(B) == [int(any(vec[k] and B[k][j] for k in range(y))) for j in range(z)]
        n = random.randint(1, 9)
        edges = [[random.randrange(n), random.randrange(n)] for _ in range(random.randint(0, 12))]
        M = BoolMatrix.fromEdges(n, edges)
        adj = M.toLists()
        p = random.randint(0, 6)
        cur = [[int(i == j) for j in range(n)] for i in range(n)]
        for _ in range(p):
            cur = [[int(any(cur[i][k] and adj[k][j] for k in range(n))) for j in range(n)] for i in range(n)]
        assert (M ** p).toLists() == cur
        reach = [[0] * n for _ in range(n)]
        for s in range(n):
            seen, stack = {s}, [s]
            while stack:
                u = stack.pop()
                for w in range(n):
                    if adj[u][w] and w not in seen:
                        seen.add(w)
                        stack.append(w)
            for w in seen:
                reach[s][w] = 1
        assert M.closure().toLists() == reach
    print("BoolMatrix ok")


def testLinearRecurrence():
    for mod in (10**9 + 7, 998244353, 7, 2):
        env = load("LinearRecurrence", mod)
        nthTerm, bm, guess = env["nthTerm"], env["berlekampMassey"], env["guessNthTerm"]
        for _ in range(200):
            d = random.randint(1, 25)
            coeffs = [random.randint(-10**9, 10**9) for _ in range(d)]
            init = [random.randint(-10**9, 10**9) for _ in range(d)]
            seq = [x % mod for x in init]
            for i in range(d, 120):
                seq.append(sum(coeffs[j] * seq[i - 1 - j] for j in range(d)) % mod)
            for n in random.sample(range(120), 15):
                assert nthTerm(coeffs, init, n) == seq[n], (mod, d, n)
            found = bm(seq[: 2 * d])
            assert len(found) <= d
            for i in range(len(found), 120):
                assert sum(found[j] * seq[i - 1 - j] for j in range(len(found))) % mod == seq[i]
            assert guess(seq[: 2 * d], 119) == seq[119]
    print("LinearRecurrence ok")


def naiveRank(M, mod):
    M = [[x % mod for x in row] for row in M]
    r = 0
    for c in range(len(M[0]) if M else 0):
        piv = next((i for i in range(r, len(M)) if M[i][c]), None)
        if piv is None:
            continue
        M[r], M[piv] = M[piv], M[r]
        inv = pow(M[r][c], mod - 2, mod)
        for i in range(len(M)):
            if i != r and M[i][c]:
                f = M[i][c] * inv % mod
                M[i] = [(a - f * b) % mod for a, b in zip(M[i], M[r])]
        r += 1
    return r


def testGauss():
    for mod in (10**9 + 7, 998244353, 7, 2, 2**31 - 1):
        env = load("GaussianElimination", mod)
        det, rank, inv, solve = env["determinant"], env["matrixRank"], env["inverse"], env["solve"]
        for _ in range(250):
            k = random.randint(1, 6)
            M = randMat(k, k, -5, 5, 0.3 if random.random() < 0.5 else 0.0)
            brute = 0
            for perm in itertools.permutations(range(k)):
                sign = (-1) ** sum(perm[i] > perm[j] for i in range(k) for j in range(i + 1, k))
                term = sign
                for i in range(k):
                    term *= M[i][perm[i]]
                brute += term
            assert det(M) == brute % mod, (M, mod)
            I = inv(M)
            if brute % mod == 0:
                assert I is None
            else:
                assert naiveMul([[x % mod for x in r] for r in M], I, mod) == [[int(i == j) for j in range(k)] for i in range(k)]
            x, y = random.randint(1, 30), random.randint(1, 30)
            A = randMat(x, y, -10**12, 10**12, random.choice([0.0, 0.5, 0.9]))
            if random.random() < 0.3 and x > 1:
                A[-1] = [a + b for a, b in zip(A[0], A[1 % x])]  # force dependence
            assert rank(A) == naiveRank(A, mod)
            b = [random.randint(-10**12, 10**12) for _ in range(x)]
            sol = solve(A, b)
            aug = [row + [v] for row, v in zip(A, b)]
            if naiveRank(aug, mod) > naiveRank(A, mod):
                assert sol is None
            else:
                assert sol is not None and all(sum(a * s for a, s in zip(row, sol)) % mod == v % mod for row, v in zip(A, b))
    print("GaussianElimination ok")


if __name__ == "__main__":
    random.seed(12345)
    testModMatrix()
    testTropical()
    testBool()
    testLinearRecurrence()
    testGauss()
