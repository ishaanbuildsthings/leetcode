"""Checks for geometry/polygonArea.{py,cpp}: fixed cases, reversing flips the sign, and |twice the area| against Pick's
theorem (lattice points counted one by one) on random simple lattice polygons. usage: python3 tests/test_geometry.py"""
import os
import random
import subprocess
import sys
import tempfile
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.dirname(ROOT))


def load_py():
    ns = {}
    exec(open(os.path.join(ROOT, "polygonArea.py")).read(), ns)
    return ns["polygonArea2"]


def area2_by_triangles(pts):
    """twice the signed area, as a sum of signed triangles from the origin, computed with fractions"""
    total = Fraction(0)
    for i in range(len(pts)):
        (x1, y1), (x2, y2) = pts[i], pts[(i + 1) % len(pts)]
        total += Fraction(x1 * y2 - x2 * y1)
    return total


def star_polygon(rng):
    """a simple polygon: random points sorted by angle around their mean (no crossings)"""
    import math
    n = rng.randrange(3, 9)
    pts = list({(rng.randrange(-20, 21), rng.randrange(-20, 21)) for _ in range(n)})
    if len(pts) < 3:
        return None
    cx = sum(x for x, _ in pts) / len(pts)
    cy = sum(y for _, y in pts) / len(pts)
    pts.sort(key=lambda p: math.atan2(p[1] - cy, p[0] - cx))
    return pts


def pick_area2(pts):
    """twice the area by Pick's theorem, 2A = 2I + B - 2: I = lattice points strictly inside (counted one by one), B =
    lattice points on the boundary (gcd of each edge's steps). Exact, and a different route from the formula."""
    from math import gcd
    n = len(pts)
    B = sum(gcd(abs(pts[(i + 1) % n][0] - pts[i][0]), abs(pts[(i + 1) % n][1] - pts[i][1])) for i in range(n))
    xs = [x for x, _ in pts]
    ys = [y for _, y in pts]
    inside = 0
    for px in range(min(xs), max(xs) + 1):
        for py in range(min(ys), max(ys) + 1):
            on_edge = False
            crossings = 0
            for i in range(n):
                (x1, y1), (x2, y2) = pts[i], pts[(i + 1) % n]
                if ((x2 - x1) * (py - y1) == (y2 - y1) * (px - x1) and min(x1, x2) <= px <= max(x1, x2)
                        and min(y1, y2) <= py <= max(y1, y2)):
                    on_edge = True
                    break
                if (y1 > py) != (y2 > py):  # (is px left of the edge at height py, exactly)
                    lhs = (px - x1) * (y2 - y1)
                    rhs = (py - y1) * (x2 - x1)
                    if (lhs < rhs) if y2 > y1 else (lhs > rhs):
                        crossings += 1
            if not on_edge and crossings % 2:
                inside += 1
    return 2 * inside + B - 2


def main():
    f = load_py()
    fixed = [([(0, 0), (4, 0), (4, 3)], 12), ([(0, 0), (4, 3), (4, 0)], -12), ([(0, 0), (1, 0), (0, 1)], 1),
             ([(0, 0), (2, 0), (2, 2), (0, 2)], 8), ([(0, 0), (1, 1), (2, 2)], 0), ([(1, 1), (5, 5)], 0), ([], 0),
             ([(10**9, -10**9), (-10**9, -10**9), (-10**9, 10**9), (10**9, 10**9)], -8 * 10**18)]
    for pts, want in fixed:
        assert f(pts) == want, (pts, f(pts), want)
    rng = random.Random(1)
    cases = []
    for _ in range(300):
        pts = star_polygon(rng)
        if not pts:
            continue
        want = area2_by_triangles(pts)
        assert f(pts) == want and f(pts[::-1]) == -want
        if rng.random() < 0.3 and want != 0:
            assert abs(f(pts)) == pick_area2(pts), (pts, f(pts), pick_area2(pts))
        cases.append(pts)
    print("polygonArea.py: ok")
    # C++: the same cases, compared with the Python answers
    from find_compiler import cxx  # noqa: E402
    with tempfile.TemporaryDirectory() as d:
        main_cpp = os.path.join(d, "t.cpp")
        open(main_cpp, "w").write(f'#include "{os.path.join(ROOT, "polygonArea.cpp")}"\n' + """
int main() {
    int t, n;
    if (!(cin >> t)) return 1;
    while (t--) {
        cin >> n;
        vector<pair<ll, ll>> p(n);
        for (auto& q : p) cin >> q.first >> q.second;
        cout << polygonArea2(p) << "\\n";
    }
}
""")
        exe = os.path.join(d, "t")
        subprocess.run([cxx(), "-std=c++17", "-O2", "-Wall", "-Werror", main_cpp, "-o", exe], check=True)
        allc = [p for p, _ in fixed] + cases
        inp = f"{len(allc)}\n" + "".join(f"{len(p)} " + " ".join(f"{x} {y}" for x, y in p) + "\n" for p in allc)
        out = subprocess.run([exe], input=inp, capture_output=True, text=True, check=True).stdout.split()
        assert [int(v) for v in out] == [f(p) for p in allc]
    print("polygonArea.cpp: ok")


if __name__ == "__main__":
    main()
