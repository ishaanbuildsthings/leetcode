#include <bits/stdc++.h>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n; cin >> n;
    vector<int> A(n); for (int i = 0; i < n; i++) cin >> A[i];

    long long out = 0;
    // for each number it will contribute left and right, right can allow duplicates
    
    // for each number, find its first occurence on the left
    unordered_map<int, int> last; // number -> current rightmost position as we scan

    vector<int> firstOnLeft(n, -1); // index of a number to the first occurence of that same number on the left
    for (int i = 0; i < n; i++) {
        int num = A[i];
        auto it = last.find(num);
        firstOnLeft[i] = (it == last.end() ? -1 : it->second);
        last[num] = i;
    }

    for (int i = 0; i < n; i++) {
        long long rightEdges = n - i;
        long long leftEdges = i - (firstOnLeft[i]);
        out += leftEdges * rightEdges;
    }

    cout << out;

}