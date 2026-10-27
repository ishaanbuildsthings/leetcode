#include <bits/stdc++.h>
using namespace std;
mt19937 rng(12345);

struct Node {
    int sz;
    long long val;
    Node* l;
    Node* r;
    int prio;
    bool lazyRev;
    long long sum = 0;
    Node (long long _val) {
        val = _val;
        sum = _val;
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
    long long nsum = node->val;
    if (node->l) {
        nsize += node->l->sz;
        nsum += node->l->sum;
    }
    if (node->r) {
        nsize += node->r->sz;
        nsum += node->r->sum;
    }
    node->sz = nsize;
    node->sum = nsum;
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
    vector<long long> A(n); for (int i = 0; i < n; i++) cin >> A[i];
    Node* root = nullptr;
    for (int i = 0; i < n; i++) {
        long long v = A[i];
        root = merge(root, new Node(v));
    }
    for (int i = 0; i < m; i++) {
        int qtype, a, b; cin >> qtype >> a >> b;
        if (qtype == 1) {
            a--; b--;
            auto [left, middle, right] = trisect(root, a, b);
            reverse(middle);
            root = join(left, middle, right);
        } else {
            auto [left, middle, right] = trisect(root, a, b);
            cout << middle->sum << '\n';
            root = join(left, middle, right);
        }
    }
}