#include <bits/stdc++.h>
using namespace std;
mt19937 rng(12345);

struct Node {
    int sz;
    char c;
    Node* l;
    Node* r;
    int prio;
    bool lazyRev;
    Node (char _c) {
        c = _c;
        sz = 1;
        prio = rng();
        lazyRev = false;
        l = nullptr;
        r = nullptr;
    }
};

void flip(Node* node) {
    if (node == nullptr) return;
    swap(node->l, node->r);
}

// should be apply tag and compose
void reverse(Node* node) {
    flip(node);
    node->lazyRev = !(node->lazyRev);
}

// pushDownAndClearLazies
void push(Node* node) {
    if (node == nullptr) return;
    if (!(node->lazyRev)) return;
    node->lazyRev = false;
    
    if (node->l) {
        flip(node->l);
        node->l->lazyRev = !node->l->lazyRev;
    }
    if (node->r) {
        flip(node->r);
        node->r->lazyRev = !node->r->lazyRev;
    }    
}

void pull(Node* node) {
    if (node == nullptr) return;
    int nsize = 1;
    if (node->l) {
        nsize += node->l->sz;
    }
    if (node->r) {
        nsize += node->r->sz;
    }
    node->sz = nsize;
}

pair<Node*, Node*> split(Node* node, int k) {
    if (node == nullptr) return {nullptr, nullptr};
    push(node);
    int onLeft = 0;
    if (node->l) {
        onLeft += node->l->sz;
    }
    if (onLeft >= k) {
        auto [first, second] = split(node->l, k);
        node->l = second;
        pull(node);
        return {first, node};
    }
    auto [first, second] = split(node->r, k - onLeft - 1);
    node->r = first;
    pull(node);
    return {node, second};
}

Node* merge(Node* left, Node* right) {
    if (left == nullptr) return right;
    if (right == nullptr) return left;
    if (left->prio < right->prio) {
        push(left);
        Node* rightMerged = merge(left->r, right);
        left->r = rightMerged;
        pull(left);
        return left;
    }
    // left goes below
    push(right);
    Node* leftMerged = merge(left, right->l);
    right->l = leftMerged;
    pull(right);
    return right;
}

tuple<Node*, Node*, Node*> trisect(Node* node, int l, int r) {
    auto [left, rest] = split(node, l);
    auto [middle, right] = split(rest, r - l + 1);
    return {left, middle, right};
}

Node* join(Node* left, Node* middle, Node* right) {
    return merge(merge(left, middle), right);
}


int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n, m; cin >> n >> m;
    string s; cin >> s;
    Node* root = nullptr;
    for (int i = 0; i < n; i++) {
        char c = s[i];
        Node* node = new Node(c);
        root = merge(root, node);
    }

    for (int i = 0; i < m; i++) {
        int l, r; cin >> l >> r; l--; r--;
        auto [left, middle, right] = trisect(root, l, r);
        reverse(middle);
        root = join(left, middle, right);
    }

    auto read = [&](auto&& self, Node* node) -> void {
        if (node == nullptr) return;
        push(node);
        self(self, node->l);
        cout << node->c;
        self(self, node->r);
    };

    read(read, root);
}