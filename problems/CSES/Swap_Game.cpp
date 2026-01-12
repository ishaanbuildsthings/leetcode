#include <bits/stdc++.h>
using namespace std;


int main() {
    cin.tie(nullptr);
    ios::sync_with_stdio(false);
    int initState = 0;
    int power = 8;
    for (int i = 0; i < 3; i++) {
        int a, b, c; cin >> a >> b >> c;
        initState +=  a * pow(10, power);
        power--;
        initState += b * pow(10, power);
        power--;
        initState += c * pow(10, power);
        power--;
    }

    vector<pair<int,int>> adjs = {{0,1},{1,2},{3,4},{4,5},{6,7},{7,8},{0,3},{1,4},{2,5},{3,6},{4,7},{5,8}};
    vector<int> pow10;
    for (int power = 0; power <= 8; power++) {
        pow10.push_back(pow(10, power));
    }

    int FINAL = 123456789;
    if (initState == FINAL) {
        cout << 0;
        return 0;
    }

    deque<int> q;
    q.push_back(initState);
    unordered_set<int> seen;
    seen.reserve(500000);
    seen.insert(initState);
    int steps = 0;
    while (q.size() > 0) {
        int length = q.size();
        for (int i = 0; i < length; i++) {
            int state = q.front(); q.pop_front();
            for (auto adjPair : adjs) {
                int adjState = state;
                // subtract the higher power
                int digit1 = (state / pow10[9 - adjPair.first - 1]) % 10;
                int digit2 = (state / pow10[9 - adjPair.second - 1]) % 10;
                adjState -= digit1 * pow10[9 - adjPair.first - 1];
                adjState += digit2 * pow10[9 - adjPair.first - 1];
                adjState -= digit2 * pow10[9 - adjPair.second - 1];
                adjState += digit1 * pow10[9 - adjPair.second - 1];
                if (adjState == FINAL) {
                    cout << steps + 1;
                    return 0;
                }
                if (seen.find(adjState) != seen.end()) {
                    continue;
                }
                seen.insert(adjState);
                q.push_back(adjState);
            }
        }
        steps++;
    }

}
// Python BFS (TLE)
// # from collections import deque

// # board = []
// # for _ in range(3):
// #     arr = list(map(int, input().split()))
// #     board.append(arr)

// # num = 0
// # power = 8
// # for r in range(3):
// #     for c in range(3):
// #         num += board[r][c] * 10**power
// #         power -= 1

// # q = deque([num])
// # seen = {num}

// # FINAL = 123456789

// # steps = 0

// # swaps = [[0, 1], [1, 2], [3, 4], [4, 5], [6, 7], [7, 8], [0, 3], [1, 4], [2, 5], [3, 6], [4, 7], [5, 8]]

// # def getAdjs(state):
// #     s = str(state)
// #     adjs = []
// #     for i, j in swaps:
// #         left = s[:i]
// #         middle = s[i+1:j]
// #         right = s[j+1:]
// #         adjs.append(left + s[j] + middle + s[i] + right)
// #     return adjs


// # while q:
// #     length = len(q)
// #     for _ in range(length):
// #         state = q.popleft()
// #         if state == FINAL:
// #             print(steps)
// #             exit()
// #         for adj in getAdjs(state):
// #             if adj in seen:
// #                 continue
// #             seen.add(adj)
// #             q.append(adj)
// #     steps += 1