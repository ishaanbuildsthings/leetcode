#include<bits/stdc++.h>
using namespace std;

int INF = INT_MAX;

struct StackMin {
    vector<pair<int,int>> stack; // holds (number, min)

    bool empty() { return stack.size() == 0; }
    void push(int x) {
        if (empty()) {
            stack.push_back({x, x});
        } else {
            int newMin = min(stack.back().second, x);
            stack.push_back({x, newMin});
        }
    }
    int pop() {
        int v = stack.back().first;
        stack.pop_back();
        return v;
    }
    int size() {
        return stack.size();
    }
    int agg() {
        return empty() ? INF : stack.back().second;
    }
};

struct QueueMin {
    StackMin in, out;
    bool empty() {
        return in.empty() && out.empty();
    }
    int size() {
        return in.size() + out.size();
    }
    void push(int x) {
        in.push(x);
    }
    void _pour() {
        if (out.empty()) {
            while (!in.empty()) {
                out.push(in.pop());
            }
        }
    }
    int pop() {
        if (out.empty()) {
            _pour();
        }
        return out.pop();
    }
    int agg() {
        return min(in.agg(), out.agg());
    }
};

int main() {
    cin.tie(nullptr);
    ios::sync_with_stdio(false);
    int n, k;
    cin >> n >> k;
    long long x, a, b, c;
    cin >> x >> a >> b >> c;
    QueueMin q;
    int result = 0;
    int currX = x;
    for (int i = 0; i < n; i++) {
        int newX = i == 0 ? x : (a * currX + b) % c;
        q.push(newX);
        currX = newX;
        if (q.size() > k) q.pop();
        if (q.size() == k) {
            result ^= q.agg();
        }
    }
    cout << result << "\n";
}