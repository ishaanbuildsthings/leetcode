#include <bits/stdc++.h>
using namespace std;


struct DynSeg {
    struct Node {
        int count;
        Node* l;
        Node* r;
    };
    Node root;
    int low;
    int high;
    DynSeg(int _low, int _high) {
        low = _low;
        high = _high;
        root = Node{0};
    }

    void pointUpdate(int pos) {
        _pointUpdate(root, low, high, pos);
    }
    void _pointUpdate(Node& node, int tl, int tr, int pos) {
        if (tl == tr) {
            node.count++;
            return;
        }
        int tm = (tr + tl) / 2;
        if (!node.l) {
            node.l = new Node{0};
        }
        if (!node.r) {
            node.r = new Node{0};
        }
        if (pos <= tm) {
            _pointUpdate(*node.l, tl, tm, pos);
        } else {
            _pointUpdate(*node.r, tm + 1, tr, pos);
        }
        pull(node);
    }
    void pull(Node& node) {
        node.count = node.l->count + node.r->count;
        return;
    }

    long long query(int l, int r) {
        return _query(root, low, high, l, r);
    }
    long long _query(Node& node, int tl, int tr, int ql, int qr) {
        if (ql <= tl && qr >= tr) {
            return node.count;
        }
        if (ql > tr || qr < tl) {
            return 0;
        }
        int tm = (tr + tl) / 2;
        if (!node.l) {
            node.l = new Node();
        }
        if (!node.r) {
            node.r = new Node();
        }
        return _query(*node.l, tl, tm, ql, qr) + _query(*node.r, tm + 1, tr, ql, qr);
    }
};


int main() {
    cin.tie(nullptr);
    ios::sync_with_stdio(false);
    int t; cin >> t;
    while (t--) {
        long long n; cin >> n;
        long long out = 0;
        vector<int> A(n); for (int i = 0; i < n; i++) cin >> A[i];
        DynSeg seg(0, 1000000000);
        for (int i = n - 1; i >= 0; i--) {
            int num = A[i];
            out += seg.query(0, num - 1);
            seg.pointUpdate(num);
        }
        bool result = out <= n * (n - 1) / 2 - 1;
        cout << (result ? "YES" : "NO") << endl;
    }
}