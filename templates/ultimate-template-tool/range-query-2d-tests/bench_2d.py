"""Times a handful of the 2D / 3D C++ templates, built the way LeetCode builds (optimized, with sanitizers on).

    python3 bench_2d.py                      # the templates as shipped (sanitizers skipped inside them)
    python3 bench_2d.py --checked            # the same files with the skip switched off: what they cost fully sanitized
    python3 bench_2d.py --cxx clang++        # another compiler (default: ../find_compiler.py's)
    python3 bench_2d.py --plain              # no sanitizers at all (Codeforces-style): the skip changes nothing there
    python3 bench_2d.py seg kd               # only the cases whose folder contains one of these

Each case prints build / updates / queries in milliseconds and a checksum (the same in every mode, or something broke).
"""
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
DIR = os.path.join(os.path.dirname(HERE), "range-queries-2d")
sys.path.insert(0, os.path.dirname(HERE))
from find_compiler import cxx  # noqa: E402

HEAD = r"""
typedef long long ll;
static unsigned long long rngState = 88172645463325252ULL;
static inline unsigned long long rnd() {
    rngState ^= rngState << 7;
    rngState ^= rngState >> 9;
    return rngState;
}
static inline ll below(ll n) { return (ll)(rnd() % (unsigned long long)n); }
static double nowMs() { return chrono::duration<double, milli>(chrono::steady_clock::now().time_since_epoch()).count(); }
#define ORDER(a, b) if (a > b) swap(a, b)
"""

# folder -> (struct, body of main): body sets `ll sum` and calls LAP("name") after each phase
CASES = {
    "grid-seg-tree-sum-max": ("SegTree2D", """
        int R = 1000, C = 1000; DS ds(R, C); LAP("build");
        for (int i = 0; i < 200000; i++) ds.pointAssign(below(R), below(C), below(1000000)); LAP("updates");
        for (int i = 0; i < 100000; i++) { int a = below(R), b = below(R), c = below(C), d = below(C); ORDER(a, b); ORDER(c, d);
            sum += ds.rectMax(a, c, b, d) + ds.rectSum(a, c, b, d); } LAP("queries");"""),
    "grid-seg-tree-max": ("SegTree2D", """
        int R = 1000, C = 1000; DS ds(R, C); LAP("build");
        for (int i = 0; i < 200000; i++) ds.pointAssign(below(R), below(C), below(1000000)); LAP("updates");
        for (int i = 0; i < 200000; i++) { int a = below(R), b = below(R), c = below(C), d = below(C); ORDER(a, b); ORDER(c, d);
            sum += ds.rectMax(a, c, b, d); } LAP("queries");"""),
    "grid-bit-sum": ("Fenwick2D", """
        int R = 1000, C = 1000; DS ds(R, C); LAP("build");
        for (int i = 0; i < 300000; i++) ds.pointAdd(below(R), below(C), below(1000)); LAP("updates");
        for (int i = 0; i < 300000; i++) { int a = below(R), b = below(R), c = below(C), d = below(C); ORDER(a, b); ORDER(c, d);
            sum += ds.rectSum(a, c, b, d); } LAP("queries");"""),
    "grid-bit-corner-max-ltelte": ("CornerMaxFenwick2D", """
        int R = 1000, C = 1000; DS ds(R, C); LAP("build");
        for (int i = 0; i < 300000; i++) ds.pointChmax(below(R), below(C), below(1000000)); LAP("updates");
        for (int i = 0; i < 300000; i++) sum += ds.maxLteLte(below(R), below(C)); LAP("queries");"""),
    "grid-kept-tags-max": ("RectChmaxRectMax2D", """
        int R = 1000, C = 1000; DS ds(R, C); LAP("build");
        for (int i = 0; i < 100000; i++) { int a = below(R), b = below(R), c = below(C), d = below(C); ORDER(a, b); ORDER(c, d);
            ds.rectChmax(a, c, b, d, below(1000000)); } LAP("updates");
        for (int i = 0; i < 100000; i++) { int a = below(R), b = below(R), c = below(C), d = below(C); ORDER(a, b); ORDER(c, d);
            sum += ds.rectMax(a, c, b, d); } LAP("queries");"""),
    "grid-sparse-table-min": ("SparseTable2D", """
        int R = 400, C = 400; vector<vector<ll>> g(R, vector<ll>(C)); for (auto& row : g) for (auto& x : row) x = below(1000000000);
        DS ds(g); LAP("build");
        LAP("updates");
        for (int i = 0; i < 1000000; i++) { int a = below(R), b = below(R), c = below(C), d = below(C); ORDER(a, b); ORDER(c, d);
            sum += ds.rectMin(a, c, b, d); } LAP("queries");"""),
    "points-seg-tree-max": ("PointsSegTree2D", """
        int n = 100000; vector<pair<ll, ll>> pts(n); for (auto& p : pts) p = {below(2000000000) - 1000000000, below(2000000000) - 1000000000};
        DS ds(pts); LAP("build");
        for (int i = 0; i < 100000; i++) { auto& p = pts[below(n)]; ds.pointAssign(p.first, p.second, below(1000000)); } LAP("updates");
        for (int i = 0; i < 100000; i++) { ll a = pts[below(n)].first, b = pts[below(n)].first, c = pts[below(n)].second, d = pts[below(n)].second;
            ORDER(a, b); ORDER(c, d); ll got = ds.rectMax(a, c, b, d); sum += got == DS::NO_MAX ? -1 : got; } LAP("queries");"""),
    "points-bit-sum": ("PointsFenwick2D", """
        int n = 100000; vector<pair<ll, ll>> pts(n); for (auto& p : pts) p = {below(2000000000) - 1000000000, below(2000000000) - 1000000000};
        DS ds(pts); LAP("build");
        for (int i = 0; i < 200000; i++) { auto& p = pts[below(n)]; ds.pointAdd(p.first, p.second, below(1000)); } LAP("updates");
        for (int i = 0; i < 200000; i++) { ll a = pts[below(n)].first, b = pts[below(n)].first, c = pts[below(n)].second, d = pts[below(n)].second;
            ORDER(a, b); ORDER(c, d); sum += ds.rectSum(a, c, b, d); } LAP("queries");"""),
    "points-bit-corner-max-ltelte": ("PointsCornerMaxFenwick2D", """
        int n = 100000; vector<pair<ll, ll>> pts(n); for (auto& p : pts) p = {below(2000000000) - 1000000000, below(2000000000) - 1000000000};
        DS ds(pts); LAP("build");
        for (int i = 0; i < 200000; i++) { auto& p = pts[below(n)]; ds.pointChmax(p.first, p.second, below(1000000)); } LAP("updates");
        for (int i = 0; i < 200000; i++) { ll got = ds.maxLteLte(pts[below(n)].first, pts[below(n)].second); sum += got == DS::NO_MAX ? -1 : got; }
        LAP("queries");"""),
    "points-kd-tree-sum-max": ("KdTree2D", """
        int n = 100000; vector<pair<ll, ll>> pts(n); for (auto& p : pts) p = {below(2000000000) - 1000000000, below(2000000000) - 1000000000};
        DS ds(pts); LAP("build");
        for (int i = 0; i < 20000; i++) { ll a = pts[below(n)].first, b = pts[below(n)].first, c = pts[below(n)].second, d = pts[below(n)].second;
            ORDER(a, b); ORDER(c, d); ds.rectAdd(a, c, b, d, below(1000)); } LAP("updates");
        for (int i = 0; i < 20000; i++) { ll a = pts[below(n)].first, b = pts[below(n)].first, c = pts[below(n)].second, d = pts[below(n)].second;
            ORDER(a, b); ORDER(c, d); sum += ds.rectSum(a, c, b, d); } LAP("queries");"""),
    "online-seg-tree-max": ("DynamicSegTree2D", """
        ll lim = 1000000000; DS ds(-lim, lim, -lim, lim); LAP("build");
        vector<pair<ll, ll>> pts(50000); for (auto& p : pts) { p = {below(2 * lim) - lim, below(2 * lim) - lim}; ds.pointAssign(p.first, p.second, below(1000000)); }
        LAP("updates");
        for (int i = 0; i < 50000; i++) { ll a = pts[below(50000)].first, b = pts[below(50000)].first, c = pts[below(50000)].second, d = pts[below(50000)].second;
            ORDER(a, b); ORDER(c, d); ll got = ds.rectMax(a, c, b, d); sum += got == DS::NO_MAX ? -1 : got; } LAP("queries");"""),
    "3d-seg-tree-max": ("SegTree3D", """
        int n = 60; DS ds(n, n, n); LAP("build");
        for (int i = 0; i < 200000; i++) ds.pointAssign(below(n), below(n), below(n), below(1000000)); LAP("updates");
        for (int i = 0; i < 200000; i++) { int a = below(n), b = below(n), c = below(n), d = below(n), e = below(n), f = below(n); ORDER(a, b); ORDER(c, d); ORDER(e, f);
            ll got = ds.boxMax(a, c, e, b, d, f); sum += got == DS::NO_MAX ? -1 : got; } LAP("queries");"""),
}


def source(folder, struct, body):
    return (f'#include "{os.path.join(DIR, folder, "template.cpp")}"\n' + HEAD + f"using DS = {struct}<long long>;\n" + """
int main() {
    unsigned long long sum = 0;
    double last = nowMs();
    auto lap = [&](const char* name) { double t = nowMs(); printf("%s %.1f ", name, t - last); last = nowMs(); };
#define LAP(name) lap(name)
""" + body + """
    printf("checksum %llu\\n", sum);
    return 0;
}
""")


def main():
    argv = sys.argv[1:]
    compiler = argv[argv.index("--cxx") + 1] if "--cxx" in argv else cxx()
    flags = ["-std=c++17", "-O2"]
    if "--plain" not in argv:
        flags += ["-fsanitize=address,undefined"]
    if "--checked" in argv:
        flags += ["-DLEETCODE_NO_SANITIZE="]  # the templates only define it when nobody else has
    names = [a for i, a in enumerate(argv) if not a.startswith("--") and (i == 0 or argv[i - 1] != "--cxx")]
    print(f"{compiler} {' '.join(flags)}")
    with tempfile.TemporaryDirectory() as tmp:
        for folder, (struct, body) in CASES.items():
            if names and not any(n in folder for n in names):
                continue
            src, exe = os.path.join(tmp, folder + ".cpp"), os.path.join(tmp, folder)
            open(src, "w").write(source(folder, struct, body))
            comp = subprocess.run([compiler, *flags, "-o", exe, src], capture_output=True, text=True)
            if comp.returncode != 0:
                print(f"{folder:32} does not compile: {comp.stderr[:600]}")
                continue
            run = subprocess.run([exe], capture_output=True, text=True, env={**os.environ, "ASAN_OPTIONS": "detect_leaks=0"})
            print(f"{folder:32} {run.stdout.strip() if run.returncode == 0 else 'crashed: ' + run.stderr[-400:]}")


if __name__ == "__main__":
    main()
