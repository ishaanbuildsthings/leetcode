#include<bits/stdc++.h>
using namespace std;

const long long BASE = 27;
// const int MOD = 1000000000 + 7;
const int MOD = 998244353;
const int MAX_N = 2 * 100000 + 5;

long long basePowMod[MAX_N];

void initPow() {
    basePowMod[0] = 1;
    for (int power = 1; power < MAX_N; power++) {
        long long newV = (basePowMod[power - 1] * BASE) % MOD;
        basePowMod[power] = newV;
    }
};

struct SegTreeHash {
    struct Node {
        long long fh, rh; // forward hash, reverse hash
    };

    vector<Node> tree;
    int n;
    string s;

    Node leaf(char v) {
        return Node{v - 'a' + 1, v - 'a' + 1};
    }

    void build(int treeI, int tl, int tr) {
        // cerr << "build called on treeI=" << treeI << " tl:" << tl << " tr:" << tr << endl;
        if (tl == tr) {
            tree[treeI] = leaf(s[tl]);
            return;
        }
        int tm = (tr + tl) / 2;
        build(2*treeI, tl, tm);
        build(2*treeI + 1, tm + 1, tr);
        int leftWidth = tm - tl + 1;
        int rightWidth = tr - (tm + 1) + 1;
        tree[treeI] = merge(tree[2 * treeI], tree[2 * treeI + 1], leftWidth, rightWidth);
    };

    SegTreeHash(string& _s) {
        s = _s;
        n = s.size();
        tree.resize(4 * n + 5);
        // cerr << "building now: " << endl;
        build(1, 0, n - 1);
        // cerr << "built" << endl;
    }

    Node merge(Node left, Node right, int leftWidth, int rightWidth) {
        long long newFh = (((left.fh * basePowMod[rightWidth]) % MOD) + right.fh) % MOD;
        // long long newRh = (((left.rh * basePowMod[rightWidth]) % MOD) + right.rh) % MOD;
        long long newRh = (((right.rh * basePowMod[leftWidth]) % MOD) + left.rh) % MOD;

        return Node({newFh, newRh});
    };

    void update(int pos, char c) {
        _updateRecurse(1, 0, n - 1, pos, c);
    };
    
    void _updateRecurse(int treeI, int tl, int tr, int pos, char c) {
        if (tl == tr) {
            tree[treeI] = leaf(c);
            return;
        }
        int tm = (tr + tl) / 2;
        if (pos <= tm) {
            _updateRecurse(2 * treeI, tl, tm, pos, c);
        } else {
            _updateRecurse(2 * treeI + 1, tm + 1, tr, pos, c);
        }
        tree[treeI] = merge(tree[2 * treeI], tree[2 * treeI + 1], tm - tl + 1, (tr - (tm + 1)) + 1);
    };

    Node _query(int treeI, int tl, int tr, int ql, int qr) {
        // full contained
        if (ql <= tl && qr >= tr) {
            return tree[treeI];
        }
        int tm = (tr + tl) / 2;
        // fully in left child
        if (qr <= tm) {
            return _query(2 * treeI, tl, tm, ql, qr);
        }
        // fully in right child
        if (ql >= tm + 1) {
            return _query(2 * treeI + 1, tm + 1, tr, ql, qr);
        }
        // in both
        // Node leftPart = _query(2 * treeI, tl, tm, ql, qr);
        // Node rightPart = _query(2 * treeI + 1, tm + 1, tr, ql, qr);
        // return merge(leftPart, rightPart, tm - ql + 1, qr - (tm + 1) + 1);
        Node leftPart  = _query(2 * treeI, tl, tm, ql, tm);
        Node rightPart = _query(2 * treeI + 1, tm + 1, tr, tm + 1, qr);
        return merge(leftPart, rightPart, tm - ql + 1, qr - (tm + 1) + 1);
        
    }

    Node query(int ql, int qr) {
        return _query(1, 0, n - 1, ql, qr);
    }
};

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    initPow();
    int n, m;
    cin >> n >> m;
    string s; cin >> s;
    SegTreeHash st = SegTreeHash(s);

    for (int i = 0; i < m; i++) {
        int op; cin >> op;
        if (op == 1) {
            int k; cin >> k; k -= 1;
            char c; cin >> c;
            // update index k to be char c
            st.update(k, c);
        } else {
            int a, b; cin >> a >> b; // check if a...b is a palindrome
            a -= 1; b -= 1;
            auto node = st.query(a, b);
            if (node.fh == node.rh) {
                cout << "YES" << endl;
            } else {
                cout << "NO" << endl;
            }
        }
    }
}