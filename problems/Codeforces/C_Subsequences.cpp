#include <bits/stdc++.h>
using namespace std;
using ll = long long;

// number of subsequences ending in this value range of length 1, 2, 3, ...
struct Node {
    ll cnt[12];
};

struct Seg {
    int U; // universe is 0...U
    vector<Node> tree;

    Seg(int _U) {
        U = _U;
        tree.resize(4 * (U + 5));
    }

    void _pull(int nodeI) {
        tree[nodeI] = _combine(tree[2 * nodeI], tree[2 * nodeI + 1]);
    }

    Node _combine(Node& a, Node& b) {
        Node out{};
        for (int i = 0; i < 12; i++) {
            out.cnt[i] = a.cnt[i] + b.cnt[i]; // number of subsequences ending in lo...hi of size X is the total amount of subsequences ending in lo...mid of size X, plus those in the right
        }
        return out;
    }

    Node _query(int nodeI, int tlo, int thi, int qlo, int qhi) {
        if (tlo == thi) {
            return tree[nodeI];
        }
        if (qlo <= tlo && qhi >= thi) {
            return tree[nodeI];
        }
        int tmi = (tlo + thi) / 2;
        if (qhi <= tmi) {
            Node left = _query(2 * nodeI, tlo, tmi, qlo, qhi);
            return left;
        } else if (qlo >= tmi + 1) {
            Node right = _query(2 * nodeI + 1, tmi + 1, thi, qlo, qhi);
            return right;
        }
        Node left = _query(2 * nodeI, tlo, tmi, qlo, qhi);
        Node right = _query(2 * nodeI + 1, tmi + 1, thi, qlo, qhi);
        return _combine(left, right);
    }

    // how many subsequences in the entire seg tree have a value range lo...hi
    Node query(int lo, int hi) {
        return _query(1, 0, U, lo, hi);
    }

    void _pointAdd(int nodeI, int tlo, int thi, int endingNumber, const Node& payload) {
        if (tlo == thi) {
            for (int i = 0; i < 12; i++) {
                tree[nodeI].cnt[i] += payload.cnt[i];
            }
            return;
        }
        int tmi = (tlo + thi) / 2;
        if (endingNumber <= tmi) {
            _pointAdd(2 * nodeI, tlo, tmi, endingNumber, payload);
        } else {
            _pointAdd(2 * nodeI + 1, tmi + 1, thi, endingNumber, payload);
        }
        _pull(nodeI);
    }

    // we are saying we can form new subsequences ending with this number, and the count of how many there are
    void pointAdd(int endingNumber, const Node& payload) {
        _pointAdd(1, 0, U, endingNumber, payload);
    }
    
};

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n, k; cin >> n >> k;
    Seg seg(100000);
    for (int i = 0; i < n; i++) {
        int num; cin >> num;
        Node prevValid = seg.query(0, num - 1); // how many previous subsequences we have ending with any number below num of those lengths
        // we can append our number to any of these, forming a new subsequence
        Node incoming{};
        for (int j = 1; j < 12; j++) {
            incoming.cnt[j] = prevValid.cnt[j - 1];
        }
        incoming.cnt[1]++; // form a subsequence by itself
        seg.pointAdd(num, incoming);
    }
    cout << seg.tree[1].cnt[k + 1];
}