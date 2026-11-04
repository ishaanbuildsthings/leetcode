"""Test the bubble sort templates (templates/bubble-sort/) against a brute force, in Python and C++:

    python3 test_bubble_sort.py

Every array of length <= 7 over up to 3 values (plus random longer ones) is checked: the brute force is a BFS over
adjacent swaps, so it finds the true minimum (to the sorted array, to a given target, to the nearest palindrome).
"""
import importlib.util
import itertools
import os
import random
import subprocess
import sys
import tempfile
from collections import deque

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
DIR = os.path.join(os.path.dirname(HERE), "bubble-sort")
FILES = {"sort": ("MinSwapsToSort", "minAdjacentSwapsToSort"), "target": ("MinSwapsToTarget", "minAdjacentSwapsToTarget"),
         "pal": ("MinSwapsToPalindrome", "minAdjacentSwapsToPalindrome")}


def bfs(start, done):  # the fewest adjacent swaps from start to a tuple passing done, or -1
    seen, todo = {start: 0}, deque([start])
    while todo:
        a = todo.popleft()
        if done(a):
            return seen[a]
        for i in range(len(a) - 1):
            b = a[:i] + (a[i + 1], a[i]) + a[i + 2:]
            if b not in seen:
                seen[b] = seen[a] + 1
                todo.append(b)
    return -1


def cases():
    out = []
    for n in range(0, 8):
        for a in itertools.product(range(3), repeat=n):
            out.append(("sort", a, None))
            out.append(("pal", a, None))
    rng = random.Random(1)
    for _ in range(3000):
        n = rng.randint(0, 7)
        a = tuple(rng.randint(0, 3) for _ in range(n))
        b = list(a)
        rng.shuffle(b)
        if rng.random() < 0.2 and b:  # (sometimes not a rearrangement: -1)
            b[rng.randrange(len(b))] = rng.randint(0, 4)
        out.append(("target", a, tuple(b if rng.random() < 0.95 else b + [0])))
    return out


def expected(mode, a, b):
    if mode == "sort":
        return bfs(a, lambda x: list(x) == sorted(a))
    if mode == "pal":
        return bfs(a, lambda x: x == x[::-1])
    return bfs(a, lambda x: x == b) if sorted(a) == sorted(b) and len(a) == len(b) else -1


def run_py(tests):
    fns = {}
    for mode, (stem, fn) in FILES.items():
        spec = importlib.util.spec_from_file_location(stem, os.path.join(DIR, stem + ".py"))
        m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(m)
        fns[mode] = getattr(m, fn)
    return [fns[mode](list(a)) if mode != "target" else fns[mode](list(a), list(b)) for mode, a, b in tests]


def run_cpp(tests):
    cxx = os.environ.get("CXX") or next(c for c in [f"g++-{v}" for v in range(15, 10, -1)] + ["g++"]
                                        if subprocess.run(["which", c], capture_output=True).returncode == 0)
    src = "#include <bits/stdc++.h>\nusing namespace std;\n" + "".join(
        f'#include "{os.path.join(DIR, stem + ".cpp")}"\n' for stem, _ in FILES.values()) + r'''
int main() {
    int t; cin >> t;
    // (strings too: every template takes them)
    if (minAdjacentSwapsToPalindrome(string("aabb")) != 2 || minAdjacentSwapsToTarget(string("abc"), string("cba")) != 3) return 2;
    while (t--) {
        string mode; int n; cin >> mode >> n;
        vector<long long> a(n); for (auto& x : a) cin >> x;
        if (mode == "sort") cout << minAdjacentSwapsToSort(a) << '\n';
        else if (mode == "pal") cout << minAdjacentSwapsToPalindrome(a) << '\n';
        else {
            int m; cin >> m; vector<long long> b(m); for (auto& x : b) cin >> x;
            cout << minAdjacentSwapsToTarget(a, b) << '\n';
        }
    }
}
'''
    d = tempfile.mkdtemp()
    open(os.path.join(d, "t.cpp"), "w").write(src)
    c = subprocess.run([cxx, "-std=c++17", "-O2", "-Wall", "-o", os.path.join(d, "t"), os.path.join(d, "t.cpp")],
                       capture_output=True, text=True)
    if c.returncode:
        raise RuntimeError(c.stderr)
    inp = [str(len(tests))]
    for mode, a, b in tests:
        inp.append(f"{mode} {len(a)} {' '.join(map(str, a))}" + (f" {len(b)} {' '.join(map(str, b))}" if mode == "target" else ""))
    r = subprocess.run([os.path.join(d, "t")], input="\n".join(inp), capture_output=True, text=True)
    if r.returncode:
        raise RuntimeError(f"exit {r.returncode}: {r.stderr}")
    return [int(x) for x in r.stdout.split()]


def main():
    tests = cases()
    want = [expected(*t) for t in tests]
    bad = 0
    for lang, got in (("py", run_py(tests)), ("cpp", run_cpp(tests))):
        for t, g, w in zip(tests, got, want):
            if g != w:
                print(f"FAIL {lang}: {t[0]}({list(t[1])}{', ' + str(list(t[2])) if t[2] is not None else ''}) = {g}, expected {w}")
                bad += 1
                break
    print("all passed" if not bad else f"{bad} failed", f"({len(tests)} cases per language)")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
