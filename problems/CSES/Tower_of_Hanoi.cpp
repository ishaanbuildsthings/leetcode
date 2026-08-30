#include <bits/stdc++.h>
using namespace std;
using ll = long long;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n; cin >> n;

    struct Move {
        int a, b;
    };

    auto move =[&](auto&& self, int size, int fromI, int toI) -> vector<Move> {
        if (size == 1) {
            return {{fromI, toI}};
        }
        int other = 6 - fromI - toI;
        vector<Move> moves = self(self, size - 1, fromI, other);
        moves.push_back({fromI, toI});
        vector<Move> moves2 = self(self, size - 1, other, toI);
        for (auto move : moves2) {
            moves.push_back(move);
        }
        return moves;
    };

    
    auto answer = move(move, n, 1, 3);
    cout << answer.size() << '\n';
    for (auto x : answer) {
        cout << x.a << " " << x.b << '\n';
    }
}