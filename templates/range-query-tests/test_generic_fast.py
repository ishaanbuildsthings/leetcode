"""Tests the fast generics against the generics they came from: fills in each template's commented example, replays the
same random operations on both, and compares every answer.

    python3 test_generic_fast.py                # every generic
    python3 test_generic_fast.py Treap.complex  # those with this in the name
    python3 test_generic_fast.py --bench        # time them under LeetCode's sanitizers (needs clang++)
"""

import concurrent.futures
import os
import re
import subprocess
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
DIR = os.environ.get("GENERIC_DIR") or os.path.join(os.path.dirname(HERE), "segment-trees", "generic")
TREES = ("LazyDynamicSeg", "DynamicSeg", "LazySeg", "Seg", "PersistentLazyTreap", "PersistentTreap", "LazyTreap", "Treap")
SANITIZE = ["-fsanitize=address,undefined", "-fno-sanitize-recover=all"]


def filled_in(text, tree):
    """The template with its commented example switched on."""
    start = re.search(rf"^(// A vector whose|// Every op copies|struct {tree} \{{)", text, re.M).start()
    head = re.sub(r"^( +)// (?!This is NOT)", r"\1", text[:start], flags=re.M)
    return head + text[start:]


def fields(text, name):
    m = re.search(rf"^struct {name} \{{\n(.*?)^\}};", text, re.M | re.S)
    found = []
    for line in m[1].split("\n") if m else []:
        f = re.match(r"\s+(long long|int|char|bool) ([\w, \[\]]+);", line)
        if f:
            found += [(f[1], x.strip()) for x in f[2].split(",")]
    return found


def show(text):
    if re.search(r"^using Node = long long;", text, re.M):
        return "put(x);"
    if re.search(r"^using Node = pair", text, re.M):
        return "put(x.first); put(x.second);"
    out = []
    for _, field in fields(text, "Node"):
        if "[" in field:
            name, size = field[:-1].split("[")
            out.append(f"for (int c = 0; c < {size}; c++) put(x.{name}[c]);")
        else:
            out.append(f"put(x.{field});")
    return " ".join(out)


def tag_maker(text):
    if re.search(r"^using Tag = long long;", text, re.M):
        return "Tag g = rr(-50, 50); return g;"
    made = {"add": "rr(-50, 50)", "assign": "R() % 2", "letter": "'a' + R() % 26", "shift": "R() % 26"}
    return "Tag g; " + " ".join(f"g.{f} = {made[f]};" for _, f in fields(text, "Tag")) + " return g;"


DRIVER = r"""
#include <chrono>
static mt19937_64 R(SEED);
static long long rr(long long a, long long b) { return a + (long long)(R() % (unsigned long long)(b - a + 1)); }
static unsigned long long H = 1469598103934665603ULL;
template <typename I> static void put(I x) { H = (H ^ (unsigned long long)x) * 1099511628211ULL; }
static void see(const Node& x) { SHOW }
static RawVal value() { return sizeof(RawVal) == 1 ? RawVal('a' + R() % 26) : RawVal(rr(-1000, 1000)); }
#if LAZY
static Tag tag() { MAKE_TAG }
#endif
int main() {
    int n = N, q = Q;
    auto start = chrono::steady_clock::now();
#if DYNAMIC
    const long long step = 1000000000000LL;
    TREE s(0, 1001 * step);
    auto at = [&]() { return rr(0, 1000) * step + rr(0, 3); };
    for (int i = 0; i < q; i++) {
        long long l = at(), r = at();
        if (l > r) swap(l, r);
        int kind = R() % KINDS;
        if (kind == 0) s.pointAssign(l, value());
        else if (kind == 1) see(s.pointGet(l));
        else if (kind == 2) see(s.rangeQuery(l, r));
#if LAZY
        else if (kind == 3) s.rangeUpdate(l, r, tag());
#endif
        else see(s.rangeQueryAll());
    }
#elif TREAP
    vector<RawVal> a(n);
    for (auto& x : a) x = value();
    TREE s(a);
    vector<TREE> olds;
    for (int i = 0; i < q; i++) {
        int m = s.size();
        long long l = rr(0, m - 1), r = rr(0, m - 1);
        if (l > r) swap(l, r);
        int kind = R() % 15;
        if (kind == 0) see(s.pointGet(l));
        else if (kind == 1) s.pointAssign(l, value());
        else if (kind == 2) { long long i = rr(0, m); s.insertAt(i, value()); }
        else if (kind == 3) s.append(value());
        else if (kind == 4) { if (m > 2) s.eraseAt(l); }
        else if (kind == 5) see(s.rangeQueryAll());
#if LAZY
        else if (kind == 6) s.rangeUpdate(l, r, tag());
#endif
#if REV
        else if (kind == 7) s.rangeReverse(l, r);
#endif
        else if (kind == 8) s.rangeRotateLeft(l, r, rr(0, 1000));
        else if (kind == 9) s.rangeRotateRight(l, r, rr(0, 1000));
        else if (kind == 10) { if (STRUCTURAL && r - l + 1 < m) { auto piece = s.cut(l, r); s.paste(rr(0, s.size()), piece); } }
        else if (kind == 11) { if (STRUCTURAL && m > 2) { auto parts = s.split(rr(1, m - 1)); auto b = parts.second; auto c = parts.first; c.merge(b); s = c; } }
        else if (kind == 12) { if (STRUCTURAL && l > 0 && r < m - 1) { auto [x, y, z] = s.trisect(l, r); x.merge(y); x.merge(z); s = x; } }
#if PERSISTENT
        else if (kind == 13) { if (STRUCTURAL && olds.size() < 20) olds.push_back(s.copy()); else if (!olds.empty()) { auto& o = olds[R() % olds.size()]; see(o.rangeQuery(0, o.size() - 1)); } }
#endif
        else see(s.rangeQuery(l, r));
    }
#else
    vector<RawVal> a(n);
    for (auto& x : a) x = value();
    TREE s(a);
    for (int i = 0; i < q; i++) {
        int l = rr(0, n - 1), r = rr(0, n - 1);
        if (l > r) swap(l, r);
        int kind = R() % KINDS;
        if (kind == 0) s.pointAssign(l, value());
        else if (kind == 1) see(s.pointGet(l));
        else if (kind == 2) see(s.rangeQuery(l, r));
#if LAZY
        else if (kind == 3) s.rangeUpdate(l, r, tag());
#endif
        else see(s.rangeQueryAll());
    }
#endif
    cerr << chrono::duration<double, milli>(chrono::steady_clock::now() - start).count() << "\n";
    cout << H << "\n";
}
"""


def program(name, seed, n, q, structural=1):
    text = open(os.path.join(DIR, name)).read()
    tree = next(t for t in TREES if re.search(rf"^struct {t} \{{", text, re.M))
    code = filled_in(text, tree)
    lazy, dynamic, treap = "Tag" in tree or "Lazy" in tree, "Dynamic" in tree, "Treap" in tree
    defs = {"TREE": tree, "SEED": f"{seed}ULL", "N": n, "Q": q, "LAZY": int(lazy), "DYNAMIC": int(dynamic), "TREAP": int(treap),
            "REV": int(".norev" not in name), "PERSISTENT": int("Persistent" in tree), "KINDS": 5 if lazy else 4,
            "STRUCTURAL": structural}
    driver = DRIVER.replace("SHOW", show(code)).replace("MAKE_TAG", tag_maker(code) if lazy else "")
    return "".join(f"#define {k} {v}\n" for k, v in defs.items() if k in ("TREE", "LAZY", "DYNAMIC", "TREAP", "REV", "PERSISTENT")) + code + \
        re.sub(r"\b(SEED|Q|N|KINDS|STRUCTURAL)\b", lambda m: str(defs[m[1]]), driver)


def run(name, seed, n, q, compiler, flags, tmp, structural=1):
    tag = re.sub(r"\W", "_", f"{name}_{seed}_{n}_{compiler}_{len(flags)}")
    src, exe = os.path.join(tmp, tag + ".cpp"), os.path.join(tmp, tag)
    open(src, "w").write(program(name, seed, n, q, structural))
    comp = subprocess.run([compiler, "-std=c++17", "-O2", "-w", *flags, "-o", exe, src], capture_output=True, text=True)
    if comp.returncode:
        raise RuntimeError(f"{name}: compile error\n{comp.stderr[:1500]}")
    got = subprocess.run([exe], capture_output=True, text=True, timeout=300)
    if got.returncode:
        raise RuntimeError(f"{name}: exited {got.returncode}: {got.stderr[:800]}")
    return got.stdout.strip(), float(got.stderr.strip().split("\n")[-1])


def check(base, tmp):
    fast = base[:-4] + ".fast.cpp"
    for seed in (1, 2, 3):
        n, q = (40, 4000) if seed < 3 else (1000, 3000)
        want, _ = run(base, seed, n, q, "g++", [], tmp)
        gcc, _ = run(fast, seed, n, q, "g++", [], tmp)
        checked = run(fast, seed, n, q, "clang++", SANITIZE, tmp)[0] if seed == 1 else want
        if want != gcc or want != checked:
            return f"FAIL  {fast}: seed {seed} gave {gcc} and {checked}, expected {want}"
    return f"PASS  {fast}"


def bench(base, tmp):
    fast = base[:-4] + ".fast.cpp"
    persistent, complex_ = "Persistent" in base, ".complex" in base
    n, q = (200000, 40000 if complex_ else 200000) if persistent else (200000, 500000 if complex_ else 1000000)
    if "Treap" in base and not persistent:
        q //= 3
    out = []
    for name in (base, fast):
        times = []
        for _ in range(3):
            answer, ms = run(name, 7, n, q, "clang++", SANITIZE, tmp)
            times.append(ms)
        out.append((sorted(times)[1], answer))
    assert out[0][1] == out[1][1], f"{base}: answers differ"
    return f"{base[:-4]:42} {out[0][0]:8.0f} {out[1][0]:8.0f}  {100 * (out[1][0] / out[0][0] - 1):+.0f}%"


def main():
    args = sys.argv[1:]
    want = [x for x in args if not x.startswith("--")]
    bases = sorted(f for f in os.listdir(DIR) if f.endswith(".cpp") and not f.endswith((".fast.cpp", ".debug.cpp")))
    bases = [f for f in bases if not want or any(x in f for x in want)]
    with tempfile.TemporaryDirectory() as tmp:
        if "--bench" in args:
            print(f"{'template':42} {'default':>8} {'fast':>8}")
            for base in bases:
                print(bench(base, tmp), flush=True)
            return
        with concurrent.futures.ThreadPoolExecutor(os.cpu_count() or 2) as pool:
            lines = list(pool.map(lambda b: check(b, tmp), bases))
    print("\n".join(lines))
    failed = sum(line.startswith("FAIL") for line in lines)
    print(f"\n{len(lines) - failed} of {len(lines)} fast generics match")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
