// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/graphs/functionalGraph.oneIndexed.cpp
#include <bits/stdc++.h>
using namespace std;

// FunctionalGraph fg({{1, 2}, {2, 3}, {3, 4}, {4, 2}, {5, 3}, {6, 5}, {7, 1}, {8, 8}, {9, 8}});
//   edges {a, b} mean a -> b, in any order; the nodes are 1..edges.size(), each the start of exactly one edge (node 0 doesn't exist)
//
// fg.cycles()                      -> {{2, 3, 4}, {8}}
// fg.componentId(6)                -> 0
// fg.numEdgesToCrossBeforeCycle(6) -> 2
// fg.firstCycleNodeHit(6)          -> 3
// fg.kthNext(6, 4)                 -> 2    6 -> 5 -> 3 -> 4 -> 2
// fg.stepsFromTo(7, 4)             -> 4
// fg.stepsFromTo(5, 1)             -> -1   5 never passes through 1
// fg.components()[0].cycle         -> {2, 3, 4}
// fg.components()[0].tails         -> {{6, 5, 3}, {7, 1, 2}}
// fg.components()[1].cycle         -> {8}
// fg.components()[1].tails         -> {{9, 8}}
//
// Build: O(V) time and space, V = number of nodes. Invalid nodes or a negative k throw invalid_argument.

struct FunctionalGraph {
    struct Component {
        vector<int> cycle;
        vector<vector<int>> tails;
    };

    explicit FunctionalGraph(const vector<array<int, 2>>& edges) {
        int n = edges.size();
        size = n + 1;
        nxt.assign(size, -1);
        for (auto [a, b] : edges) {
            if (a < 1 || a >= size || b < 1 || b >= size)
                throw invalid_argument("FunctionalGraph: an edge is outside the nodes (one node per edge)");
            if (nxt[a] != -1) throw invalid_argument("FunctionalGraph: a node is the start of more than one edge");
            nxt[a] = b;
        }
        // n edges, each node the start of at most one: so every node starts exactly one

        // find the cycles: walk forward from each unseen node until the walk hits something seen
        vector<char> state(size, 0);  // 0 unseen, 1 on the current walk, 2 finished
        vector<vector<int>> found;
        vector<int> path;
        for (int start = 1; start < size; start++) {
            if (state[start]) continue;
            path.clear();
            int node = start;
            while (state[node] == 0) {
                state[node] = 1;
                path.push_back(node);
                node = nxt[node];
            }
            if (state[node] == 1)  // the walk ran into itself: from there on it's a new cycle
                found.emplace_back(find(path.begin(), path.end(), node), path.end());
            for (int x : path) state[x] = 2;
        }
        for (auto& cyc : found) rotate(cyc.begin(), min_element(cyc.begin(), cyc.end()), cyc.end());  // smallest first
        sort(found.begin(), found.end());
        cycleList = found;

        comp.assign(size, -1);
        depth.assign(size, 0);  // edges to cross before being on a cycle
        first.assign(size, -1);  // first cycle node hit
        pos.assign(size, -1);  // index within its cycle, for cycle nodes
        vector<char> onCycle(size, 0);
        for (int cid = 0; cid < (int)cycleList.size(); cid++)
            for (int i = 0; i < (int)cycleList[cid].size(); i++) {
                int node = cycleList[cid][i];
                onCycle[node] = 1;
                comp[node] = cid;
                first[node] = node;
                pos[node] = i;
            }

        // the tails form trees hanging off cycle nodes: walk them backward, recording depth-first entry / exit times
        vector<int> childStart(size + 1, 0), childList;
        for (int a = 1; a < size; a++)
            if (!onCycle[a]) childStart[nxt[a] + 1]++;
        for (int i = 0; i < size; i++) childStart[i + 1] += childStart[i];
        childList.resize(childStart[size]);
        {
            vector<int> fill(childStart.begin(), childStart.end() - 1);
            for (int a = 1; a < size; a++)
                if (!onCycle[a]) childList[fill[nxt[a]]++] = a;
        }
        tin.assign(size, 0);
        tout.assign(size, 0);
        int timer = 0;
        vector<int> stack;
        for (int cid = 0; cid < (int)cycleList.size(); cid++)
            for (int root : cycleList[cid]) {
                stack.push_back(root);
                while (!stack.empty()) {
                    int node = stack.back();
                    stack.pop_back();
                    if (node >= 0) {
                        tin[node] = timer++;
                        int d = depth[node];
                        if (d == (int)byDepthTins.size()) {
                            byDepthTins.emplace_back();
                            byDepthNodes.emplace_back();
                        }
                        byDepthTins[d].push_back(tin[node]);
                        byDepthNodes[d].push_back(node);
                        stack.push_back(~node);
                        for (int i = childStart[node]; i < childStart[node + 1]; i++) {
                            int child = childList[i];
                            depth[child] = d + 1;
                            first[child] = first[node];
                            comp[child] = cid;
                            stack.push_back(child);
                        }
                    } else {
                        tout[~node] = timer - 1;
                    }
                }
            }

        // components: each tail walk starts at a node nothing points to and stops at the first node already listed
        vector<char> hasIncoming(size, 0);
        for (int a = 1; a < size; a++) hasIncoming[nxt[a]] = 1;
        vector<char> listed = onCycle;
        componentList.resize(cycleList.size());
        for (int cid = 0; cid < (int)cycleList.size(); cid++) componentList[cid].cycle = cycleList[cid];
        for (int start = 1; start < size; start++) {
            if (hasIncoming[start]) continue;
            vector<int> walk = {start};
            listed[start] = 1;
            int node = nxt[start];
            while (!listed[node]) {
                walk.push_back(node);
                listed[node] = 1;
                node = nxt[node];
            }
            walk.push_back(node);
            componentList[comp[start]].tails.push_back(move(walk));
        }
    }

    // O(1), every cycle as a list of only the nodes on it (no tails), in walking order: {1, 2, 3} is 1 -> 2 -> 3 -> 1.
    // Each starts at its smallest node; the cycles are sorted by that node. Its index here is its componentId
    const vector<vector<int>>& cycles() const { return cycleList; }

    // O(1), which component node is in, for ANY node (on a cycle or not): an index into cycles(), 0..cycles().size() - 1
    int componentId(int node) const { check(node); return comp[node]; }

    // O(1), how many edges node crosses before being part of a cycle; 0 if node is on a cycle
    int numEdgesToCrossBeforeCycle(int node) const { check(node); return depth[node]; }

    // O(1), the first cycle node node's walk reaches; a node on a cycle is its own
    int firstCycleNodeHit(int node) const { check(node); return first[node]; }

    // O(1) if k reaches the cycle, else O(log V): where node is after k steps (k >= 0, any size). kthNext(node, 0) = node
    int kthNext(int node, long long k) const {
        check(node);
        if (k < 0) throw invalid_argument("FunctionalGraph: kthNext needs k >= 0");
        int d = depth[node];
        if (k >= d) {
            const vector<int>& cyc = cycleList[comp[node]];
            return cyc[(pos[first[node]] + (k - d) % (long long)cyc.size()) % cyc.size()];
        }
        // still on the tail: the node k steps ahead is the one at depth d - k whose subtree contains node, which is the
        // last node at that depth entered before node
        int target = d - k;
        const vector<int>& tins = byDepthTins[target];
        int i = upper_bound(tins.begin(), tins.end(), tin[node]) - tins.begin() - 1;
        return byDepthNodes[target][i];
    }

    // O(1), how many steps it takes to get from a to b (0 if a == b), or -1 if a never reaches b
    long long stepsFromTo(int a, int b) const {
        check(a);
        check(b);
        if (comp[a] != comp[b]) return -1;
        if (depth[b] == 0) {  // b is on the cycle: reach the cycle, then go around to b
            int cycLen = cycleList[comp[b]].size();
            return depth[a] + ((pos[b] - pos[first[a]]) % cycLen + cycLen) % cycLen;
        }
        if (tin[b] <= tin[a] && tin[a] <= tout[b]) return depth[a] - depth[b];  // b is on a tail: a has to come down through b
        return -1;
    }

    // O(1) (built in O(V)), every component in componentId order:
    //   .cycle = cycles()[componentId]
    //   .tails = one walk per node with no incoming edges (increasing), following edges and stopping at the first node
    //            already listed (a cycle node, or a node of an earlier walk where the tails merge), which is included.
    //            Every node appears in the component once, plus each walk's last node. Total size O(V)
    const vector<Component>& components() const { return componentList; }

private:
    int size;
    vector<int> nxt, comp, depth, first, pos, tin, tout;
    vector<vector<int>> cycleList, byDepthTins, byDepthNodes;
    vector<Component> componentList;

    void check(int node) const {
        if (node < 1 || node >= size) throw invalid_argument("FunctionalGraph: node outside the nodes");
    }
};
