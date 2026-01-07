// True O(n) solution using 2 agg stacks
#include <bits/stdc++.h>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    const int BITS = 32;

    int n, k;
    cin >> n >> k;

    uint64_t x, a, b, c;
    cin >> x >> a >> b >> c;

    uint32_t currX = (uint32_t)x;

    static int frq[BITS];
    uint32_t curOr = 0;
    uint32_t out = 0;

    vector<uint32_t> ring(k); // no -1 init
    int i = 0;

    auto addVal = [&](uint32_t v) {
        while (v) {
            int bit = __builtin_ctz(v);
            if (++frq[bit] == 1) curOr |= (1u << bit);
            v &= v - 1;
        }
    };

    auto removeVal = [&](uint32_t v) {
        while (v) {
            int bit = __builtin_ctz(v);
            if (--frq[bit] == 0) curOr &= ~(1u << bit);
            v &= v - 1;
        }
    };

    for (int r = 0; r < n; r++) {
        if (r) currX = (uint32_t)((a * (uint64_t)currX + b) % c);

        if (r >= k) removeVal(ring[i]); // remove before overwrite

        ring[i] = currX;
        addVal(currX);

        if (++i == k) i = 0;

        if (r + 1 >= k) out ^= curOr;
    }

    cout << out << "\n";
}

#include<bits/stdc++.h>
using namespace std;
using ll = long long;

struct AggStackOr {
    vector<pair<int, int>> stack; // will hold (number, currentBitwiseOr)

    bool empty() {
        return stack.empty();
    }

    void push(int x) {
        if (empty()) {
            stack.push_back({x, x});
        } else {
            stack.push_back({x, stack.back().second | x});
        }
    }

    int pop() {
        int v = stack.back().first;
        stack.pop_back();
        return v;
    }

    int agg() {
        return empty() ? 0 : stack.back().second; // identity value
    }

    int size() {
        return stack.size();
    }
};

struct AggQueueOr {
    AggStackOr in, out;
    
    int agg() {
        return out.agg() | in.agg();
    }

    void push(int x) {
        in.push(x);
    }

    // refill the out queue (only if empty)
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

    int size() {
        return out.size() + in.size();
    }
};

int main() {
    int n, k;
    cin >> n >> k;
    AggQueueOr q;
    ll x, a, b, c;
    cin >> x >> a >> b >> c;
    int currX = x;
    int res = 0;
    for (int r = 0; r < n; r++) {
        ll newX = r == 0 ? x : (a * currX + b) % c;
        currX = newX;
        q.push(newX);
        if (q.size() > k) {
            q.pop();
        }

        if (r + 1 >= k) {
            res ^= q.agg();
        }

    }
    cout << res;
    cout << "\n";
}

// O(n * BITS) solution, hyperoptimized with ring buffer and iterating only on set bits, not all 32 each loop, still TLE

// #include<bits/stdc++.h>
// using namespace std;
// using ll = long long;

// int BITS = 32;
// int main() {
//     ios::sync_with_stdio(false);
//     cin.tie(nullptr);

//     int n, k;
//     cin >> n >> k;
//     int x;
//     ll a, b, c;
//     cin >> x >> a >> b >> c;

//     int currX = x;
//     vector<int> frq(BITS);
//     ll out = 0;
//     ll curOr = 0;

//     vector<int> ring(k, -1);
//     int i = 0; // ring insertion pointer
//     for (int r = 0; r < n; r++) {
//         if (r != 0) currX = (a * currX + b) % c;
//         int lost = ring[i];
//         ring[i] = currX;
//         i++;
//         if (i == k) {
//             i = 0;
//         }

//         // iterate over set bits only (instead of all 32 spots) to update frequency
//         int currX2 = currX;
//         while (currX2) {
//             int lsb = __builtin_ctz(currX2);
//             if (++frq[lsb] == 1) curOr |= (1 << lsb);
//             currX2 &= currX2 - 1;
//         }

//         if (r >= k) {
//             while (lost) {
//                 int lsb = __builtin_ctz(lost);
//                 if (--frq[lsb] == 0) curOr ^= (1 << lsb);
//                 lost &= lost - 1;
//             }
//         }

//         if (r + 1 >= k) {
//             out ^= curOr;
//         }
//     }

//     cout << out << "\n";
// }