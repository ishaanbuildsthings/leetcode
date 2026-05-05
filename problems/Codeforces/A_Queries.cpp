#include <bits/stdc++.h>
using namespace std;
using ll = long long;
int MOD = 4001;
inline int add(int a, int b) { return (a + b) % MOD; }
inline int sub(int a, int b) { return (a - b + MOD) % MOD; }
inline int mul(int a, int b) { return a * b % MOD; }


const int B = 10;

struct Node {
    int odds[B] = {}; // odds[bit] -> count of how many prefixes have an odd # of bits
    int evens[B] = {};
};
struct Tag {
    bool flipped[B] = {}; // when we do a point update, we are affecting multiple suffix-ed prefix XORs
    // like if a number was 101 in binary (5) and now we set it to 000 (0) then the 0th bit and 2nd bit, for all suffixed XORs, changes
};
struct Seg {
    int n;
    vector<Node> tree;
    vector<Tag> lazy;
    Node _combine(Node& left, Node& right) {
        Node out;
        for (int b = 0; b < B; b++) {
            out.odds[b] = add(left.odds[b], right.odds[b]);
            out.evens[b] = add(left.evens[b], right.evens[b]);
        }
        return out;
    }
    void _pull(int nodeI) {
        Node& left = tree[2 * nodeI];
        Node& right = tree[2 * nodeI + 1];
        tree[nodeI] = _combine(left, right);
    }
    Tag _compose(Tag& oldT, Tag& newT) {
        Tag out;
        for (int i = 0; i < B; i++) {
            out.flipped[i] = oldT.flipped[i] ^ newT.flipped[i];
        }
        return out;
    }
    // applies this tag to the node's value, then composes it with other tags
    void _applyTagAndCompose(int nodeI, Tag t) {
        Node& node = tree[nodeI];
        for (int i = 0; i < B; i++) {
            if (t.flipped[i]) {
                swap(node.evens[i], node.odds[i]);
            }
        }
        lazy[nodeI] = _compose(lazy[nodeI], t);
    }
    void _pushDownAndClear(int nodeI) {
        _applyTagAndCompose(2 * nodeI, lazy[nodeI]);
        _applyTagAndCompose(2 * nodeI + 1, lazy[nodeI]);
        Tag t;
        lazy[nodeI] = t;
    }
    void _build(int nodeI, int tl, int tr, const vector<int>& pf) {
        if (tl == tr) {
            Node out;
            for (int b = 0; b < B; b++) {
                if (pf[tl] & (1 << b)) {
                    out.odds[b] = 1;
                } else {
                    out.evens[b] = 1;
                }
            }
            tree[nodeI] = out;
            return;
        }
        int tm = (tl + tr) / 2;
        _build(2 * nodeI, tl, tm, pf);
        _build(2 * nodeI + 1, tm + 1, tr, pf);
        _pull(nodeI);
    }
    Seg(const vector<int>& pf) {
        n = pf.size();
        tree.resize(4 * n);
        lazy.resize(4 * n);
        _build(1, 0, n - 1, pf);
    }
    Node _query(int nodeI, int tl, int tr, int ql, int qr) {
        // out of range
        if (qr < tl || ql > tr) {
            Node node;
            return node; 
        }
        // fully contained
        if (ql <= tl && qr >= tr) {
            return tree[nodeI];
        }

        _pushDownAndClear(nodeI);

        int tm = (tl + tr) / 2;
        Node left = _query(2 * nodeI, tl, tm, ql, qr);
        Node right = _query(2 * nodeI + 1, tm + 1, tr, ql, qr);
        Node out;
        for (int b = 0; b < B; b++) {
            out.evens[b] = add(left.evens[b], right.evens[b]);
            out.odds[b] = add(left.odds[b], right.odds[b]);
        }
        return out;
    }
    int query(int l, int r) {
        Node agg = _query(1, 0, n - 1, l, r);
        int out = 0;
        for (int b = 0; b < B; b++) {
            out = add(out, mul(mul((1 << b), agg.evens[b]), agg.odds[b]));
        }
        return out;
    }
    void _rangeApply(int nodeI, int tl, int tr, int ql, int qr, int delta) {
        // oob
        if (qr < tl || ql > tr) return;
        // fully inside
        if (ql <= tl && qr >= tr) {
            Tag incoming;
            for (int i = 0; i < B; i++) {
                if ((1 << i) & delta) {
                    incoming.flipped[i] = true;
                }
            }
            _applyTagAndCompose(nodeI, incoming);
            return;
        }
        _pushDownAndClear(nodeI);
        int tm = (tl + tr) / 2;
        _rangeApply(2 * nodeI, tl, tm, ql, qr, delta);
        _rangeApply(2 * nodeI + 1, tm + 1, tr, ql, qr, delta);
        _pull(nodeI);
    }
    // apply this XOR to all things in this range
    void rangeApply(int l, int r, int delta) {
        _rangeApply(1, 0, n - 1, l, r, delta);
    }
};

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n; cin >> n;
    int m; cin >> m;
    vector<int> A(n); for (int i = 0; i < n; i++) cin >> A[i];
    vector<int> pf;
    pf.push_back(0);
    int curr = 0;
    for (auto x : A) {
        curr ^= x;
        pf.push_back(curr);
    }
    Seg seg(pf);
    for (int i = 0; i < m; i++) {
        int qtype; cin >> qtype;
        if (qtype == 1) {
            int idx, newVal; cin >> idx >> newVal; idx--;
            int oldVal = A[idx];
            A[idx] = newVal;
            int diffMask = oldVal ^ newVal;
            seg.rangeApply(idx + 1, n, diffMask);
        } else {
            int l, r; cin >> l >> r; l--; r--;
            cout << seg.query(l, r + 1) << endl;
        }
    }

}