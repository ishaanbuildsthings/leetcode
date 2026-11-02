#include <bits/stdc++.h>
using namespace std;
template <typename T>
struct ImplicitTreap {
    struct SafeHash {
        size_t operator()(const T& x) const {
            static const unsigned long long seed = chrono::steady_clock::now().time_since_epoch().count();
            unsigned long long z = (unsigned long long)x + seed + 0x9e3779b97f4a7c15ULL;
            z = (z ^ (z >> 30)) * 0xbf58476d1ce4e5b9ULL;
            z = (z ^ (z >> 27)) * 0x94d049bb133111ebULL;
            return z ^ (z >> 31);
        }
    };
    struct Node {
        unsigned long long pri = 0;
        T val = T(0);
        int L = 0;
        int R = 0;
        int sz = 0;
        int par = 0;
        bool rev = false;
    };
    struct Pool {
        vector<Node> nodes{Node{}};
        vector<int> where = vector<int>(200002, 0);
    };
    shared_ptr<Pool> pool;
    vector<Node>& nodes;
    vector<int>& where;
    int root = 0;

    explicit ImplicitTreap(const vector<T>& arr = {}) : ImplicitTreap(make_shared<Pool>()) { root = build(arr); }
    explicit ImplicitTreap(shared_ptr<Pool> p) : pool(p), nodes(p->nodes), where(p->where) {}

    static unsigned long long rnd() {
        static mt19937_64 g(chrono::steady_clock::now().time_since_epoch().count());
        return g();
    }

    int size() const { return nodes[root].sz; }

    int find(T x) {
        int t = where[x];
        vector<int> path{t};
        while (true) {
            int c = path.back(), p = nodes[c].par;
            if (!p || (nodes[p].L != c && nodes[p].R != c)) break;
            path.push_back(p);
        }
        if (path.back() != root) return -1;
        for (int k = (int)path.size() - 1; k >= 0; k--) push(path[k]);
        int i = nodes[nodes[t].L].sz;
        for (size_t k = 1; k < path.size(); k++)
            if (nodes[path[k]].R == path[k - 1]) i += nodes[nodes[path[k]].L].sz + 1;
        return i;
    }

    void rangeReverse(int l, int r) {
        int a, b, c;
        cut(l, r, a, b, c);
        applyRev(b);
        root = merge(merge(a, b), c);
    }

    int newNode(T v) {
        Node node;
        node.pri = rnd();
        node.val = v;
        node.sz = 1;
        nodes.push_back(node);
        where[v] = (int)nodes.size() - 1;
        return (int)nodes.size() - 1;
    }

    int build(const vector<T>& vals) {
        nodes.reserve(nodes.size() + vals.size());
        vector<int> stk, order, todo;
        for (const T& v : vals) {
            int x = newNode(v), last = 0;
            while (!stk.empty() && nodes[stk.back()].pri < nodes[x].pri) last = stk.back(), stk.pop_back();
            nodes[x].L = last;
            if (!stk.empty()) nodes[stk.back()].R = x;
            stk.push_back(x);
        }
        int rt = stk.empty() ? 0 : stk[0];
        if (rt) todo.push_back(rt);
        while (!todo.empty()) {
            int x = todo.back();
            todo.pop_back(), order.push_back(x);
            if (nodes[x].L) todo.push_back(nodes[x].L);
            if (nodes[x].R) todo.push_back(nodes[x].R);
        }
        for (int k = (int)order.size() - 1; k >= 0; k--) pull(order[k]);
        return rt;
    }

    void pull(int x) {
        int l = nodes[x].L, r = nodes[x].R;
        nodes[x].sz = nodes[l].sz + nodes[r].sz + 1;
        nodes[l].par = nodes[r].par = x;
    }

    void applyRev(int x) {
        if (!x) return;
        swap(nodes[x].L, nodes[x].R), nodes[x].rev ^= 1;
    }

    void push(int x) {
        if (nodes[x].rev) applyRev(nodes[x].L), applyRev(nodes[x].R), nodes[x].rev = 0;
    }

    void split(int t, int k, int& a, int& b) {
        if (!t) { a = b = 0; return; }
        push(t);
        if (nodes[nodes[t].L].sz >= k) split(nodes[t].L, k, a, nodes[t].L), b = t;
        else split(nodes[t].R, k - nodes[nodes[t].L].sz - 1, nodes[t].R, b), a = t;
        pull(t);
    }

    int merge(int a, int b) {
        if (!a || !b) return a | b;
        if (nodes[a].pri > nodes[b].pri) {
            push(a);
            nodes[a].R = merge(nodes[a].R, b);
            pull(a);
            return a;
        }
        push(b);
        nodes[b].L = merge(a, nodes[b].L);
        pull(b);
        return b;
    }

    void cut(int l, int r, int& a, int& b, int& c) {
        split(root, l, a, b);
        split(b, r - l + 1, b, c);
    }
};
int main() {
    cin.tie(nullptr);
    ios::sync_with_stdio(false);
    int n; cin >> n;
    vector<int> A(n); for (int i=0;i<n;i++) cin >> A[i];
    ImplicitTreap<int> treap(A);
    vector<pair<int,int>> out;
    for (int i = 1; i <= n; i++) {
        int idx = treap.find(i);
        out.push_back({i - 1, idx});
        treap.rangeReverse(i - 1, idx);
    }
    cout << out.size() << '\n';
    for (auto& [a, b] : out) {
        cout << (a+1) << " " << (b+1) << '\n';
    }
}