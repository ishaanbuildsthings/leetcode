"""Every commented generic example, switched on, against a real brute force (C++ files, sanitized when the compiler can)."""
import os, re, sys, subprocess, tempfile, concurrent.futures
HERE = os.path.dirname(os.path.abspath(__file__)); SNAP = os.path.dirname(HERE)
sys.path[:0] = [HERE, SNAP]; sys.dont_write_bytecode = True
from find_compiler import cxx, sanitize_flags
import test_generic_fast as F
G = SNAP + '/generic-seg-trees'
TMPL = r'''
#include <chrono>
static mt19937_64 R(SEED);
static long long rr(long long a, long long b) { return a + (long long)(R() % (unsigned long long)(b - a + 1)); }
static unsigned long long H;
template <typename I> static void put(I x) { H = (H ^ (unsigned long long)x) * 1099511628211ULL; }
static unsigned long long hv(const Node& x) { H = 1469598103934665603ULL; SHOW return H; }
static RawVal value() { return sizeof(RawVal) == 1 ? RawVal('a' + R() % 26) : RawVal(rr(-1000, 1000)); }
TAGFN
static Node fold(const vector<Node>& v, int l, int r) { Node a = v[l]; for (int i = l + 1; i <= r; i++) a = combine(a, v[i]); return a; }
#define CK(got, exp, what) do { if (hv(got) != hv(exp)) { cout << "MISMATCH " << what << " step " << step << " l=" << l << " r=" << r << "\n"; return 1; } } while (0)
LEAFDEF
int main() {
 for (int test = 0; test < 200; test++) {
#if DYNAMIC
  long long lo = test % 2 ? -7 : 0; int n = rr(1, 30); long long hi = lo + n - 1;
  vector<Node> ns(n); for (int i = 0; i < n; i++) ns[i] = blank(lo + i, lo + i);
  TREE s(lo, hi); long long off = lo;
#else
  int n = rr(1, 30); vector<RawVal> a(n); for (auto& x : a) x = value();
  vector<Node> ns(n); for (int i = 0; i < n; i++) ns[i] = LF(a[i], i);
  TREE s(a); long long off = 0;
#endif
  vector<pair<TREE, vector<Node>>> olds;
  for (int step = 0; step < 250; step++) {
   int m = ns.size(); int l = rr(0, m - 1), r = rr(0, m - 1); if (l > r) swap(l, r);
   int kind = R() % 16;
   if (kind == 0) { Node g = s.pointGet(l + off); CK(g, ns[l], "pointGet"); }
   else if (kind == 1) { CK(s.rangeQuery(l + off, r + off), fold(ns, l, r), "rangeQuery"); }
   else if (kind == 2) { CK(s.rangeQueryAll(), fold(ns, 0, m - 1), "rangeQueryAll"); }
#if !STATIC
   else if (kind == 3) { RawVal v = value(); s.pointAssign(l + off, v); ns[l] = LF(v, l + off); }
#endif
#if LAZY
   else if (kind == 4 || kind == 5) { Tag t = tag(); s.rangeUpdate(l + off, r + off, t); for (int i = l; i <= r; i++) ns[i] = ::apply(ns[i], (const Tag&)t); }
#endif
#if TREAP
   else if (kind == 6) { int i = rr(0, m); RawVal v = value(); s.insertAt(i, v); ns.insert(ns.begin() + i, LF(v, i)); }
   else if (kind == 7) { RawVal v = value(); s.append(v); ns.push_back(LF(v, m)); }
   else if (kind == 8) { if (m > 1) { s.eraseAt(l); ns.erase(ns.begin() + l); } }
   else if (kind == 9 || kind == 10) { long long k = rr(-40, 40); if (kind == 9) s.rangeRotateLeft(l, r, k); else s.rangeRotateRight(l, r, k);
     int len = r - l + 1; long long kk = ((kind == 9 ? k : -k) % len + len) % len; std::rotate(ns.begin() + l, ns.begin() + l + kk, ns.begin() + r + 1); }
#if REV
   else if (kind == 11) { s.rangeReverse(l, r); for (int i = l; i <= r; i++) ns[i] = reverse(ns[i]); std::reverse(ns.begin() + l, ns.begin() + r + 1); }
#endif
   else if (kind == 12) { if (r - l + 1 < m) { auto p = s.cut(l, r); vector<Node> pc(ns.begin() + l, ns.begin() + r + 1); ns.erase(ns.begin() + l, ns.begin() + r + 1); int i = rr(0, ns.size()); s.paste(i, p); ns.insert(ns.begin() + i, pc.begin(), pc.end()); } }
   else if (kind == 13) { int k = rr(0, m); auto parts = s.split(k); auto x = parts.first; auto y = parts.second; x.merge(y); s = x; }
   else if (kind == 14) { auto [x, y, z] = s.trisect(l, r); x.merge(y); x.merge(z); s = x; }
#if PERSISTENT
   else if (kind == 15) { if (olds.size() < 12) { if (R() % 2) olds.push_back({s.copy(), ns}); else olds.push_back({s.copy(l, r), vector<Node>(ns.begin() + l, ns.begin() + r + 1)}); }
     else { auto& o = olds[R() % olds.size()]; CK(o.first.rangeQueryAll(), fold(o.second, 0, (int)o.second.size() - 1), "old version"); } }
#endif
#endif
  }
 }
 cout << "OK\n";
}
'''
def build(name):
    text = open(f'{G}/{name}').read()
    tree = next(t for t in F.TREES if re.search(rf"^struct {t} \{{", text, re.M))
    code = F.filled_in(text, tree)
    lazy = 'Lazy' in tree; dyn = 'Dynamic' in tree; treap = 'Treap' in tree
    two = re.search(r'^(?:LEETCODE_NO_SANITIZE )?Node (leaf|baseFn)\(const RawVal& v, (long long|int) i\)', code, re.M)
    fn = 'baseFn' if re.search(r'^(?:LEETCODE_NO_SANITIZE )?Node baseFn\(', code, re.M) else 'leaf'
    leafdef = f'#define LF(v, i) {fn}(v, i)' if two else f'#define LF(v, i) {fn}(v)'
    tagf = 'static Tag tag() { ' + F.tag_maker(code) + ' }' if lazy else ''
    defs = {'TREE': tree, 'LAZY': int(lazy), 'DYNAMIC': int(dyn), 'TREAP': int(treap), 'REV': int('.norev' not in name and treap), 'PERSISTENT': int('Persistent' in tree), 'STATIC': int(tree == 'SparseTable')}
    body = TMPL.replace('SHOW', F.show(code)).replace('TAGFN', tagf).replace('LEAFDEF', leafdef).replace('SEED', '12345ULL')
    return ''.join(f'#define {k} {v}\n' for k, v in defs.items()) + code + body
def one(name):
    with tempfile.TemporaryDirectory() as tmp:
        p = f'{tmp}/x.cpp'; open(p, 'w').write(build(name))
        c = subprocess.run([cxx(), '-std=c++17', '-O1', '-g', '-w', *sanitize_flags(), '-o', f'{tmp}/x', p], capture_output=True, text=True)
        if c.returncode: return f'COMPILE {name}: ' + ' || '.join(l for l in c.stderr.split(chr(10)) if 'error' in l)[:900]
        try:
            r = subprocess.run([f'{tmp}/x'], capture_output=True, text=True, timeout=500)
        except subprocess.TimeoutExpired: return f'TIMEOUT {name}'
        return f'{"PASS" if r.returncode == 0 and r.stdout.strip() == "OK" else "FAIL"} {name} {r.stdout[-200:].strip()} {r.stderr[:900]}'
names = sorted(f for f in os.listdir(G) if f.endswith('.cpp') and not f.endswith('.debug.cpp'))
if len(sys.argv) > 1: names = [n for n in names if any(a in n for a in sys.argv[1:])]
with concurrent.futures.ThreadPoolExecutor(4) as p:
    for l in p.map(one, names): print(l.strip()[:1200], flush=True)
