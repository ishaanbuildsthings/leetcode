// Takes an array of vals (can be strings, tuples, etc) since it operates based on indices
// DSU<int> dsu(vals);
template <typename T>
struct DSU {
    vector<T> vals;
    vector<int> par, sz;
    int comps, mx;

    // O(n), every element starts in its own component
    DSU(const vector<T>& vals) : vals(vals), par(vals.size()), sz(vals.size(), 1),
                                 comps(vals.size()), mx(vals.empty() ? 0 : 1) {
        iota(par.begin(), par.end(), 0);
    }

    // O(1), index of the representative of i's component
    int find(int i) {
        while (par[i] != i) {
            par[i] = par[par[i]];
            i = par[i];
        }
        return i;
    }

    // O(1), merges the two components, false if i and j were already together
    bool unite(int i, int j) {
        i = find(i), j = find(j);
        if (i == j) return false;
        if (sz[i] < sz[j]) swap(i, j);
        par[j] = i;
        sz[i] += sz[j];
        comps--;
        mx = max(mx, sz[i]);
        return true;
    }

    // O(1), true if i and j are in the same component
    bool areUnioned(int i, int j) { return find(i) == find(j); }

    // O(1), how many elements are in i's component
    int size(int i) { return sz[find(i)]; }

    // O(1), how many components exist right now
    int numComponents() { return comps; }

    // O(1), size of the biggest component, maintained in unite
    int largestSize() { return mx; }

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

    // O(n), groupsArr[rt] = values whose root is rt, empty if rt is not a root
    vector<vector<T>> groups() {
        int n = par.size();
        vector<vector<T>> groupsArr(n);
        for (int i = 0; i < n; i++) groupsArr[find(i)].push_back(vals[i]);
        return groupsArr;
    }

    // O(n), the values of every element sitting in the same group as index i
    vector<T> elementsInGroup(int i) {
        int rt = find(i);
        vector<T> res;
        for (int j = 0; j < (int)par.size(); j++)
            if (find(j) == rt) res.push_back(vals[j]);
        return res;
    }
};