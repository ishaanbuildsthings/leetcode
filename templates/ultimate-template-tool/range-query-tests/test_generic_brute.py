"""Every commented generic example, switched on, against a real brute force (Python files; C++ is test_generic_brute_cpp.py)."""
import os, re, sys, random, inspect, importlib.util, tempfile, subprocess, traceback
G = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'generic-seg-trees')
sys.setrecursionlimit(100000)
def fill_py(text):
    k = re.search(r'^class ', text, re.M).start()
    head = text[:k]
    head = re.sub(r'^( +)# (?!This is NOT)(.*)$', r'\1\2', head, flags=re.M)
    head = re.sub(r'^    pass\n', '', head, flags=re.M)
    return head + text[k:]
def load(name, tmp):
    code = fill_py(open(f'{G}/{name}').read())
    p = f'{tmp}/{name.replace(".", "_")}.py'
    open(p, 'w').write(code)
    s = importlib.util.spec_from_file_location(name.replace('.', '_'), p); m = importlib.util.module_from_spec(s); s.loader.exec_module(m)
    return m, code
def leaf_of(m):
    fn = getattr(m, 'leaf', None) or m.baseFn  # (GenericSparseTable names it baseFn)
    n = len(inspect.signature(fn).parameters)
    return (lambda v, i: fn(v, i)) if n == 2 else (lambda v, i: fn(v))
def fold(m, xs):
    r = xs[0]
    for x in xs[1:]: r = m.combine(r, x)
    return r
def pyone(name, seed, tmp, log):
    m, _ = load(name, tmp)
    cls = next(c for n, c in inspect.getmembers(m, inspect.isclass) if c.__module__ == m.__name__)
    sig = inspect.signature(cls.__init__)
    rng = random.Random(seed); L = leaf_of(m)
    lazy = hasattr(m, 'apply'); rev = hasattr(m, 'reverse'); dyn = 'Dynamic' in name
    n = rng.randint(1, 30)
    if dyn:
        lo, hi = rng.choice([(0, 25), (-7, 20)])
        n = hi - lo + 1
        idx = list(range(lo, hi + 1)); nodes = [m.blank(i, i) for i in idx]; off = lo
    else:
        a = [rng.randint(-50, 50) for _ in range(n)]; off = 0
        nodes = [L(v, i) for i, v in enumerate(a)]
    kw = {}
    for p in list(sig.parameters)[1:]:
        if p == 'a' or p == 'arr': kw[p] = a
        elif p == 'lo': kw[p] = lo
        elif p == 'hi': kw[p] = hi
        elif hasattr(m, p): kw[p] = getattr(m, p)
        elif sig.parameters[p].default is inspect._empty: raise RuntimeError('ctor arg ' + p)
    s = cls(**kw)
    olds = []
    meth = {n for n in dir(cls) if not n.startswith('_')}
    for step in range(250):
        n = len(nodes)
        l, r = sorted((rng.randrange(n), rng.randrange(n)))
        op = rng.choice(sorted(meth & {'pointGet', 'pointAssign', 'insertAt', 'append', 'eraseAt', 'rangeQuery', 'rangeQueryAll', 'rangeUpdate', 'rangeReverse', 'cut', 'split', 'trisect', 'rangeRotateLeft', 'rangeRotateRight', 'copy', 'size', 'merge', 'paste'}))
        def check(got, exp, what):
            if got != exp: raise AssertionError(f'{what}: got {got} expected {exp} step {step}')
        if op == 'size': check(s.size(), n, 'size')
        elif op == 'pointGet': check(s.pointGet(l + off), nodes[l], 'pointGet')
        elif op == 'pointAssign':
            v = rng.randint(-50, 50); s.pointAssign(l + off, v); nodes[l] = L(v, l + off)
        elif op == 'insertAt':
            v = rng.randint(-50, 50); i = rng.randint(0, n); s.insertAt(i, v); nodes.insert(i, L(v, i))
        elif op == 'append':
            v = rng.randint(-50, 50); s.append(v); nodes.append(L(v, n))
        elif op == 'eraseAt':
            if n > 1: s.eraseAt(l); del nodes[l]
        elif op == 'rangeQuery': check(s.rangeQuery(l + off, r + off), fold(m, nodes[l:r + 1]), f'rangeQuery({l},{r})')
        elif op == 'rangeQueryAll': check(s.rangeQueryAll(), fold(m, nodes), 'rangeQueryAll')
        elif op == 'rangeUpdate':
            t = rng.randint(-50, 50); s.rangeUpdate(l + off, r + off, t)
            for i in range(l, r + 1): nodes[i] = m.apply(nodes[i], t)
        elif op == 'rangeReverse':
            s.rangeReverse(l, r); nodes[l:r + 1] = [m.reverse(x) for x in nodes[l:r + 1]][::-1]
        elif op in ('rangeRotateLeft', 'rangeRotateRight'):
            k = rng.randint(-40, 40); getattr(s, op)(l, r, k)
            seg = nodes[l:r + 1]; ln = len(seg); kk = (k if op == 'rangeRotateLeft' else -k) % ln
            nodes[l:r + 1] = seg[kk:] + seg[:kk]
        elif op == 'cut':
            if r - l + 1 < n:
                p = s.cut(l, r); piece = nodes[l:r + 1]; del nodes[l:r + 1]
                check(p.size(), len(piece), 'piece size')
                i = rng.randint(0, len(nodes)); s.paste(i, p); check(p.size(), 0, 'pasted piece left empty'); nodes[i:i] = piece
        elif op == 'split':
            k = rng.randint(0, n); x, y = s.split(k); check(s.size(), 0, 'split leaves empty'); check(x.size(), k, 'split left'); x.merge(y); s = x
        elif op == 'trisect':
            x, y, z = s.trisect(l, r); check(s.size(), 0, 'trisect'); check(y.size(), r - l + 1, 'mid'); x.merge(y); x.merge(z); s = x
        elif op == 'copy':
            if len(olds) < 12:
                if rng.random() < .5: olds.append((s.copy(), list(nodes)))
                else: olds.append((s.copy(l, r), nodes[l:r + 1]))
            else:
                o, ns = rng.choice(olds)
                check(o.rangeQueryAll(), fold(m, ns), 'old version')
    return True
def edges_py(name, tmp):
    m, _ = load(name, tmp)
    cls = next(c for n, c in inspect.getmembers(m, inspect.isclass) if c.__module__ == m.__name__)
    sig = inspect.signature(cls.__init__); out = []
    for desc, arr in (('empty', []), ('single', [5])):
        if 'Dynamic' in name: continue
        kw = {}
        for p in list(sig.parameters)[1:]:
            if p in ('a', 'arr'): kw[p] = arr
            elif hasattr(m, p): kw[p] = getattr(m, p)
        try:
            s = cls(**kw)
            if hasattr(s, 'size'): assert s.size() == len(arr)
            if hasattr(s, 'rangeQueryAll'):
                try: r = s.rangeQueryAll()
                except Exception as e: out.append(f'{desc}: rangeQueryAll raises {type(e).__name__}({str(e)!r})')
                else: out.append(f'{desc}: rangeQueryAll returns {r!r}')
            if desc == 'empty' and hasattr(s, 'append'):
                s.append(7)
                assert s.size() == 1 and s.rangeQueryAll() == m.leaf(7)
        except Exception as e:
            out.append(f'{desc}: {type(e).__name__}: {e} @ ' + traceback.format_exc().strip().split(chr(10))[-3].strip())
    return out
if __name__ == '__main__':
    with tempfile.TemporaryDirectory() as tmp:
        bad = 0
        names = sorted(f for f in os.listdir(G) if f.endswith('.py') and '.debug.' not in f)
        for name in names:
            try:
                for seed in range(250): pyone(name, seed, tmp, None)
                print('PASS', name)
            except Exception as e:
                bad += 1; print('FAIL', name, 'seed', seed, f'{type(e).__name__}: {e}'[:400]); print(traceback.format_exc()[-500:])
            try:
                for x in edges_py(name, tmp): print('    edge', name, x[:200])
            except Exception as e: print('    edge-harness', name, repr(e)[:200])
        print('bad', bad, 'of', len(names))
