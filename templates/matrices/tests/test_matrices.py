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
        ModMatrix = load("ModMatrix", mod)["ModMatrix"]
        for _ in range(150):
            x, y, z = random.randint(1, 20), random.randint(1, 20), random.randint(1, 20)
            A, B = randMat(x, y), randMat(y, z)
            assert (ModMatrix(A) @ ModMatrix(B)).rows == naiveMul(A, B, mod)
            vec = [random.randint(-10**15, 10**15) for _ in range(x)]
            assert vec @ ModMatrix(randMat(1, 1) and A) == naiveMul([vec], A, mod)[0]
            k = random.randint(1, 12)
            M = randMat(k, k)
            p = random.randint(0, 12)
            want = naivePow(M, p, mod)
            assert (ModMatrix(M) ** p).rows == want
            v = [random.randint(-50, 50) for _ in range(k)]
            assert ModMatrix(M).vecPow(v, p) == naiveMul([v], want, mod)[0]
        big = ModMatrix([[1, 1], [1, 0]])
        assert [1, 0] @ big ** 10**18 == big.vecPow([1, 0], 10**18)
    print("ModMatrix ok")


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
        nthTerm = env["nthTerm"]
        for _ in range(200):
            d = random.randint(1, 25)
            coeffs = [random.randint(-10**9, 10**9) for _ in range(d)]
            init = [random.randint(-10**9, 10**9) for _ in range(d)]
            seq = [x % mod for x in init]
            for i in range(d, 120):
                seq.append(sum(coeffs[j] * seq[i - 1 - j] for j in range(d)) % mod)
            for n in random.sample(range(120), 15):
                assert nthTerm(coeffs, init, n) == seq[n], (mod, d, n)
    print("LinearRecurrence ok")


if __name__ == "__main__":
    random.seed(12345)
    testModMatrix()
    testTropical()
    testBool()
    testLinearRecurrence()
