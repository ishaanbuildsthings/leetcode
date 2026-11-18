// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/geometry/polygonArea.cpp
#include <bits/stdc++.h>
using namespace std;
using ll = long long;

// Twice the signed area of a polygon (shoelace formula), as an exact integer for integer corners: the area is
// abs(result) / 2, and the sign is the direction, > 0 counterclockwise, < 0 clockwise, 0 for no area (e.g. all
// corners on one line). Doubling keeps it exact: integer corners always give a whole number or a whole and a half.
// points: the corners in order around the boundary (either direction, not shuffled), as (x, y) pairs; the last corner
// joins back to the first. Fewer than 3 corners give 0. Coordinates up to about 10^9 fit (each term is up to 2e18).
// polygonArea2({{0, 0}, {4, 0}, {4, 3}}) -> 12 (area 6, counterclockwise)
// O(n)
ll polygonArea2(const vector<pair<ll, ll>>& points) {
    int n = points.size();
    ll total = 0;
    for (int i = 0; i < n; i++) {
        auto [x1, y1] = points[i];
        auto [x2, y2] = points[i + 1 == n ? 0 : i + 1];  // (the last corner joins back to the first)
        total += x1 * y2 - x2 * y1;
    }
    return total;
}
