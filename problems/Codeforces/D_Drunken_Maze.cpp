#include <bits/stdc++.h>
using namespace std;

struct State {
    int dist;
    int r;
    int c;
    string prev3;
};

struct Cmp {
    bool operator()(const State& a, const State& b) const {
        return a.dist > b.dist;
    }
};

string key3(int r, int c, const string& prev3) {
    return to_string(r) + ',' + to_string(c) + ':' + prev3;
}

string key4(const State& s) {
    return to_string(s.dist) + ',' + to_string(s.r) + ',' + to_string(s.c) + ':' + s.prev3;
}

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int h, w;
    if (!(cin >> h >> w)) return 0;

    vector<string> rows(h);
    for (int i = 0; i < h; ++i) cin >> rows[i];

    int sr = 0, sc = 0, tr = 0, tc = 0;
    for (int r = 0; r < h; ++r)
        for (int c = 0; c < w; ++c) {
            if (rows[r][c] == 'S') { sr = r; sc = c; }
            if (rows[r][c] == 'T') { tr = r; tc = c; }
        }

    priority_queue<State, vector<State>, Cmp> heap;
    State startTup{0, sr, sc, ""};
    heap.push(startTup);

    unordered_set<string> seen;
    seen.insert(key4(startTup));

    const array<pair<int, int>, 4> dirTups = { pair<int,int>{1,0}, {-1,0}, {0,1}, {0,-1} };

    while (!heap.empty()) {
        State cur = heap.top();
        heap.pop();

        if (seen.count(key3(cur.r, cur.c, cur.prev3))) continue;
        seen.insert(key3(cur.r, cur.c, cur.prev3));

        if (cur.r == tr && cur.c == tc) {
            cout << cur.dist << '\n';
            return 0;
        }

        for (int dirIdx = 0; dirIdx < 4; ++dirIdx) {
            auto dirTup = dirTups[dirIdx];
            int nr = cur.r + dirTup.first;
            int nc = cur.c + dirTup.second;
            if (nr < 0 || nr >= h || nc < 0 || nc >= w) continue;
            if (rows[nr][nc] == '#') continue;
            if (cur.prev3.size() == 3 && (cur.prev3.back() - '0') == dirIdx) continue;

            string new3;
            if (cur.prev3.empty()) new3 = string(1, '0' + dirIdx);
            else if ((cur.prev3.back() - '0') == dirIdx) new3 = cur.prev3 + char('0' + dirIdx);
            else new3 = string(1, '0' + dirIdx);

            State newState{cur.dist + 1, nr, nc, new3};
            heap.push(newState);
        }
    }

    cout << -1 << '\n';
    return 0;
}