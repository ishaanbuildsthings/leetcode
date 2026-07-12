// DSU<string> dsu(vals);
// takes an array of values (can be array of strings, pairs, etc) since everything operates on indices

template <typename T>
struct RollbackDSU {
    vector<T> vals;
    vector<int> par, sz;
    int comps, mx;
    // i < 0 marks a unite that found i and j already together, so it changed nothing
    vector<array<int, 3>> stk;

    // O(n), every element starts in its own component
    RollbackDSU(const vector<T>& vals) : vals(vals) {
        int n = vals.size();
        par.resize(n);
        iota(par.begin(), par.end(), 0);
        sz.assign(n, 1);
        comps = n;
        mx = n ? 1 : 0;
    }

    // O(log n), no path compression, so depth is bounded by union by size alone
    int find(int i) {
        while (par[i] != i) i = par[i];
        return i;
    }

    // O(log n), merges the two components, false if i and j were already together
    // either way it records a frame, so it always takes exactly one rollback to undo
    bool unite(int i, int j) {
        i = find(i), j = find(j);
        if (i == j) {
            stk.push_back({-1, -1, mx});
            return false;
        }
        if (sz[i] < sz[j]) swap(i, j);
        stk.push_back({i, j, mx});
        par[j] = i;
        sz[i] += sz[j];
        comps--;
        mx = max(mx, sz[i]);
        return true;
    }

    // O(1), undoes the single most recent unite, whether or not that unite merged anything
    // a unite that returned false changed nothing, so its rollback changes nothing, but it
    // still counts: k rollbacks always undo the last k unites
    void rollback() {
        auto [i, j, oldMx] = stk.back();
        stk.pop_back();
        if (i < 0) return;
        par[j] = j;
        sz[i] -= sz[j];
        comps++;
        mx = oldMx;
    }

    // O(log n), true if i and j are in the same component
    bool areUnioned(int i, int j) {
        return find(i) == find(j);
    }

    // O(log n), how many elements are in i's component
    int size(int i) {
        return sz[find(i)];
    }

    // O(1), how many components exist right now
    int numComponents() {
        return comps;
    }

    // O(1), size of the biggest component, maintained in unite
    int largestSize() {
        return mx;
    }

    // O(n), one index per component: the representative each member's find returns
    vector<int> roots() {
        vector<int> res;
        for (int i = 0; i < (int)par.size(); i++)
            if (par[i] == i) res.push_back(i);
        return res;
    }

    // O(n log n), the sizes of all components, biggest first, e.g. [4, 2, 1]
    vector<int> sizes() {
        vector<int> res;
        for (int i = 0; i < (int)par.size(); i++)
            if (par[i] == i) res.push_back(sz[i]);
        sort(res.rbegin(), res.rend());
        return res;
    }

    // O(n log n), groupsArr[rt] = list of values whose root is rt, empty if rt is not a root
    vector<vector<T>> groups() {
        int n = par.size();
        vector<vector<T>> groupsArr(n);
        for (int i = 0; i < n; i++) groupsArr[find(i)].push_back(vals[i]);
        return groupsArr;
    }

    // O(n log n), the values of every element sitting in the same group as index i
    vector<T> elementsInGroup(int i) {
        int rt = find(i);
        vector<T> res;
        for (int j = 0; j < (int)par.size(); j++)
            if (find(j) == rt) res.push_back(vals[j]);
        return res;
    }
};