"""Tests primes/Primes.{py,cpp} the way the Primes tab serves it: for every single op and for all of them, the file is
trimmed to the ticked ops (string-tests/eertree_strip.py, the site's rules), checked against brute force (trial
division, a plain sieve, known prime counts), and the C++ trim, built with sanitizers, must print what Python does.

    python3 test_primes.py               # every trim
    python3 test_primes.py countPrimes   # just these trims ("all" = the whole file)
"""
import os
import random
import subprocess
import sys
from math import isqrt, prod

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "string-tests"))
from eertree_strip import strip  # noqa: E402

SRC = os.path.join(os.path.dirname(HERE), "primes")
OPS = ["isPrime", "primeFactorize", "allFactors", "sieveIsPrime", "sieveSmallestPrimeFactor", "sieveFactorize",
       "sieveFactorizeUpToNSquared", "sievePrimes", "primesUpTo", "forEachPrimeUpTo", "primesInRange", "countPrimes"]
SIEVE_N = 3000
rnd = random.Random(2)


def trial(x):
    res, p = [], 2
    while p * p <= x:
        e = 0
        while x % p == 0:
            x //= p
            e += 1
        if e:
            res.append((p, e))
        p += 1
    if x > 1:
        res.append((x, 1))
    return res


PLAIN = [x for x in range(200001) if x >= 2 and all(x % p for p in range(2, isqrt(x) + 1))]
PLAIN_SET = set(PLAIN)
# big values: known primes, Carmichael numbers, semiprimes of big primes, prime powers, products near 2^64
BIG_PRIMES = [2**61 - 1, 1000000000000000003, 999999999989, 18446744073709551557, 4294967291, 1000000007]
BIG = BIG_PRIMES + [561, 1105, 1729, 2465, 3215031751, 2**64 - 1, (2**31 - 1) ** 2, 1000000007 * 998244353,
                    4294967291 * 4294967279, 2**63, 3**40, 999999999989 * 17]


def cases(op):
    """(call args, exact answer) pairs; answers as plain Python values"""
    out = []
    if op == "isPrime":
        out += [((x,), x in PLAIN_SET) for x in [rnd.randint(0, 200000) for _ in range(300)] + list(range(0, 50))]
        out += [((x,), x in BIG_PRIMES) for x in BIG]
    elif op in ("primeFactorize", "allFactors"):
        xs = [rnd.randint(1, 10**6) for _ in range(150)] + [1, 2, 4, 97] + BIG
        for x in xs:
            if op == "primeFactorize":
                out.append(((x,), None))
            elif x < 10**13 or x in BIG_PRIMES:
                out.append(((x,), None))
    elif op == "sieveIsPrime":
        out += [((x,), x in PLAIN_SET) for x in range(0, SIEVE_N + 1)]
    elif op == "sieveSmallestPrimeFactor":
        out += [((x,), trial(x)[0][0]) for x in range(2, SIEVE_N + 1)]
    elif op == "sieveFactorize":
        out += [((x,), trial(x)) for x in range(1, SIEVE_N + 1)]
    elif op == "sieveFactorizeUpToNSquared":
        xs = list(range(1, 200)) + [rnd.randint(1, SIEVE_N * SIEVE_N) for _ in range(300)] + [SIEVE_N * SIEVE_N, 2999 * 2999, 2999 * 2]
        out += [((x,), trial(x)) for x in xs]
    elif op == "sievePrimes":
        out.append(((), [p for p in PLAIN if p <= SIEVE_N]))
    elif op in ("primesUpTo", "forEachPrimeUpTo"):
        for n in [0, 1, 2, 3, 10, 100, 1000, 200000, rnd.randint(0, 200000), 2**18 + 1, 2 * 2**18 + 5]:
            out.append(((n,), [p for p in PLAIN if p <= n]))
    elif op == "primesInRange":
        for _ in range(60):
            lo = rnd.randint(-5, 199000)
            hi = lo + rnd.randint(-3, 1000)
            out.append(((lo, hi), [p for p in PLAIN if lo <= p <= hi]))
        out.append(((10**12, 10**12 + 100), [1000000000039, 1000000000061, 1000000000063, 1000000000091]))
    elif op == "countPrimes":
        import bisect
        for n in list(range(0, 40)) + [rnd.randint(0, 200000) for _ in range(60)] + [200000]:
            out.append(((n,), bisect.bisect_right(PLAIN, n)))
        out += [((10**9,), 50847534)]
    return out


def checkFactor(x, got):
    assert prod(p**e for p, e in got) == x and all(e >= 1 for _, e in got), (x, got)
    assert [p for p, _ in got] == sorted({p for p, _ in got}), (x, got)
    for p, _ in got:
        assert p in BIG_PRIMES or (p <= 200000 and p in PLAIN_SET) or p == trial(p)[0][0], (x, p)


def run_py(ns, op, args):
    if op.startswith("sieve"):
        s = ns["PrimeSieve"](SIEVE_N)
        if op == "sievePrimes":
            return s.primes
        method = {"sieveIsPrime": "isPrime", "sieveSmallestPrimeFactor": "smallestPrimeFactor", "sieveFactorize": "factorize",
                  "sieveFactorizeUpToNSquared": "factorizeUpToNSquared"}[op]
        return getattr(s, method)(*args)
    if op == "forEachPrimeUpTo":
        got = []
        ns[op](*args, got.append)
        return got
    return ns[op](*args)



def fmt2(v):
    if isinstance(v, bool):
        return "1" if v else "0"
    if isinstance(v, int):
        return str(v)
    return " ".join(f"{x[0]}^{x[1]}" if isinstance(x, tuple) else str(x) for x in v)


CPP_CALL = {
    "isPrime": lambda a: f"cout << isPrime({a[0]}ULL);",
    "primeFactorize": lambda a: f"{{ auto r = primeFactorize({a[0]}ULL); for (size_t i = 0; i < r.size(); i++) cout << (i ? \" \" : \"\") << r[i].first << \"^\" << r[i].second; }}",
    "allFactors": lambda a: f"{{ auto r = allFactors({a[0]}ULL); for (size_t i = 0; i < r.size(); i++) cout << (i ? \" \" : \"\") << r[i]; }}",
    "sieveIsPrime": lambda a: f"cout << sieve.isPrime({a[0]});",
    "sieveSmallestPrimeFactor": lambda a: f"cout << sieve.smallestPrimeFactor({a[0]});",
    "sieveFactorize": lambda a: f"{{ auto r = sieve.factorize({a[0]}); for (size_t i = 0; i < r.size(); i++) cout << (i ? \" \" : \"\") << r[i].first << \"^\" << r[i].second; }}",
    "sieveFactorizeUpToNSquared": lambda a: f"{{ auto r = sieve.factorizeUpToNSquared({a[0]}LL); for (size_t i = 0; i < r.size(); i++) cout << (i ? \" \" : \"\") << r[i].first << \"^\" << r[i].second; }}",
    "sievePrimes": lambda a: "{ for (size_t i = 0; i < sieve.primes.size(); i++) cout << (i ? \" \" : \"\") << sieve.primes[i]; }",
    "primesUpTo": lambda a: f"{{ auto r = primesUpTo({a[0]}LL); for (size_t i = 0; i < r.size(); i++) cout << (i ? \" \" : \"\") << r[i]; }}",
    "forEachPrimeUpTo": lambda a: f"{{ bool first = true; forEachPrimeUpTo({a[0]}LL, [&](ll p) {{ cout << (first ? \"\" : \" \") << p; first = false; }}); }}",
    "primesInRange": lambda a: f"{{ auto r = primesInRange({a[0]}LL, {a[1]}LL); for (size_t i = 0; i < r.size(); i++) cout << (i ? \" \" : \"\") << r[i]; }}",
    "countPrimes": lambda a: f"cout << countPrimes({a[0]}LL);",
}


def main():
    py = open(os.path.join(SRC, "Primes.py")).read()
    cpp = open(os.path.join(SRC, "Primes.cpp")).read()
    sets = [[op] for op in OPS] + [OPS]
    want = [a for a in sys.argv[1:]]  # optional: only these trims ("all" for the full file)
    if want:
        sets = [c for c in sets if (c[0] if len(c) == 1 else "all") in want]
    os.makedirs("/tmp/primes-test", exist_ok=True)
    total = 0
    for chosen in sets:
        ns = {}
        exec(strip(py, set(chosen)), ns)
        lines, expected = [], []
        for op in chosen:
            for args, exact in cases(op):
                got = run_py(ns, op, args)
                if op == "primeFactorize":
                    checkFactor(args[0], got)
                elif op == "allFactors":
                    x = args[0]
                    if x < 10**7:
                        divs = [1]
                        for q, e in trial(x):
                            divs = [d * q**k for d in divs for k in range(e + 1)]
                        assert got == sorted(divs), (x, got)
                    else:
                        assert got == sorted(got) and all(x % d == 0 for d in got) and got[0] == 1 and got[-1] == x
                else:
                    assert got == exact, (op, args, got, exact)
                lines.append(CPP_CALL[op](args) + ' cout << "\\n";')
                expected.append(fmt2(got))
                total += 1
        name = chosen[0] if len(chosen) == 1 else "all"
        path = f"/tmp/primes-test/{name}"
        needsSieve = any(op.startswith("sieve") for op in chosen)
        main_ = "int main() {\n" + (f"    PrimeSieve sieve({SIEVE_N});\n" if needsSieve else "") + "\n".join("    " + l for l in lines) + "\n}\n"
        open(path + ".cpp", "w").write(strip(cpp, set(chosen)) + "\n" + main_)
        r = subprocess.run(["g++", "-std=c++17", "-O1", "-Wall", "-fsanitize=address,undefined", "-o", path, path + ".cpp"], capture_output=True, text=True)
        if r.returncode or "warning" in r.stderr:
            sys.exit(f"FAIL cpp {name}: compile\n{r.stderr[:2000]}")
        got = subprocess.run([path], capture_output=True, text=True, timeout=300).stdout.split("\n")[:-1]
        if got != expected:
            k = next(k for k in range(len(expected)) if k >= len(got) or got[k] != expected[k])
            sys.exit(f"FAIL cpp {name}: line {k} '{lines[k][:80]}' gave {got[k][:80] if k < len(got) else 'nothing'}, python {expected[k][:80]}")
        print(f"PASS {name}", flush=True)
    print(f"all trims: python matches brute force and C++ matches python ({total} calls)")


if __name__ == "__main__":
    main()
