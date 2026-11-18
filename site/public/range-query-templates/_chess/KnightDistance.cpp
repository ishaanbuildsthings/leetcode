// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/chess/KnightDistance.cpp
#include <bits/stdc++.h>
using namespace std;
using ll = long long;

// O(1) min # of moves to go from one position to another on an infinite chess board
ll knightDistanceFullyInfiniteChessboard(ll x1, ll y1, ll x2, ll y2) {
    ll x = llabs(x2 - x1), y = llabs(y2 - y1);
    if (x < y) swap(x, y);

    if (x == 1 && y == 0)
        return 3;
    if (x == 2 && y == 2)
        return 4;

    ll moves = max((x + 1) / 2, (x + y + 2) / 3);

    if (moves % 2 != (x + y) % 2)
        moves += 1;

    return moves;
}

// O(1)
// CORNER IS BOUNDED, so one quarter of the graph is infinite
// corner is (0, 0)
// X and Y MUST be >= 0
ll knightDistanceFromCorner(ll x, ll y) {
    if (x == 1 && y == 1)
        return 4;
    return knightDistanceFullyInfiniteChessboard(0, 0, x, y);
}
