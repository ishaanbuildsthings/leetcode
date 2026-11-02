#include <bits/stdc++.h>
using namespace std;
mt19937 rng(12345);

struct Node {
    char c;
    Node* l;
    Node* r;
    int prio;
    int sz;
    Node(char _c) {
        c = _c;
        sz = 1;
        l = nullptr;
        r = nullptr;
        prio = rng();
    }
};

void updateSize(Node* node) {
    int nsz = 1;
    if (node->l) {
        nsz += node->l->sz;
    }
    if (node->r) {
        nsz += node->r->sz;
    }
    node->sz = nsz;
}

Node* merge(Node* left, Node* right) {
    if (left == nullptr) return right;
    if (right == nullptr) return left;
    // if left is above right, right merges with left's right child
    if (left->prio < right->prio) {
        Node* nright = merge(left->r, right);
        left->r = nright;
        updateSize(left);
        return left;
    } else {
        // if right is above left, left merges into right's left child
        Node* nleft = merge(left, right->l);
        right->l = nleft;
        updateSize(right);
        return right;
    }
};

// gives us two treaps, the first up to K and the remaining ones
pair<Node*, Node*> split(Node* node, int k) {
    if (node == nullptr) return {nullptr, nullptr};
    int leftSize = 0;
    if (node->l) {
        leftSize = node->l->sz;
    }
    int pos = leftSize + 1; // our current node
    if (pos <= k) {
        // node and left go to first piece, only some of the right is in the first portion
        auto [firstPortion, secondPortion] = split(node->r, k - pos);
        node->r = firstPortion;
        updateSize(node);
        return {node, secondPortion};
    }
    // some of the left is in the first portion
    auto [firstPortion, secondPortion] = split(node->l, k);
    node->l = secondPortion;
    updateSize(node);
    return {firstPortion, node};
}

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n, m; cin >> n >> m;
    vector<char> A(n);
    for (int i = 0; i < n; i++) cin >> A[i];
    Node* root = new Node(A[0]);
    for (int i = 1; i < n; i++) {
        char c = A[i];
        Node* node = new Node(c);
        root = merge(root, node);
    }
    for (int i = 0; i < m; i++) {
        int a, b; cin >> a >> b;
        auto [one, twoThree] = split(root, a - 1);
        auto [two, three] = split(twoThree, b - a + 1);
        Node* newLeft = merge(one, three);
        root = merge(newLeft, two);
    }

    auto print = [&](auto&& self, Node* node) -> void {
        if (node == nullptr) return;
        self(self, node->l);
        cout << node->c;
        self(self, node->r);
    };

    print(print, root);
}