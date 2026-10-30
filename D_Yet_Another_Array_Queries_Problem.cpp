#include <bits/stdc++.h>
using namespace std;
mt19937 rng(12345);

struct Node {
    int sz;
    int v;
    Node* l;
    Node* r;
    bool lazyFlip;
    int prio;
    Node (int _v) {
        sz = 1;
        v = _v;
        l = r = nullptr;
        prio = rng();
        lazyFlip = false;
    }
};

bool composeLazies(bool lazy1, bool lazy2) {
    return lazy1 ^ lazy2;
}

void applyLazyAndCompose(Node* node, bool incoming) {
    if (!node) return;
    if (!incoming) return;
    swap(node->l, node->r);
    node->lazyFlip = composeLazies(node->lazyFlip, incoming);
}

void pull(Node* node) {
    if (!node) return;
    int nsize = 1;
    if (node->l) nsize += node->l->sz;
    if (node->r) nsize += node->r->sz;
    node->sz = nsize;
}

// apply lazy values here to children, and clear this lazy tag
void push(Node* node) {
    if (!node) return;
    applyLazyAndCompose(node->l, node->lazyFlip);
    applyLazyAndCompose(node->r, node->lazyFlip);
    node->lazyFlip = false;
}


Node* merge(Node* left, Node* right) {
    if (!left) return right;
    if (!right) return left;
    push(left);
    push(right);
    // left goes above
    if (left->prio < right->prio) {
        Node* nright = merge(left->r, right);
        left->r = nright;
        pull(left);
        return left;
    }
    // right goes above
    Node* nleft = merge(left, right->l);
    right->l = nleft;
    pull(right);
    return right;
}

pair<Node*, Node*> split(Node* node, int k) {
    if (!node) return {nullptr, nullptr};
    push(node);
    int onLeft = 0;
    if (node->l) onLeft += node->l->sz;
    // if root is part of left section
    if (onLeft + 1 <= k) {
        auto [first, second] = split(node->r, k - (onLeft + 1));
        node->r = first;
        pull(node);
        return {node, second};
    }
    // root is part of right section
    auto [first, second] = split(node->l, k);
    node->l = second;
    pull(node);
    return {first, node};
}

tuple<Node*, Node*, Node*> trisect(Node* node, int l, int r) {
    auto [first, rest] = split(node, l);
    auto [middle, right] = split(rest, r - l + 1);
    return {first, middle, right};
}

Node* join(Node* left, Node* middle, Node* right) {
    return merge(merge(left, middle), right);
}


int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n, q, m; cin >> n >> q >> m;
    vector<int> A(n); for (int i = 0; i < n; i++) cin >> A[i];

    Node* root = nullptr;
    for (int i = 0; i < n; i++) {
        int v = A[i];
        root = merge(root, new Node(v));
    }
    for (int i = 0; i < q; i++) {
        int qtype, l, r; cin >> qtype >> l >> r; l--; r--;
        if (qtype == 1) {
            auto [left, mid, right]= trisect(root, l, r);
            int width = r - l + 1;
            auto [L, single] = split(mid, width - 1);
            auto newMid = merge(single, L);
            root = join(left, newMid, right);
        } else {
            auto [left, mid, right] = trisect(root, l, r);
            applyLazyAndCompose(mid, true);
            root = join(left, mid, right);
        }
    }
    vector<int> order;
    auto dfs = [&](auto&& self, Node* node) -> void {
        if (!node) return;
        push(node);
        self(self, node->l);
        order.push_back(node->v);
        self(self, node->r);
    };
    dfs(dfs, root);

    for (int i = 0; i < m; i++) {
        int importantIdx; cin >> importantIdx; importantIdx--;
        cout << order[importantIdx] << " ";
    }
}