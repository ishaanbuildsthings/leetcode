#include <bits/stdc++.h>
using namespace std;
using ll = long long;

const ll MOD = 1000000007;
const ll MAX_N = 200001;
const ll BASE = 911;
ll basePow[MAX_N + 1];

struct Node {
    ll fw = 0;
    ll rev = 0;
    int width = 1;
};

struct Seg {
    vector<Node> tree;
    int n;
    string s;
    Seg(string& _s) {
        s = _s;
        n = s.size();
        tree.resize(4 * n);
        _build(1, 0, n - 1);
    }

    Node leaf(char c) {
        int coeff = c - 'a' + 1;
        return {
            coeff, coeff, 1
        };
    }

    void _build(int nodeI, int tl, int tr) {
        if (tl == tr) {
            tree[nodeI] = leaf(s[tl]);
            return;
        }
        int tm = (tl + tr) / 2;
        _build(2 * nodeI, tl, tm);
        _build(2 * nodeI + 1, tm + 1, tr);
        _pull(nodeI);
    }

    void _pull(int nodeI) {
        Node& left = tree[2 * nodeI];
        Node& right = tree[2 * nodeI + 1];
        tree[nodeI] = merge(left, right);
    }

    Node merge(Node& left, Node& right) {
        ll newForward = ((left.fw * basePow[right.width]) + right.fw) % MOD;
        ll newRev = (((right.rev * basePow[left.width])) + left.rev) % MOD;
        return {newForward, newRev, left.width + right.width};
    }

    void pointUpdate(int pos, char newC) {
        _pointUpdate(1, 0, n - 1, pos, newC);
    }

    void _pointUpdate(int nodeI, int tl, int tr, int pos, char newC) {
        if (tl == tr) {
            tree[nodeI] = leaf(newC);
            return;
        }
        int tm = (tl + tr) / 2;
        if (pos <= tm) {
            _pointUpdate(2 * nodeI, tl, tm, pos, newC);
        } else {
            _pointUpdate(2 * nodeI + 1, tm + 1, tr, pos, newC);
        }
        _pull(nodeI);
    }

    Node _query(int nodeI, int tl, int tr, int ql, int qr) {
        if (ql <= tl && qr >= tr) {
            return tree[nodeI];
        }
        int tm = (tl + tr) / 2;
        if (qr <= tm) {
            return _query(2 * nodeI, tl, tm, ql, qr);
        } else if (ql >= tm + 1) {
            return _query(2 * nodeI + 1, tm + 1, tr, ql, qr);
        }
        Node left = _query(2 * nodeI, tl, tm, ql, qr);
        Node right = _query(2 * nodeI + 1, tm + 1, tr, ql, qr);
        return merge(left, right);
    }

    Node query(int l, int r) {
        return _query(1, 0, n - 1, l, r);
    }
};

void init() {
    ll curr = 1;
    for (int p = 0; p <= MAX_N; p++) {
        basePow[p] = curr;
        curr *= BASE;
        curr %= MOD;
    }
}

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    init();
    int n, m; cin >> n >> m;
    string s; cin >> s;
    Seg seg(s);
    while (m--) {
        int qtype; cin >> qtype;
        if (qtype == 1) {
            int pos; cin >> pos; pos--;
            char c; cin >> c;
            seg.pointUpdate(pos, c);
        } else {
            int a, b; cin >> a >> b; a--; b--;
            Node out = seg.query(a, b);
            cout << (out.fw == out.rev ? "YES" : "NO") << '\n';
        }
    }
}