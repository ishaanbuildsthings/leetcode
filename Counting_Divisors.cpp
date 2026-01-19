#include<bits/stdc++.h>
using namespace std;

int main() {
    cin.tie(nullptr);
    ios::sync_with_stdio(false);
    int n; cin >> n;
    int MAX_X = 1000000;
    vector<int> divs(MAX_X + 1);
    for (int number = 1; number <= MAX_X; number++) {
        int curr = number;
        while (curr <= MAX_X) {
            divs[curr]++;
            curr += number;
        }
    }
    for (int i = 0; i < n; i++) {
        int x; cin >> x;
        cout << divs[x] << endl;
    }
}