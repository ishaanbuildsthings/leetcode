#include <bits/stdc++.h>
using namespace std;
mt19937 rng(12345);
using ll = long long;


struct Node {
    char c;
    int arr[10];
    int sz;
    Node* l;
    Node* r;
    int prio;
    bool lazyFlip;
    Node (char _c) {
        c = _c;
        for (int i = 0; i < 10; i++) arr[i] = 0;
        arr[_c - 'a']++;
        sz = 1;
        l = r = nullptr;
        prio = rng();
        lazyFlip = false;
    }
};

void apply(Node* node, bool flip) {
    if (!node) return;
    if (!flip) return;
    swap(node->l, node->r);
    node->lazyFlip = !node->lazyFlip;
}

void push(Node* node) {
    if (!node) return;
    apply(node->l, node->lazyFlip);
    apply(node->r, node->lazyFlip);
    node->lazyFlip = false;
}

void pull(Node* node) {
    if (!node) return;
    for (int i = 0; i < 10; i++) {
        node->arr[i] = 0;
    }
    node->arr[node->c - 'a'] = 1;
    int sz = 1;
    if (node->l) {
        sz += node->l->sz;
        for (int i = 0; i < 10; i++) {
            node->arr[i] += node->l->arr[i];
        }
    }
    if (node->r) {
        sz += node->r->sz;
        for (int i = 0; i < 10; i++) {
            node->arr[i] += node->r->arr[i];
        }
    }
    node->sz = sz;
}

pair<Node*, Node*> split(Node* node, int k) {
    if (!node) return {nullptr, nullptr};
    push(node);
    int onLeft = 0;
    if (node->l) onLeft += node->l->sz;
    if (onLeft >= k) {
        auto [left, right] = split(node->l, k);
        node->l = right;
        pull(node);
        return {left, node};
    }
    auto [left, right] = split(node->r, k - onLeft - 1);
    node->r = left;
    pull(node);
    return {node, right};
}

tuple<Node*, Node*, Node*> trisect(Node* node, int l, int r) {
    auto [left, rest] = split(node, l);
    auto [mid, right] = split(rest, r - l + 1);
    return {left, mid, right};
}

Node* merge(Node* left, Node* right) {
    if (!left) return right;
    if (!right) return left;
    push(left);
    push(right);
    // left above
    if (left->prio < right->prio) {
        Node* nright = merge(left->r, right);
        left->r = nright;
        pull(left);
        return left;
    }
    Node* nleft = merge(left, right->l);
    right->l = nleft;
    pull(right);
    return right;
}

Node* trimerge(Node* left, Node* mid, Node* right) {
    return merge(merge(left, mid), right);
}





int MOD = 1000000007;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n, q; cin >> n >> q;
    string s; cin >> s;
    
    vector<ll> modFac;
    modFac.push_back(1);
    for (int i = 1; i <= n; i++) {
        ll newV = (modFac.back() * i) % MOD;
        modFac.push_back(newV);
    }
    
    vector<ll> invFac(n + 1, 0);
    auto modPow = [&](auto&& self, ll base, int e) -> ll {
        if (e == 0) return 1;
        if (e % 2) {
            return (base * self(self, base, e - 1)) % MOD;
        }
        ll half = self(self, base, e / 2);
        return (half * half) % MOD;
    };
    invFac[n] = modPow(modPow, modFac[n], MOD - 2);
    for (int i = n; i >= 1; i--) invFac[i - 1] = (invFac[i] * i) % MOD;
    
    auto ways = [&](vector<int>& cnts) -> ll {
      int tot = 0;
      for (auto x : cnts) tot += x;
      ll allWays = modFac[tot];
      for (auto cnt : cnts) {
          allWays *= invFac[cnt];
          allWays %= MOD;
      }
      return allWays;
    };
    
    vector<char> A(s.begin(), s.end());
    Node* root = nullptr;
    for (int i = 0; i < n; i++) {
        char c = A[i];
        Node* node = new Node(c);
        root = merge(root, node);
    }
    for (int i = 0; i < q; i++) {
        int qtype, l, r; cin >> qtype >> l >> r; l--; r--;
        if (qtype == 1) {
            auto [left, mid, right] = trisect(root, l, r);
            apply(mid, true);
            root = trimerge(left, mid, right);
        } else {
            auto [left, mid, right] = trisect(root, l, r);
            int odds = 0;
            for (int i = 0; i < 10; i++) {
                if (mid->arr[i] % 2) {
                    odds++;
                }
            }
            if (odds > 1) {
                root = trimerge(left, mid, right);
                cout << 0 << '\n';
                continue;
            }
            vector<int> cnts;
            for (int i = 0; i < 10; i++) {
                cnts.push_back(mid->arr[i] / 2);
            }
            cout << ways(cnts) << '\n';
            root = trimerge(left, mid, right);
        }
    }
}