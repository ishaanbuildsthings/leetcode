#include <bits/stdc++.h>
using namespace std;

int main() {
    cin.tie(nullptr);
    ios::sync_with_stdio(false);
    priority_queue<long long, vector<long long>, greater<long long>> minHeap;
    int sz, n; cin >> sz >> n;
    for (int i = 0; i < n; i++) {
        int x; cin >> x;
        minHeap.push(x);
    }
    long long out = 0;
    while (minHeap.size() > 1) {
        int s1 = minHeap.top(); minHeap.pop();
        int s2 = minHeap.top(); minHeap.pop();
        out += s1 + s2;
        minHeap.push(s1 + s2);
    }
    cout << out;
}