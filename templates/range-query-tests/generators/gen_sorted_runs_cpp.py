"""C++ bodies for gen_sorted_runs.py (same structures and names as the Python ones)."""
from gen_sorted_runs import AGG_OPS, QDOC, VFIELDS, WORD, class_name, doc, header, kind_of
from gen_treap import CPP_HASH_HELPERS

RND = '''
    static unsigned long long rnd() {
        static mt19937_64 g(chrono::steady_clock::now().time_since_epoch().count());
        return g();
    }
'''


def cpp_value_tree(aggs):
    H = "hash" in aggs
    decl = {"sm": "vector<S> sm{S(0)};", "xr": "vector<T> xr{T(0)};", "ov": "vector<T> ov{T(0)};",
            "av": "vector<T> av{T(~T(0))};  // node 0 holds every bit (AND's identity)",
            "fh": "vector<unsigned long long> fh{0}, bh{0}, pw{1}, gs{0};  // hashes both ways; B^k; 1 + B + ... + B^(k-1)"}
    push = {"sm": "sm.push_back(S(0))", "xr": "xr.push_back(T(0))", "ov": "ov.push_back(T(0))", "av": "av.push_back(T(~T(0)))",
            "fh": "fh.push_back(0), bh.push_back(0)"}
    vf = [f for a in aggs for f in VFIELDS.get(a, []) if f != "bh"]
    leaf = ["        cnt[x] = c;"] + ([] if set(aggs) & {"sum", "xor", "or", "and", "hash"} else ["        (void)v;"])
    if "sum" in aggs: leaf.append("        sm[x] = S(c) * S(v);")
    if "xor" in aggs: leaf.append("        xr[x] = (c & 1) ? T(v) : T(0);")
    if "or" in aggs: leaf.append("        ov[x] = T(v);")
    if "and" in aggs: leaf.append("        av[x] = T(v);")
    if H: leaf.append("        fh[x] = bh[x] = hmul(hval(T(v)), gs[c]);")
    pull = ["        int l = Lc[x], r = Rc[x];", "        cnt[x] = cnt[l] + cnt[r];"]
    if "sum" in aggs: pull.append("        sm[x] = sm[l] + sm[r];")
    if "xor" in aggs: pull.append("        xr[x] = xr[l] ^ xr[r];")
    if "or" in aggs: pull.append("        ov[x] = ov[l] | ov[r];")
    if "and" in aggs: pull.append("        av[x] = av[l] & av[r];")
    if H:
        pull += ["        fh[x] = hadd(hmul(fh[l], pw[cnt[r]]), fh[r]);", "        bh[x] = hadd(hmul(bh[r], pw[cnt[l]]), bh[l]);"]
    decls = "".join(f"    {decl[f]}\n" for f in vf)
    grow = '''
    // hash tables up to length m
    void grow(long long m) {
        while ((long long)pw.size() <= m) gs.push_back(hadd(gs.back(), pw.back())), pw.push_back(hmul(pw.back(), HB()));
    }
''' if H else ""
    body = f'''
    // ---- internals: value trees (node 0 = the empty tree) ----

    int node() {{
        if (!freeList.empty()) {{
            int t = freeList.back();
            freeList.pop_back();
            Lc[t] = Rc[t] = 0, cnt[t] = 0;
            return t;
        }}
        Lc.push_back(0), Rc.push_back(0), cnt.push_back(0){"".join(", " + push[f] for f in vf)};
        return (int)cnt.size() - 1;
    }}

    void freeTree(int t) {{  // hand every node of t back
        vector<int> st;
        if (t) st.push_back(t);
        while (!st.empty()) {{
            int u = st.back();
            st.pop_back();
            freeList.push_back(u);
            if (Lc[u]) st.push_back(Lc[u]);
            if (Rc[u]) st.push_back(Rc[u]);
        }}
    }}

    // node x holds c copies of v (a leaf, or a node with one value under it)
    void setLeaf(int x, long long v, long long c) {{
{chr(10).join(leaf)}
    }}

    void pull(int x) {{
{chr(10).join(pull)}
    }}
{grow}
    // a tree holding c copies of v: one node per level
    int leaf(T v, long long c = 1) {{
        int top_ = node(), t = top_;
        long long nl = vlo, nh = vhi;
        while (true) {{
            setLeaf(t, (long long)v, c);
            if (nl == nh) return top_;
            long long mid = nl + (nh - nl) / 2;
            int u = node();
            if ((long long)v <= mid) Lc[t] = u, nh = mid;
            else Rc[t] = u, nl = mid + 1;
            t = u;
        }}
    }}

    // a = the k smallest of t, b = the rest (0 <= k <= cnt[t]); t keeps the first part, new nodes (one path) the second
    void split(int t, long long k, long long nl, long long nh, int& a, int& b) {{
        if (k <= 0) {{ a = 0, b = t; return; }}
        if (k >= cnt[t]) {{ a = t, b = 0; return; }}
        int nb = node();
        if (nl == nh) {{  // one value: split its copies
            setLeaf(nb, nl, cnt[t] - k), setLeaf(t, nl, k);
            a = t, b = nb;
            return;
        }}
        long long mid = nl + (nh - nl) / 2, cl = cnt[Lc[t]];
        int x, y;
        if (k <= cl) {{
            split(Lc[t], k, nl, mid, x, y);
            Lc[t] = x, Lc[nb] = y, Rc[nb] = Rc[t], Rc[t] = 0;
        }} else {{
            split(Rc[t], k - cl, mid + 1, nh, x, y);
            Rc[t] = x, Rc[nb] = y;
        }}
        pull(t), pull(nb);
        a = t, b = nb;
    }}

    // the union of a and b, overlaid node by node (b's nodes where both have one are freed)
    int merge(int a, int b, long long nl, long long nh) {{
        if (!a || !b) return a ? a : b;
        if (nl == nh) {{
            setLeaf(a, nl, cnt[a] + cnt[b]);
        }} else {{
            long long mid = nl + (nh - nl) / 2;
            int x = merge(Lc[a], Lc[b], nl, mid);
            Lc[a] = x;
            int y = merge(Rc[a], Rc[b], mid + 1, nh);
            Rc[a] = y;
            pull(a);
        }}
        freeList.push_back(b);
        return a;
    }}

    // the k-th smallest value of t, 1 <= k <= cnt[t]
    T kth(int t, long long k) const {{
        long long nl = vlo, nh = vhi;
        while (nl != nh) {{
            long long mid = nl + (nh - nl) / 2, cl = cnt[Lc[t]];
            if (k <= cl) t = Lc[t], nh = mid;
            else k -= cl, t = Rc[t], nl = mid + 1;
        }}
        return T(nl);
    }}

    // append t's values, ascending (or descending), to out
    void values(int t, bool d, vector<T>& out) const {{
        size_t from = out.size();
        vector<tuple<int, long long, long long>> st{{{{t, vlo, vhi}}}};
        while (!st.empty()) {{  // in-order, pushed right first
            auto [u, nl, nh] = st.back();
            st.pop_back();
            if (!cnt[u]) continue;
            if (nl == nh) {{
                out.insert(out.end(), cnt[u], T(nl));
                continue;
            }}
            long long mid = nl + (nh - nl) / 2;
            st.push_back({{Rc[u], mid + 1, nh}}), st.push_back({{Lc[u], nl, mid}});
        }}
        if (d) reverse(out.begin() + from, out.end());
    }}
'''
    return decls, body


CPP_POINT_WRAPPERS = '''
    // O(log N + log U) amortized -- a[i] += v
    void pointAdd(int i, T v) { pointAssign(i, pointGet(i) + v); }

    // O(log N + log U) amortized -- a[i] = max(a[i], v)
    void pointChmax(int i, T v) { if (v > pointGet(i)) pointAssign(i, v); }

    // O(log N + log U) amortized -- a[i] = min(a[i], v)
    void pointChmin(int i, T v) { if (v < pointGet(i)) pointAssign(i, v); }
'''

RET = {"rangeSum": "S", "rangeXorQuery": "T", "rangeMin": "T", "rangeMax": "T", "rangeOrQuery": "T", "rangeAndQuery": "T",
       "rangeHash": "unsigned long long", "rangeHashReversed": "unsigned long long", "isPalindrome": "bool", "rangesEqual": "bool"}


def cpp_runs(aggs):
    kind = kind_of(aggs, False)
    SEG = kind == "seg"
    io = bool(aggs)
    decls, vt = cpp_value_tree(aggs)
    mem = ["    vector<int> root, len;  // per run start: its value tree, its length",
           "    vector<char> desc;      // per run start: sorted descending?",
           "    vector<int> bc;         // Fenwick: 1 at each run start"]
    ctor_init = ["root(n)", "len(n, 1)", "desc(n, 0)", "bc(n + 1, 1)"]
    build = ["        bc[0] = 0;"]
    fen_build = ["bc[j] += bc[i]"]
    if kind == "fenwick":
        if "sum" in aggs:
            mem.append("    vector<S> bs;           // Fenwick: each run's sum, at its start")
            ctor_init.append("bs(n + 1, S(0))")
            build.append("        for (int i = 0; i < n; i++) bs[i + 1] = S(arr[i]);")
            fen_build.append("bs[j] += bs[i]")
        if "xor" in aggs:
            mem.append("    vector<T> bx;           // Fenwick (of xors): each run's xor, at its start")
            ctor_init.append("bx(n + 1, T(0))")
            build.append("        for (int i = 0; i < n; i++) bx[i + 1] = arr[i];")
            fen_build.append("bx[j] ^= bx[i]")
    build.append("        for (int i = 1; i <= n; i++) {  // O(N) Fenwick builds")
    build.append("            int j = i + (i & -i);")
    build.append(f"            if (j <= n) {', '.join(fen_build)};")
    build.append("        }")
    Q = {"sum": [("qs", "S", "S(0)")], "xor": [("qx", "T", "T(0)")], "min": [("qn", "T", "numeric_limits<T>::max()")],
         "max": [("qm", "T", "numeric_limits<T>::lowest()")], "or": [("qo", "T", "T(0)")], "and": [("qa", "T", "T(~T(0))")],
         "hash": [("qf", "unsigned long long", "0"), ("qb", "unsigned long long", "0"), ("ql", "int", "0")]}
    qarr = [x for a in aggs for x in Q[a]]
    if SEG:
        mem.append("    int size;               // seg tree over positions: each run's aggregates at its start")
        mem += [f"    vector<{ty}> {q};" for q, ty, _ in qarr]
        build.append("        for (size = 1; size < n; size <<= 1) {}")
        build += [f"        {q}.assign(2 * size, {idn});" for q, _, idn in qarr]
        build.append("        for (int s = 0; s < n; s++) setPos(s + size, s);")
        build.append("        for (int p = size - 1; p > 0; p--) up(p);")
    inout = ""
    if kind == "fenwick" and io:
        add = []
        if "sum" in aggs: add.append("fen(bs, s, sgn > 0 ? sm[t] : -sm[t])")
        if "xor" in aggs: add.append("fenx(s, xr[t])")
        inout = f'''
    // add (sgn = 1) or take out (sgn = -1) the run starting at s from the run aggregates
    void io(int s, int sgn) {{
        int t = root[s];
        {", ".join(add)};{" (void)sgn;" if "sum" not in aggs else ""}
    }}
'''
        if "xor" in aggs:
            inout += '''
    void fenx(int i, T v) {  // xor v in at i
        for (i++; i <= n; i += i & -i) bx[i] ^= v;
    }

    T prex(int i) const {  // xor of positions 0..i-1
        T s = 0;
        for (; i > 0; i &= i - 1) s ^= bx[i];
        return s;
    }
'''
    asks = ""
    if SEG:
        setl = ["        int t = root[s];"]
        for a in aggs:
            setl += {"sum": ["        qs[p] = sm[t];"], "xor": ["        qx[p] = xr[t];"], "min": ["        qn[p] = kth(t, 1);"],
                     "max": ["        qm[p] = kth(t, cnt[t]);"], "or": ["        qo[p] = ov[t];"], "and": ["        qa[p] = av[t];"],
                     "hash": ["        qf[p] = desc[s] ? bh[t] : fh[t], qb[p] = desc[s] ? fh[t] : bh[t], ql[p] = len[s];"]}[a]
        clr = [f"{q}[p] = {idn}" for q, _, idn in qarr]
        up = []
        for a in aggs:
            up += {"sum": ["        qs[p] = qs[2 * p] + qs[2 * p + 1];"], "xor": ["        qx[p] = qx[2 * p] ^ qx[2 * p + 1];"],
                   "min": ["        qn[p] = min(qn[2 * p], qn[2 * p + 1]);"], "max": ["        qm[p] = max(qm[2 * p], qm[2 * p + 1]);"],
                   "or": ["        qo[p] = qo[2 * p] | qo[2 * p + 1];"], "and": ["        qa[p] = qa[2 * p] & qa[2 * p + 1];"],
                   "hash": ["        int l = 2 * p, r = l + 1;", "        qf[p] = hadd(hmul(qf[l], pw[ql[r]]), qf[r]);",
                            "        qb[p] = hadd(hmul(qb[r], pw[ql[l]]), qb[l]);", "        ql[p] = ql[l] + ql[r];"]}[a]
        inout = f'''
    // leaf p of the position tree <- the aggregates of the run starting at s
    void setPos(int p, int s) {{
{chr(10).join(setl)}
    }}

    void up(int p) {{
{chr(10).join(up)}
    }}

    // add (sgn = 1) or take out (sgn = -1) the run starting at s from the position tree
    void io(int s, int sgn) {{
        int p = s + size;
        if (sgn > 0) setPos(p, s);
        else {", ".join(clr)};
        for (p >>= 1; p; p >>= 1) up(p);
    }}
'''
        for a in aggs:
            if a == "hash":
                asks += '''
    // (hash of positions l..r read left to right, read right to left)
    pair<unsigned long long, unsigned long long> askHash(int l, int r) const {
        unsigned long long lf = 0, lb = 0, rf = 0, rb = 0;
        int ll = 0, rl = 0;
        for (l += size, r += size + 1; l < r; l >>= 1, r >>= 1) {
            if (l & 1) lf = hadd(hmul(lf, pw[ql[l]]), qf[l]), lb = hadd(hmul(qb[l], pw[ll]), lb), ll += ql[l], l++;
            if (r & 1) --r, rf = hadd(hmul(qf[r], pw[rl]), rf), rb = hadd(hmul(rb, pw[ql[r]]), qb[r]), rl += ql[r];
        }
        return {hadd(hmul(lf, pw[rl]), rf), hadd(hmul(rb, pw[ll]), lb)};
    }
'''
                continue
            q, ty, idn = Q[a][0]
            f = {"sum": "res += {x}", "xor": "res ^= {x}", "min": "res = min(res, {x})", "max": "res = max(res, {x})",
                 "or": "res |= {x}", "and": "res &= {x}"}[a]
            asks += f'''
    {ty} ask_{q}(int l, int r) const {{  // the {WORD[a]} over positions l..r
        {ty} res = {idn};
        for (l += size, r += size + 1; l < r; l >>= 1, r >>= 1) {{
            if (l & 1) {f.format(x=f"{q}[l++]")};
            if (r & 1) {f.format(x=f"{q}[--r]")};
        }}
        return res;
    }}
'''

    def call(s, sgn, ind):
        return f"{ind}io({s}, {sgn});\n" if io else ""
    queries = ""
    for a in aggs:
        for op in AGG_OPS[a]:
            if op == "rangesEqual":
                queries += f'''
    // O(log N + log U) amortized -- {QDOC[op]}
    bool rangesEqual(int l1, int r1, int l2, int r2) {{ return r1 - l1 == r2 - l2 && rangeHash(l1, r1) == rangeHash(l2, r2); }}
'''
                continue
            if kind == "fenwick":
                body = {"rangeSum": "return pre(bs, r + 1) - pre(bs, l);", "rangeXorQuery": "return prex(r + 1) ^ prex(l);"}[op]
            else:
                body = {"rangeSum": "return ask_qs(l, r);", "rangeXorQuery": "return ask_qx(l, r);", "rangeMin": "return ask_qn(l, r);",
                        "rangeMax": "return ask_qm(l, r);", "rangeOrQuery": "return ask_qo(l, r);", "rangeAndQuery": "return ask_qa(l, r);",
                        "rangeHash": "return askHash(l, r).first;", "rangeHashReversed": "return askHash(l, r).second;",
                        "isPalindrome": "auto [f, b] = askHash(l, r);\n        return f == b;"}[op]
            queries += f'''
    // O(log N + log U) amortized -- {QDOC[op]}
    {RET[op]} {op}(int l, int r) {{
        cutAt(l), cutAt(r + 1);
        {body}
    }}
'''
    H = "hash" in aggs
    name = class_name(aggs, False)
    return f'''template <typename T>
struct {name} {{
    using S = conditional_t<(sizeof(T) < sizeof(long long)), long long, T>;
    int n, top;
    long long vlo, vhi;
    vector<int> Lc{{0}}, Rc{{0}}, freeList;  // value node 0 = the empty tree; nodes freed by merges are reused first
    vector<long long> cnt{{0}};
{decls}{chr(10).join(mem)}
{(CPP_HASH_HELPERS + RND) if H else ""}
    // O(N log U) -- arr: the initial array; every value a[i] ever holds must lie in [valLo, valHi] (U = valHi - valLo + 1)
    {name}(const vector<T>& arr, long long valLo, long long valHi)
        : n((int)arr.size()), vlo(valLo), vhi(valHi), {", ".join(ctor_init)} {{
{"        grow(n);" + chr(10) if H else ""}        for (int i = 0; i < n; i++) root[i] = leaf(arr[i]);
        top = n ? 1 << (31 - __builtin_clz(n)) : 0;
{chr(10).join(build)}
    }}

    // O(log N + log U) -- a[i]
    T pointGet(int i) const {{
        int s = startOf(i), k = i - s;
        return kth(root[s], desc[s] ? len[s] - k : k + 1);
    }}

    // O(log N + log U) amortized -- a[i] = v
    void pointAssign(int i, T v) {{
        cutAt(i), cutAt(i + 1);
{call("i", -1, "        ")}        freeTree(root[i]);
        int t = leaf(v);
        root[i] = t;
{call("i", 1, "        ")}    }}
{CPP_POINT_WRAPPERS}
    // O(log N + log U) amortized -- sort a[l..r] ascending
    void rangeSortAsc(int l, int r) {{ sortRange(l, r, false, false, T(0)); }}

    // O(log N + log U) amortized -- sort a[l..r] descending
    void rangeSortDesc(int l, int r) {{ sortRange(l, r, true, false, T(0)); }}

    // O(log N + log U) amortized -- a[i] = v for i in [l, r]
    void rangeAssign(int l, int r, T v) {{ sortRange(l, r, false, true, v); }}
{queries}
    // O(N log U) -- the whole current array
    vector<T> getAll() const {{
        vector<T> out;
        out.reserve(n);
        for (int s = 0; s < n; s += len[s]) values(root[s], desc[s], out);
        return out;
    }}

    // ---- internals: runs ----

    // cut at l and r + 1, then turn a[l..r] into one run: every run inside merged (assign false) or thrown away for a
    // run of r - l + 1 copies of v
    void sortRange(int l, int r, bool d, bool assign, T v) {{
        cutAt(l), cutAt(r + 1);
{call("l", -1, "        ")}        int t = root[l];
        if (assign) freeTree(t);
        for (int s = l + len[l]; s <= r;) {{  // every run inside goes
            int b = root[s], nxt = s + len[s];
{call("s", -1, "            ")}            fen(bc, s, -1);
            if (assign) freeTree(b);
            else t = merge(t, b, vlo, vhi);
            s = nxt;
        }}
        if (assign) t = leaf(v, r - l + 1);
        root[l] = t, len[l] = r - l + 1, desc[l] = d;
{call("l", 1, "        ")}    }}

    // make a run start at p (0 < p < n): split the run holding it by count
    void cutAt(int p) {{
        if (p <= 0 || p >= n) return;
        int s = startOf(p);
        if (s == p) return;
{call("s", -1, "        ")}        int t = root[s], k = p - s, ln = len[s], a, b;
        if (desc[s]) split(t, ln - k, vlo, vhi, b, a);  // the first k are the k largest
        else split(t, k, vlo, vhi, a, b);
        root[s] = a, len[s] = k;
        root[p] = b, len[p] = ln - k, desc[p] = desc[s];
        fen(bc, p, 1);
{call("s", 1, "        ")}{call("p", 1, "        ")}    }}

    // the start of the run holding i: the (# of starts <= i)-th start, by binary lifting
    int startOf(int i) const {{
        int k = pre(bc, i + 1), pos = 0;
        for (int step = top; step; step >>= 1)
            if (pos + step <= n && bc[pos + step] < k) pos += step, k -= bc[pos];
        return pos;
    }}

    template <class V>
    void fen(vector<V>& f, int i, V v) {{
        for (i++; i <= n; i += i & -i) f[i] += v;
    }}

    template <class V>
    static V pre(const vector<V>& f, int i) {{  // f's total over positions 0..i-1
        V s = 0;
        for (; i > 0; i &= i - 1) s += f[i];
        return s;
    }}
{inout}{asks}{vt}}};
'''


def cpp_treap(aggs):
    H = "hash" in aggs
    decls, vt = cpp_value_tree(aggs)
    sub = {"sum": [("Ssm", "S", "S(0)")], "xor": [("Sxr", "T", "T(0)")],
           "min": [("Omn", "T", "numeric_limits<T>::max()"), ("Smn", "T", "numeric_limits<T>::max()")],
           "max": [("Omx", "T", "numeric_limits<T>::lowest()"), ("Smx", "T", "numeric_limits<T>::lowest()")],
           "or": [("Sov", "T", "T(0)")], "and": [("Sav", "T", "T(~T(0))")],
           "hash": [("Sfh", "unsigned long long", "0"), ("Sbh", "unsigned long long", "0")]}
    arrs = [x for a in aggs for x in sub[a]]
    mem = ["    // treap of runs (node 0 = empty): children TL / TR, priority TP, value tree TV, length TN, descending TD,",
           "    // subtree length TS, pending reverse TF" + (", subtree " + " / ".join(WORD[a] for a in aggs) if aggs else "") +
           (" (O: the run's own min / max)" if {"min", "max"} & set(aggs) else ""),
           "    vector<int> TL{0}, TR{0}, TV{0}, TN{0}, TS{0}, tfree;", "    vector<unsigned long long> TP{0};",
           "    vector<char> TD{0}, TF{0};"]
    mem += [f"    vector<{ty}> {a}{{{idn}}};" for a, ty, idn in arrs]

    def own(t):
        out = []
        if "min" in aggs: out.append(f"        Omn[x] = kth({t}, 1);")
        if "max" in aggs: out.append(f"        Omx[x] = kth({t}, cnt[{t}]);")
        return "".join(ln + "\n" for ln in out)
    tpull = ["        int L = TL[x], R = TR[x]" + (", t = TV[x];" if set(aggs) & {"sum", "xor", "or", "and", "hash"} else ";"),
             "        TS[x] = TS[L] + TN[x] + TS[R];"]
    for a in aggs:
        tpull += {"sum": ["        Ssm[x] = Ssm[L] + sm[t] + Ssm[R];"], "xor": ["        Sxr[x] = Sxr[L] ^ xr[t] ^ Sxr[R];"],
                  "min": ["        Smn[x] = min(Omn[x], min(Smn[L], Smn[R]));"], "max": ["        Smx[x] = max(Omx[x], max(Smx[L], Smx[R]));"],
                  "or": ["        Sov[x] = Sov[L] | ov[t] | Sov[R];"], "and": ["        Sav[x] = Sav[L] & av[t] & Sav[R];"],
                  "hash": ["        unsigned long long f = TD[x] ? bh[t] : fh[t], b = TD[x] ? fh[t] : bh[t];  // the run, read left to right / right to left",
                           "        Sfh[x] = hadd(hmul(hadd(hmul(Sfh[L], pw[TN[x]]), f), pw[TS[R]]), Sfh[R]);",
                           "        Sbh[x] = hadd(hmul(hadd(hmul(Sbh[R], pw[TN[x]]), b), pw[TS[L]]), Sbh[L]);"]}[a]
    rev = "swap(TL[x], TR[x]), TD[x] ^= 1" + (", swap(Sfh[x], Sbh[x])" if H else "") + ", TF[x] ^= 1"
    queries = ""
    for a in aggs:
        for op in AGG_OPS[a]:
            if op == "rangesEqual":
                queries += f'''
    // O(log N + log U) amortized -- {QDOC[op]}
    bool rangesEqual(int l1, int r1, int l2, int r2) {{ return r1 - l1 == r2 - l2 && rangeHash(l1, r1) == rangeHash(l2, r2); }}
'''
                continue
            read = {"rangeSum": "Ssm[B]", "rangeXorQuery": "Sxr[B]", "rangeMin": "Smn[B]", "rangeMax": "Smx[B]", "rangeOrQuery": "Sov[B]",
                    "rangeAndQuery": "Sav[B]", "rangeHash": "Sfh[B]", "rangeHashReversed": "Sbh[B]", "isPalindrome": "Sfh[B] == Sbh[B]"}[op]
            queries += f'''
    // O(log N + log U) amortized -- {QDOC[op]}
    {RET[op]} {op}(int l, int r) {{
        auto [A, B, C] = extract(l, r);
        {RET[op]} res = {read};
        join(A, B, C);
        return res;
    }}
'''
    name = class_name(aggs, True)
    pushes = "".join(f", {a}.push_back({idn})" for a, _, idn in arrs)
    from gen_treap_algebra import POOL_NOTE
    from gen_treap import wrap
    members = (["    vector<int> Lc{0}, Rc{0}, freeList;  // value node 0 = the empty tree; merges free nodes, reused first",
                "    vector<long long> cnt{0};"] + [ln for ln in decls.split(chr(10)) if ln.strip()] + mem)
    pool_text = wrap(POOL_NOTE.format(cls=name + "<T>").replace("Nodes are never freed (memory = every value ever inserted, over the whole run), so there is nothing to reset", "Nodes freed by merges are reused, and there is nothing to reset"), "    //") + "".join(
        ("    static inline " + ln[4:] if ln.startswith("    vector<") else ln) + chr(10) for ln in members) + "    long long vlo, vhi;  // (each one's value range)\n"
    return f'''template <typename T>
struct {name} {{
    using S = conditional_t<(sizeof(T) < sizeof(long long)), long long, T>;
{pool_text}    int n = 0, rt = 0;
{CPP_HASH_HELPERS if H else ""}{RND}
    // O(N log U) -- arr: the initial array; every value a[i] ever holds must lie in [valLo, valHi]
    // (U = valHi - valLo + 1)
    {name}(const vector<T>& arr, long long valLo, long long valHi) : vlo(valLo), vhi(valHi) {{ buildFrom(arr); }}

    {name} makeEmpty() const {{ return {name}({{}}, vlo, vhi); }}  // (a new, empty one: same pool, same value range)

    void buildFrom(const vector<T>& arr) {{
        n = (int)arr.size();
{"        grow(n);" + chr(10) if H else ""}        vector<int> st;  // O(N) build: the treap's right spine
        for (const T& v : arr) {{
            int x = run(leaf(v), 1, false), last = 0;
            while (!st.empty() && TP[st.back()] < TP[x]) last = st.back(), st.pop_back(), tpull(last);
            TL[x] = last;
            if (!st.empty()) TR[st.back()] = x;
            st.push_back(x);
        }}
        for (int i = (int)st.size() - 1; i >= 0; i--) tpull(st[i]);
        rt = st.empty() ? 0 : st[0];
    }}

    // O(1) -- the current length
    int size() const {{ return n; }}

    // O(log N + log U) expected -- a[i]
    T pointGet(int i) {{
        for (int x = rt;;) {{
            push(x);
            int ls = TS[TL[x]];
            if (i < ls) x = TL[x];
            else if (i < ls + TN[x]) {{
                int k = i - ls;
                return kth(TV[x], TD[x] ? TN[x] - k : k + 1);
            }} else i -= ls + TN[x], x = TR[x];
        }}
    }}

    // O(log N + log U) amortized -- a[i] = v
    void pointAssign(int i, T v) {{ rangeAssign(i, i, v); }}
{CPP_POINT_WRAPPERS}
    // O(log N + log U) amortized -- sort a[l..r] ascending
    void rangeSortAsc(int l, int r) {{ sortRange(l, r, false); }}

    // O(log N + log U) amortized -- sort a[l..r] descending
    void rangeSortDesc(int l, int r) {{ sortRange(l, r, true); }}

    // O(log N + log U) amortized -- a[i] = v for i in [l, r]
    void rangeAssign(int l, int r, T v) {{
        auto [A, B, C] = extract(l, r);
        drop(B);
        join(A, run(leaf(v, r - l + 1), r - l + 1, false), C);
    }}

    // O(log N + log U) amortized -- reverse a[l..r]
    void rangeReverse(int l, int r) {{
        auto [A, B, C] = extract(l, r);
        rev(B);
        join(A, B, C);
    }}

    // O(log N + log U) amortized -- insert v so it becomes a[i]; 0 <= i <= size() (i = size() appends)
    void insertAt(int i, T v) {{ insertCopiesAt(i, v, 1); }}

    // O(log N + log U) amortized -- insert k copies of v starting at index i (0 <= i <= size(); k <= 0 does nothing)
    void insertCopiesAt(int i, T v, long long k) {{
        if (k <= 0) return;
        n += (int)k;
{"        grow(n);" + chr(10) if H else ""}        auto [A, C] = tsplit(rt, i);
        rt = tmerge(tmerge(A, run(leaf(v, k), (int)k, false)), C);
    }}

    // O(log N + log U) amortized -- append v
    void append(T v) {{ insertCopiesAt(n, v, 1); }}

    // O(log N + log U) amortized -- insert v at the front (it becomes a[0])
    void appendLeft(T v) {{ insertCopiesAt(0, v, 1); }}

    // O(log N + log U) amortized -- remove a[l..r] and return it as one of its own (indices from 0)
    {name} cut(int l, int r) {{
        auto [A, B, C] = extract(l, r);
        rt = tmerge(A, C), n -= r - l + 1;
        {name} piece = makeEmpty();
        piece.rt = B, piece.n = r - l + 1;
        return piece;
    }}

    // O(log N + log U) amortized -- insert all of other (one with the same valLo / valHi, e.g. a cut piece) so it
    // starts at a[i] (0 <= i <= size()); other is left empty
    void paste(int i, {name}& other) {{
        n += other.n;
{"        grow(n);  // (before the merge reads the powers)" + chr(10) if H else ""}        auto [A, C] = tsplit(rt, i);
        rt = tmerge(tmerge(A, other.rt), C), other.rt = other.n = 0;
    }}

    // O(log N + log U) amortized -- append all of other at the end, leaving it empty (it must share this one's nodes)
    void merge({name}& other) {{ paste(n, other); }}

    // O(log N + log U) amortized -- (a[0..k-1], a[k..]) as two of their own; this one is left empty
    pair<{name}, {name}> split(int k) {{
        {name} left = makeEmpty(), right = makeEmpty();
        tie(left.rt, right.rt) = tsplit(rt, k);
        left.n = k, right.n = n - k, rt = n = 0;
        return {{left, right}};
    }}

    // O(log N + log U) amortized -- (a[0..l-1], a[l..r], a[r+1..]) as three of their own; this one is left empty
    tuple<{name}, {name}, {name}> trisect(int l, int r) {{
        {name} left = makeEmpty(), mid = makeEmpty(), right = makeEmpty();
        tie(left.rt, mid.rt, right.rt) = extract(l, r);
        left.n = l, mid.n = r - l + 1, right.n = n - r - 1, rt = n = 0;
        return {{left, mid, right}};
    }}

    // O(log N + log U) amortized -- rotate a[l..r] left by k (a[l + k] comes first); k can be huge or
    // negative: it is taken mod the length (negative = right)
    void rangeRotateLeft(int l, int r, long long k) {{
        long long m = r - l + 1;
        k = ((k % m) + m) % m;
        if (!k) return;
        auto [A, B, C] = extract(l, r);
        auto [X, Y] = tsplit(B, (int)k);
        join(A, tmerge(Y, X), C);
    }}

    // O(log N + log U) amortized -- rotate a[l..r] right by k; k can be huge or negative: it is taken mod
    // the length (negative = left)
    void rangeRotateRight(int l, int r, long long k) {{ rangeRotateLeft(l, r, -k); }}
{queries}
    // O(N log U) -- the whole current array
    vector<T> getAll() {{
        vector<T> out;
        out.reserve(n);
        vector<int> st;
        for (int x = rt; !st.empty() || x;) {{
            for (; x; x = TL[x]) push(x), st.push_back(x);
            x = st.back();
            st.pop_back();
            values(TV[x], TD[x], out);
            x = TR[x];
        }}
        return out;
    }}

    // ---- internals: the treap of runs ----

    // a new run node: value tree t, length ln, descending?
    int run(int t, int ln, bool d) {{
        int x;
        if (!tfree.empty()) x = tfree.back(), tfree.pop_back(), TL[x] = TR[x] = 0, TF[x] = 0;
        else {{
            x = (int)TS.size();
            TL.push_back(0), TR.push_back(0), TV.push_back(0), TN.push_back(0), TS.push_back(0), TP.push_back(0);
            TD.push_back(0), TF.push_back(0){pushes};
        }}
        TP[x] = rnd(), TV[x] = t, TN[x] = ln, TD[x] = d;
{own("t")}        tpull(x);
        return x;
    }}

    void tpull(int x) {{
{chr(10).join(tpull)}
    }}

    void rev(int x) {{  // reverse x's subtree: swap its children (and below, lazily), flip its run
        if (x) {rev};
    }}

    void push(int x) {{
        if (TF[x]) rev(TL[x]), rev(TR[x]), TF[x] = 0;
    }}

    // (the first k elements, the rest), cutting the run that straddles k
    pair<int, int> tsplit(int x, int k) {{
        if (!x || k <= 0) return {{0, x}};
        if (k >= TS[x]) return {{x, 0}};
        push(x);
        int ls = TS[TL[x]];
        if (k <= ls) {{
            auto [a, b] = tsplit(TL[x], k);
            TL[x] = b;
            tpull(x);
            return {{a, x}};
        }}
        if (k >= ls + TN[x]) {{
            auto [a, b] = tsplit(TR[x], k - ls - TN[x]);
            TR[x] = a;
            tpull(x);
            return {{x, b}};
        }}
        k -= ls;  // cut this run: x keeps its first k elements, a new node the rest
        int t = TV[x], ln = TN[x], a, b;
        if (TD[x]) split(t, ln - k, vlo, vhi, b, a);  // the first k are the k largest
        else split(t, k, vlo, vhi, a, b);
        TV[x] = a, TN[x] = k;
{own("a")}        int u = run(b, ln - k, TD[x]), R = TR[x];
        TR[x] = 0;
        tpull(x);
        return {{x, tmerge(u, R)}};
    }}

    int tmerge(int a, int b) {{
        if (!a || !b) return a ? a : b;
        if (TP[a] > TP[b]) {{
            push(a);
            int r = tmerge(TR[a], b);
            TR[a] = r;
            tpull(a);
            return a;
        }}
        push(b);
        int l = tmerge(a, TL[b]);
        TL[b] = l;
        tpull(b);
        return b;
    }}

    // (before l, a[l..r], after r) as three treaps
    tuple<int, int, int> extract(int l, int r) {{
        auto [A, B] = tsplit(rt, l);
        auto [B2, C] = tsplit(B, r - l + 1);
        return {{A, B2, C}};
    }}

    void join(int A, int B, int C) {{ rt = tmerge(tmerge(A, B), C); }}

    vector<int> nodes(int x) const {{  // every run node of x's treap
        vector<int> out, st;
        if (x) st.push_back(x);
        while (!st.empty()) {{
            int y = st.back();
            st.pop_back();
            out.push_back(y);
            if (TL[y]) st.push_back(TL[y]);
            if (TR[y]) st.push_back(TR[y]);
        }}
        return out;
    }}

    void drop(int x) {{  // free every run of x (value trees and treap nodes)
        for (int y : nodes(x)) freeTree(TV[y]), tfree.push_back(y);
    }}

    // a[l..r] becomes one sorted run: every run inside merges into one
    void sortRange(int l, int r, bool d) {{
        auto [A, B, C] = extract(l, r);
        int t = 0;
        for (int y : nodes(B)) t = merge(t, TV[y], vlo, vhi), tfree.push_back(y);
        join(A, run(t, r - l + 1, d), C);
    }}
{vt}}};
'''


def cpp(aggs, seq):
    return (header("//", aggs, seq) + "\n" + doc("//", aggs, seq) + "// T: int, long long, ...; sums in S (long long for small T).\n" +
            (cpp_treap(aggs) if seq else cpp_runs(aggs)))
