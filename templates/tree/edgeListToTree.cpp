// TEMPLATE BY ISHAAN AGRAWAL, github: ishaanbuildsthings

// edgeList = {{a, b}, {c, d}, ...}
// if zeroIndex is true, assumes the root is 0, returns a vector `children` that goes up to `children[n-1]` (n-1 is inferred from the edgeList)
// if zeroIndex is false, assumes the root is 1, returns a vector `children` that goes up to `children[n]`, children[0] is empty and unused
vector<vector<int>> edgeListToTree(const vector<pair<int, int>>& edgeList, bool zeroIndexed = true) {
    int n = (int)edgeList.size() + 1;
    int size = zeroIndexed ? n : n + 1;
    int root = zeroIndexed ? 0 : 1;
    vector<vector<int>> edgeMap(size);
    for (auto& [a, b] : edgeList) {
        edgeMap[a].push_back(b);
        edgeMap[b].push_back(a);
    }
    vector<vector<int>> children(size);
    vector<int> parent(size, -1);
    vector<int> stk = {root};
    while (!stk.empty()) {
        int node = stk.back();
        stk.pop_back();
        for (int adj : edgeMap[node]) {
            if (adj == parent[node]) continue;
            parent[adj] = node;
            children[node].push_back(adj);
            stk.push_back(adj);
        }
    }
    return children;
}