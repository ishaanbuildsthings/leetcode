#include <bits/stdc++.h>
using namespace std;

const long long BASE = 27;
const long MOD = 1000000000 + 7;
vector<long long> modBasePow; // modBasePow[pow] = base^pow % MOD
int MAX_POW = 1000000;

struct PalindromeSeg {
    string s;

    struct Node {
        long long fh = 0;
        long long rh = 0;
        int width = 0;
    };

    vector<Node> tree;

    PalindromeSeg(string _s) {
        s = _s;
        tree.resize(s.size() * 4 + 5);
        build();
    }

    Node merge(Node left, Node right) {
        int newWidth = left.width + right.width;
        // forward hash means left index is a higher power
        long long leftFhContribution = (left.fh * modBasePow[right.width]) % MOD;
        long long newFh = (leftFhContribution + right.fh) % MOD;

        // rev hash means right index is a higher power
        long long rightRhContribution = (right.rh * modBasePow[left.width]) % MOD;
        long long newRh = (rightRhContribution + left.rh) % MOD;

        return Node{newFh, newRh, newWidth};
    }

    void pull(int i) {
        tree[i] = merge(tree[2 * i], tree[2 * i + 1]);
    }

    void build() {
        _build(1, 0, s.size() - 1);
    }

    Node leaf(char c) {
        return Node{c - 'a' + 1, c - 'a' + 1, 1};
    }

    void _build(int i, int tl, int tr) {
        if (tl == tr) {
            tree[i] = leaf(s[tl]);
            return;
        }
        int tm = (tr + tl) / 2;
        _build(2 * i, tl, tm);
        _build(2 * i + 1, tm + 1, tr);
        pull(i);
    }

    void pointAssign(int pos, char newC) {
        _pointAssign(1, 0, s.size() - 1, pos, newC);
    }

    void _pointAssign(int i, int tl, int tr, int pos, char newC) {
        if (tl == tr) {
            tree[i] = leaf(newC);
            return;
        }
        int tm = (tr + tl) / 2;
        if (pos <= tm) {
            _pointAssign(2 * i, tl, tm, pos, newC);
        } else {
            _pointAssign(2 * i + 1, tm + 1, tr, pos, newC);
        }
        pull(i);
    }

    Node query(int l, int r) {
        return _query(1, 0, s.size() - 1, l, r);
    }

    Node _query(int i, int tl, int tr, int ql, int qr) {
        // if we are fully in range, return our node
        if (ql <= tl && qr >= tr) {
            return tree[i];
        }
        int tm = (tr + tl) / 2;
        // If only left is in range return that
        if (qr <= tm) {
            return _query(2 * i, tl, tm, ql, qr);
        }
        // Only right in range
        if (ql >= tm + 1) {
            return _query(2 * i + 1, tm + 1, tr, ql, qr);
        }

        Node left = _query(2 * i, tl, tm, ql, qr);
        Node right = _query(2 * i + 1, tm + 1, tr, ql, qr);
        return merge(left, right);
    }

    bool isPal(int l, int r) {
        Node finalNode = query(l, r);
        return finalNode.fh == finalNode.rh;
    }
};

void initPow() {
    modBasePow.push_back(1);
    for (int power = 1; power <= MAX_POW; power++) {
        long long newV = (modBasePow.back() * BASE) % MOD;
        modBasePow.push_back(newV);
    }
}

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n, m; cin >> n >> m;
    string s; cin >> s;
    initPow();
    PalindromeSeg st(s);
    for (int i = 0; i < m; i++) {
        int op; cin >> op;
        if (op == 1) {
            int k; cin >> k; k--;
            char newC; cin >> newC;
            st.pointAssign(k, newC);
        } else {
            int a, b; cin >> a >> b; a--; b--;
            if (st.isPal(a, b)) {
                cout << "YES";
            } else {
                cout << "NO";
            }
            cout << endl;
        }
    }
}