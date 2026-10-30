#include<bits/stdc++.h>
using namespace std;
mt19937 rng(12345);

struct Node {
    Node* l;
    Node* r;
    int sz;
    int v;
    int mn;
    bool lazyFlip;
    int prio;
    Node (int _v) {
        v = _v;
        mn = _v;
        l = r = nullptr;
        sz = 1;
        lazyFlip = false;
        prio = rng();
    }
};

void applyLazyAndCompose(Node* node, bool lazy) {
    if (!lazy) return;
    if (!node) return;
    swap(node->l, node->r);
    node->lazyFlip = !node->lazyFlip;
}

void pushAndClearLazy(Node* node) {
    if (!node) return;
    applyLazyAndCompose(node->l, node->lazyFlip);
    applyLazyAndCompose(node->r, node->lazyFlip);
    node->lazyFlip = false;
}


void pull(Node* node) {
    if (!node) return;
    int mn = node->v;
    int sz = 1;
    if (node->l) {
        sz += node->l->sz;
        mn = min(mn, node->l->mn);
    }
    if (node->r) {
        sz += node->r->sz;
        mn = min(mn, node->r->mn);
    }
    node->sz = sz;
    node->mn = mn;
}

pair<Node*, Node*> split(Node* node, int k) {
    if (!node) return {nullptr, nullptr};
    pushAndClearLazy(node);
    int onLeft = 0;
    if (node->l) onLeft += node->l->sz;
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
    if (!left) return right;
    if (!right) return left;
    pushAndClearLazy(left);
    pushAndClearLazy(right);
    if (left->prio < right->prio) {
        left->r = merge(left->r, right);
        pull(left);
        return left;
    }
    right->l = merge(left, right->l);
    pull(right);
    return right;
}

tuple<Node*, Node*, Node*> trisect(Node* node, int l, int r) {
    auto [first, rest] = split(node, l);
    auto [middle, last] = split(rest, r - l + 1);
    return {first, middle, last};
}

Node* trimerge(Node* left, Node* middle, Node* right) {
    return merge(merge(left, middle), right);
}

int findIdxOfMin(Node* node) {
    Node* curr = node;
    int onLeft = 0;
    while (true) {
        pushAndClearLazy(curr);
        if (!curr->l && !curr->r) break;
        bool minInLeft = (curr->l && curr->l->mn == curr->mn);
        if (minInLeft) {
            curr = curr->l;
            continue;
        }
        if (curr->mn == curr->v) {
            int gainLeft = 0;
            if (curr->l) gainLeft += curr->l->sz;
            onLeft += gainLeft;
            return onLeft;
        }
        int gainOnLeft = 1;
        if (curr->l) gainOnLeft += curr->l->sz;
        onLeft += gainOnLeft;
        curr = curr->r;
    }
    return onLeft;
}


int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n; cin >> n;
    vector<int> A(n); for (int i = 0; i < n; i++) cin >> A[i];
    Node* root = nullptr;
    for (int i = 0; i < n; i++) {
        int v = A[i];
        root = merge(root, new Node(v));
    }
    vector<pair<int,int>> res;
    for (int val = 1; val <= n; val++) {
        auto [prefix, suffix] = split(root, val - 1);
        int idx = findIdxOfMin(suffix);
        res.push_back({val, val + idx});
        auto [first, mid, right] = trisect(suffix, 0, idx);
        applyLazyAndCompose(mid, true);
        root = merge(prefix, trimerge(first, mid, right));
    }
    cout << res.size() << '\n';
    for (auto [l, r] : res) {
        cout << l << " " << r  << '\n';
    }
}