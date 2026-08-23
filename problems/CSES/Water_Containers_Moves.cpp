#include <bits/stdc++.h>
using namespace std;
using ll = long long;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int A, B, X; cin >> A >> B >> X;
    if (X > A) {
        cout << -1 << '\n';
        return 0;
    }
    using Tup = tuple<ll, int, int>; // holds (min distance moved, currA water, currB water)
    priority_queue<Tup, vector<Tup>, greater<Tup>> heap;
    heap.push({0, 0, 0});
    ll INF = LLONG_MAX / 4;
    int S = (A + 1) * (B + 1);

    auto key = [&](int a, int b) -> int {
        return (a * (B + 1)) + b;
    };
    auto keyToState = [&](int key) -> pair<int,int> {
        int As = key / (B + 1);
        int Bs = key % (B + 1);
        return {As, Bs};
    };

    vector<ll> minD(S, INF);
    minD[key(0, 0)] = 0;
    vector<pair<int, string>> parents(S, pair<int, string>(-1, "")); // parents[sIdx] = (prevIdx, move)
    while (heap.size()) {
        auto [dist, currA, currB] = heap.top(); heap.pop();
        int idx = key(currA, currB);
        if (minD[idx] != dist) continue;

        vector<tuple<string, int, int, int>> moves; // will hold (moveType, newA, newB, adjCost)

        // empty
        tuple<string, int, int, int> emptyA = {"EMPTY A", 0, currB, currA};
        tuple<string, int, int, int> emptyB = {"EMPTY B", currA, 0, currB};
        // full
        tuple<string, int, int, int> fillA = {"FILL A", A, currB, A - currA};
        tuple<string, int, int, int> fillB = {"FILL B", currA, B, B - currB};
        // move
        int aMovedToB = min(currA, B - currB);
        tuple<string, int, int, int> moveAtoB = {"MOVE A B", currA - aMovedToB, currB + aMovedToB, aMovedToB};
        int bMovedToA = min(currB, A - currA);
        tuple<string, int, int, int> moveBtoA = {"MOVE B A", currA + bMovedToA, currB - bMovedToA, bMovedToA};

        moves.push_back(emptyA);
        moves.push_back(emptyB);
        moves.push_back(fillA);
        moves.push_back(fillB);
        moves.push_back(moveAtoB);
        moves.push_back(moveBtoA);

        for (auto [moveType, newA, newB, adjCost] : moves) {
            ll ndist = dist + adjCost;
            int adjState = key(newA, newB);
            if (ndist < minD[adjState]) {
                minD[adjState] = ndist;
                parents[adjState] = {idx, moveType};
                heap.push({ndist, newA, newB});
            }
        }
    }

    // find the best answer, b holds anything a holds exactly x
    ll bestDist = INF;
    int filledB = -1;
    for (int b = 0; b <= B; b++) {
        int idx = key(X, b);
        ll cost = minD[idx];
        if (cost < bestDist) {
            bestDist = cost;
            filledB = b;
        }
    }
    if (filledB == -1) {
        cout << -1 << '\n';
        return 0;
    }

    int currB = filledB;
    int currA = X;
    vector<string> path;
    while (parents[key(currA, currB)].first != -1) {
        auto [prevIdx, prevMove] = parents[key(currA, currB)];
        path.push_back(prevMove);
        auto [newA, newB] = keyToState(prevIdx);
        currA = newA;
        currB = newB;
    }
    reverse(path.begin(), path.end());
    cout << path.size() << " " << bestDist << '\n';
    for (auto mv : path) {
        cout << mv << '\n';
    }
}