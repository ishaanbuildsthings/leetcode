// Fully dynamic connectivity (Holm-de Lichtenberg-Thorup, JACM 2001).
// Online edge insert + edge delete + connectivity query. Unlike DSU, deletions are allowed.
// Takes an array of vals (can be strings, tuples, etc) since it operates based on indices
// DynamicConnectivity<int> dc(vals);
//
// Memory is O(n log n) treap nodes at ~26 bytes each, so n = 1e5 costs roughly 80 MB. Budget for it.
template <typename T>
struct DynamicConnectivity {
    // One level's spanning forest, held as Euler tours in a treap.
    // Tour of a k-vertex tree = k vertex nodes + 2(k-1) arc nodes = 3k-2 nodes.
    // A tree edge is addressed by a "slot" in 0 .. n-2, recycled by the owner.
    struct Forest {
        vector<int> lc, rc, pa, sz, eid, arcNode;  // arcNode[2s], arcNode[2s+1] = the two arcs of slot s
        vector<unsigned> pri;
        vector<char> mk, ag;  // bit 0 = tree edge living at this level, bit 1 = vertex owns an incident non-tree edge at this level
        vector<int> pool;
        unsigned rngState = 2463534242u;
        int n = 0;

        unsigned rnd() {
            unsigned x = rngState;
            x ^= x << 13, x ^= x >> 17, x ^= x << 5;
            return rngState = x;
        }

        // node 0 is null, vertex u is node u + 1, arc nodes get allocated after that
        void init(int n_) {
            n = n_;
            int cap = n + 1;
            lc.assign(cap, 0), rc.assign(cap, 0), pa.assign(cap, 0), sz.assign(cap, 1);
            eid.assign(cap, -1), pri.assign(cap, 0), mk.assign(cap, 0), ag.assign(cap, 0);
            sz[0] = 0;
            for (int u = 0; u < n; u++) pri[u + 1] = rnd();
            arcNode.assign(2 * max(n - 1, 1), 0);
        }

        int vnode(int u) const { return u + 1; }
        int vertexOf(int x) const { return x - 1; }
        void pull(int x) {
            sz[x] = 1 + sz[lc[x]] + sz[rc[x]];
            ag[x] = mk[x] | ag[lc[x]] | ag[rc[x]];
        }

        int newNode(int e) {
            int x;
            if (!pool.empty()) x = pool.back(), pool.pop_back();
            else {
                x = lc.size();
                lc.push_back(0), rc.push_back(0), pa.push_back(0), sz.push_back(1);
                eid.push_back(-1), pri.push_back(0), mk.push_back(0), ag.push_back(0);
            }
            lc[x] = rc[x] = pa[x] = 0, sz[x] = 1, mk[x] = ag[x] = 0, pri[x] = rnd(), eid[x] = e;
            return x;
        }

        int merge(int a, int b) {
            if (!a || !b) {
                int r = a ? a : b;
                if (r) pa[r] = 0;
                return r;
            }
            if (pri[a] > pri[b]) {
                rc[a] = merge(rc[a], b);
                if (rc[a]) pa[rc[a]] = a;
                pull(a), pa[a] = 0;
                return a;
            }
            lc[b] = merge(a, lc[b]);
            if (lc[b]) pa[lc[b]] = b;
            pull(b), pa[b] = 0;
            return b;
        }

        // first k nodes of t go to a, the rest to b
        void split(int t, int k, int& a, int& b) {
            if (!t) { a = b = 0; return; }
            pa[t] = 0;
            if (sz[lc[t]] >= k) {
                split(lc[t], k, a, lc[t]);
                if (lc[t]) pa[lc[t]] = t;
                if (a) pa[a] = 0;
                pull(t), b = t;
            } else {
                split(rc[t], k - sz[lc[t]] - 1, rc[t], b);
                if (rc[t]) pa[rc[t]] = t;
                if (b) pa[b] = 0;
                pull(t), a = t;
            }
        }

        int findRoot(int x) { while (pa[x]) x = pa[x]; return x; }
        int pos(int x) {
            int k = sz[lc[x]];
            while (pa[x]) {
                int p = pa[x];
                if (rc[p] == x) k += sz[lc[p]] + 1;
                x = p;
            }
            return k;
        }
        void updatePath(int x) { while (x) pull(x), x = pa[x]; }

        int rootOf(int u) { return findRoot(vnode(u)); }
        bool sameTree(int u, int v) { return u == v || rootOf(u) == rootOf(v); }
        int treeSize(int u) { return (sz[rootOf(u)] + 2) / 3; }

        // rotate the tour so u comes first; the tour is circular, so this is free
        void reroot(int u) {
            int x = vnode(u), r = findRoot(x), k = pos(x);
            if (!k) return;
            int a, b;
            split(r, k, a, b);
            merge(b, a);
        }

        void link(int u, int v, int slot, int e) {
            reroot(u), reroot(v);
            int ru = rootOf(u), rv = rootOf(v);
            int a = newNode(e), b = newNode(e);
            arcNode[2 * slot] = a, arcNode[2 * slot + 1] = b;
            merge(merge(merge(ru, a), rv), b);
        }

        void cut(int slot) {
            int x = arcNode[2 * slot], y = arcNode[2 * slot + 1];
            int r = findRoot(x), px = pos(x), py = pos(y);
            if (px > py) swap(px, py), swap(x, y);
            int a, b, c, t1, t2, xx, yy;
            split(r, px, a, t1);            // a = tour before the arc
            split(t1, 1, xx, t2);           // xx = the arc itself
            split(t2, py - px - 1, b, t1);  // b = tour of the half that breaks off
            split(t1, 1, yy, c);            // yy = the back arc, c = tour after it
            merge(a, c);
            pool.push_back(xx), pool.push_back(yy);
        }

        void setVertexMark(int u, bool b) {
            int x = vnode(u);
            mk[x] = char((mk[x] & 1) | (b << 1));
            updatePath(x);
        }
        void setEdgeMark(int slot, bool b) {
            int x = arcNode[2 * slot];
            mk[x] = char((mk[x] & 2) | int(b));
            updatePath(x);
        }

        // O(#hits * log n): the OR aggregate lets us skip every subtree with no marked node in it
        void gather(int t, int bit, vector<int>& out) {
            if (!t || !((ag[t] >> bit) & 1)) return;
            gather(lc[t], bit, out);
            if ((mk[t] >> bit) & 1) out.push_back(t);
            gather(rc[t], bit, out);
        }
    };

    vector<T> vals;
    int n, levels, comps;
    vector<Forest> forest;
    vector<int> eu, ev, elevel, slot, nxt, prv, freeIds, freeSlots;
    vector<char> seen;
    vector<vector<int>> head;  // head[l][u] = first arc of u's level-l non-tree list
    map<pair<int, int>, vector<int>> byPair;
    vector<int> tmpEdges, tmpVerts, tmpPromote;

    // O(n log n), every element starts in its own component
    DynamicConnectivity(const vector<T>& vals) : vals(vals), n(vals.size()), comps(vals.size()) {
        levels = 1;
        while ((1 << levels) < max(n, 2)) levels++;
        levels++;
        forest.resize(levels);
        for (int l = 0; l < levels; l++) forest[l].init(n);
        head.assign(levels, vector<int>(n, -1));
        freeSlots.resize(max(n - 1, 1));
        iota(freeSlots.rbegin(), freeSlots.rend(), 0);
    }

    int owner(int a) { return (a & 1) ? ev[a >> 1] : eu[a >> 1]; }
    int other(int a) { return (a & 1) ? eu[a >> 1] : ev[a >> 1]; }

    int newId() {
        if (!freeIds.empty()) {
            int e = freeIds.back();
            freeIds.pop_back();
            return e;
        }
        int e = eu.size();
        eu.push_back(0), ev.push_back(0), elevel.push_back(0), slot.push_back(-1), seen.push_back(0);
        nxt.push_back(-1), nxt.push_back(-1), prv.push_back(-1), prv.push_back(-1);
        return e;
    }

    void addArc(int a, int l) {
        int u = owner(a), h = head[l][u];
        nxt[a] = h, prv[a] = -1;
        if (h != -1) prv[h] = a;
        head[l][u] = a;
        if (h == -1) forest[l].setVertexMark(u, true);
    }
    void delArc(int a, int l) {
        int u = owner(a), p = prv[a], q = nxt[a];
        if (p != -1) nxt[p] = q;
        else head[l][u] = q;
        if (q != -1) prv[q] = p;
        if (head[l][u] == -1) forest[l].setVertexMark(u, false);
    }

    void makeTreeEdge(int e, int l) {
        int s = freeSlots.back();
        freeSlots.pop_back();
        slot[e] = s;
        for (int i = 0; i <= l; i++) forest[i].link(eu[e], ev[e], s, e);
        forest[l].setEdgeMark(s, true);
    }

    // the heart of HDLT: hunt for an edge that reconnects the two halves
    bool replace(int l, int u, int v) {
        Forest& f = forest[l];
        int a = f.treeSize(u) <= f.treeSize(v) ? u : v;  // always walk the smaller half, so a promotion doubles a component
        int ra = f.rootOf(a);

        // every level-l tree edge of the smaller half moves up to level l + 1
        tmpEdges.clear();
        f.gather(ra, 0, tmpEdges);
        for (int x : tmpEdges) {
            int e = f.eid[x], s = slot[e];
            f.setEdgeMark(s, false);
            elevel[e] = l + 1;
            forest[l + 1].link(eu[e], ev[e], s, e);
            forest[l + 1].setEdgeMark(s, true);
        }

        // scan level-l non-tree edges out of the smaller half, stopping at the first one that crosses over
        tmpVerts.clear();
        f.gather(ra, 1, tmpVerts);
        tmpPromote.clear();
        int rep = -1;
        for (int x : tmpVerts) {
            for (int arc = head[l][f.vertexOf(x)]; arc != -1; arc = nxt[arc]) {
                int e = arc >> 1;
                if (f.rootOf(other(arc)) != ra) { rep = e; break; }
                if (!seen[e]) seen[e] = 1, tmpPromote.push_back(e);
            }
            if (rep != -1) break;
        }

        // everything we looked at and rejected has both ends inside the smaller half, so it moves up too
        for (int e : tmpPromote) {
            seen[e] = 0;
            delArc(2 * e, l), delArc(2 * e + 1, l);
            elevel[e] = l + 1;
            addArc(2 * e, l + 1), addArc(2 * e + 1, l + 1);
        }
        tmpPromote.clear();

        if (rep != -1) {
            delArc(2 * rep, l), delArc(2 * rep + 1, l);
            makeTreeEdge(rep, l);
            return true;
        }
        return l > 0 ? replace(l - 1, u, v) : false;
    }

    // O(log^2 n) amortized, returns an edge id you hand back to removeEdge
    int addEdge(int u, int v) {
        int e = newId();
        eu[e] = u, ev[e] = v, elevel[e] = 0, slot[e] = -1;
        byPair[{min(u, v), max(u, v)}].push_back(e);
        if (u == v) return e;
        if (!forest[0].sameTree(u, v)) {
            makeTreeEdge(e, 0);
            comps--;
        } else {
            addArc(2 * e, 0), addArc(2 * e + 1, 0);
        }
        return e;
    }

    // O(log^2 n) amortized, true if the component actually split in two
    bool removeEdge(int e) {
        int u = eu[e], v = ev[e], l = elevel[e], s = slot[e];
        bool split = false;
        if (s != -1) {
            forest[l].setEdgeMark(s, false);
            for (int i = 0; i <= l; i++) forest[i].cut(s);
            slot[e] = -1;
            freeSlots.push_back(s);
            split = !replace(l, u, v);
            if (split) comps++;
        } else if (u != v) {
            delArc(2 * e, l), delArc(2 * e + 1, l);
        }
        auto& ids = byPair[{min(u, v), max(u, v)}];
        ids.erase(find(ids.begin(), ids.end(), e));
        freeIds.push_back(e);
        return split;
    }

    // O(log^2 n) amortized, removes one edge between u and v, false if there was none
    bool removeEdge(int u, int v) {
        auto it = byPair.find({min(u, v), max(u, v)});
        if (it == byPair.end() || it->second.empty()) return false;
        removeEdge(it->second.back());
        return true;
    }

    // O(log n), true if u and v are in the same component
    bool areConnected(int u, int v) { return forest[0].sameTree(u, v); }

    // O(log n), how many elements are in u's component
    int size(int u) { return forest[0].treeSize(u); }

    // O(1), how many components exist right now
    int numComponents() { return comps; }

    // O(log n), opaque handle shared by exactly the vertices of u's component, invalidated by the next update
    int componentId(int u) { return forest[0].rootOf(u); }

    // O(n log n), one vertex index per component
    vector<int> roots() {
        map<int, int> rep;
        for (int u = 0; u < n; u++) rep.emplace(componentId(u), u);
        vector<int> res;
        for (auto& [k, u] : rep) res.push_back(u);
        return res;
    }

    // O(n log n), the values grouped by component
    vector<vector<T>> groups() {
        map<int, vector<T>> g;
        for (int u = 0; u < n; u++) g[componentId(u)].push_back(vals[u]);
        vector<vector<T>> res;
        for (auto& [k, v] : g) res.push_back(v);
        return res;
    }

    // O(n log n), the sizes of all components, biggest first, e.g. [4, 2, 1]
    vector<int> sizes() {
        map<int, int> cnt;
        for (int u = 0; u < n; u++) cnt[componentId(u)]++;
        vector<int> res;
        for (auto& [k, c] : cnt) res.push_back(c);
        sort(res.rbegin(), res.rend());
        return res;
    }

    // O(n log n), the values of every element sitting in the same component as index u
    vector<T> elementsInGroup(int u) {
        int r = componentId(u);
        vector<T> res;
        for (int j = 0; j < n; j++)
            if (componentId(j) == r) res.push_back(vals[j]);
        return res;
    }
};