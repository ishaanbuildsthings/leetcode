#include <bits/stdc++.h>
using namespace std;

vector<vector<int>> edgeListToTree(const vector<pair<int, int>>& edgeList, int n) {
    vector<vector<int>> edgeMap(n + 1);
    for (auto [a, b] : edgeList) {
        edgeMap[a].push_back(b);
        edgeMap[b].push_back(a);
    }

    vector<vector<int>> children(n + 1); // maps a node to its children

    function<void(int, int)> buildTree = [&](int node, int parent) {
        for (int adj : edgeMap[node]) {
            if (adj == parent) continue;
            children[node].push_back(adj);
            buildTree(adj, node);
        }
    };
    buildTree(1, -1); // root at 1
    return children;
}

class RollbackLIS {
    // O(1)
    vector<int> _tails;
    vector<pair<int, int>> _history; // oldVal == -1 means append

public:
    // O(1)
    RollbackLIS() = default;

    // O(log n)
    void append(int value) {
        int idx = lower_bound(_tails.begin(), _tails.end(), value) - _tails.begin();
        if (idx == (int)_tails.size()) {
            _tails.push_back(value);
            _history.emplace_back(idx, -1);
        } else {
            int old = _tails[idx];
            _tails[idx] = value;
            _history.emplace_back(idx, old);
        }
    }

    // O(1)
    void pop() {
        auto [idx, old] = _history.back();
        _history.pop_back();
        if (old == -1) {
            _tails.pop_back();
        } else {
            _tails[idx] = old;
        }
    }

    // O(1)
    int lisLength() const {
        return (int)_tails.size();
    }
};

int n;
vector<int> vertexValues;
vector<vector<int>> children;
vector<int> answers;
RollbackLIS rollbacklis;

void dfs(int node) {
    int v = vertexValues[node];
    rollbacklis.append(v);
    answers[node] = rollbacklis.lisLength();
    for (int child : children[node]) dfs(child);
    rollbacklis.pop();
}

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    cin >> n;
    vertexValues.resize(n + 1);
    for (int i = 1; i <= n; ++i) cin >> vertexValues[i];

    vector<pair<int, int>> edges;
    edges.reserve(n - 1);
    for (int i = 0; i < n - 1; ++i) {
        int u, v;
        cin >> u >> v;
        edges.emplace_back(u, v);
    }

    children = edgeListToTree(edges, n);
    answers.assign(n + 1, 0);

    dfs(1);

    for (int i = 1; i <= n; ++i) cout << answers[i] << '\n';
    return 0;
}
