#include <bits/stdc++.h>
using namespace std;

struct DynSeg {
    struct Node {
        int pref;
        int suff;
        int max;
        int width;
        int left = -1; // indices
        int right = -1;
    };
    int low;
    int high;
    int ptr = 0;
    vector<Node> tree;
    DynSeg(int _low, int _high, int maxNodes) {
        low = _low;
        high = _high;
        int widthRoot = high - low + 1;
        tree.resize(maxNodes);
        safeMake(widthRoot);
    }

    int safeMake(int width) {
        tree[ptr] = Node{width, width, width, width};
        ptr++;
        return ptr - 1;
    }

    Node merge(Node& left, Node&right) {
        int npref = left.pref;
        if (left.pref == left.width) npref += right.pref;
        int nsuff = right.suff;
        if (right.suff == right.width) nsuff += left.suff;
        int nwidth = left.width + right.width;
        int nmax = max({left.max, right.max, left.suff + right.pref});
        return Node{npref, nsuff, nmax, nwidth};
    }

    int queryAll() {
        return tree[0].max;
    }
    void pointLight(int pos) {
        _pointLight(0, low, high, pos);
    }
    void _pointLight(int i, int tl, int tr, int pos) {
        if (tl == tr) {
            tree[i] = Node{0, 0, 0, 1};
            return;
        }
        int tm = (tr + tl) / 2;
        Node& node = tree[i];
        if (node.left == -1) {
            int leftWidth = tm - tl + 1;
            int leftNodeIdx = safeMake(leftWidth);
            node.left = leftNodeIdx;

        }
        if (node.right == -1) {
            int rightWidth = tr - (tm + 1) + 1;
            int rightNodeIdx = safeMake(rightWidth);
            node.right = rightNodeIdx;
        }
        if (pos <= tm) {
            _pointLight(node.left, tl, tm, pos);
        } else {
            _pointLight(node.right, tm + 1, tr, pos);
        }
        pull(i);
    }

    void pull(int i) {
        Node merged = merge(tree[tree[i].left], tree[tree[i].right]);
        tree[i].pref = merged.pref;
        tree[i].suff = merged.suff;
        tree[i].max = merged.max;
        tree[i].width = merged.width;
    }
};

int main() {
    cin.tie(nullptr);
    ios::sync_with_stdio(false);
    int x, n; cin >> x >> n;
    vector<int> A(n); for (int i = 0; i < n; i++) cin >> A[i];
    DynSeg seg(0, x, 30 * n); // rough guess
    seg.pointLight(0);
    seg.pointLight(x);
    for (auto x : A) {
        seg.pointLight(x);
        cout << seg.queryAll() + 1 << " ";
    }
}
