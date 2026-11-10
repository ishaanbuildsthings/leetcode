#include <bits/stdc++.h>
using namespace std;
using ll = long long;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n, k; cin >> n >> k;
    vector<int> A(n); for (int i = 0; i < n; i++) cin >> A[i];

    vector<int> slots(32, 0);
    for (int i = 0; i < n; i++) {
        int v = A[i];
        int curr = v;
        while (curr) {
            int msb = 31 - __builtin_clz(curr);
            if (slots[msb] == 0) {
                slots[msb] = curr;
                break;
            }
            curr = curr ^ slots[msb];
        }
    }

    // convert to full-basis
    for (int below = 0; below < 32; below++) {
        if (slots[below] == 0) continue;
        for (int above = below + 1; above < 32; above++) {
            if ((1 << below) & slots[above]) {
                slots[above] ^= slots[below];
            }
        }
    }

    int filled = 0;
    for (auto x : slots) {
        if (x) filled++;
    }
    ll useless = n - filled;
    ll options = useless > 35 ? k : pow(2LL, useless);

    vector<int> filledSlots;
    for (int i = 0; i < 32; i++) {
        if (slots[i]) {
            filledSlots.push_back(slots[i]);
        }
    }

    vector<int> xorOf = {0};
    
    int fmask = (1 << filled) - 1;
    for (int mask = 1; mask <= min(fmask, k); mask++) {
        int msb = 31 - __builtin_clz(mask);
        xorOf.push_back(filledSlots[msb] ^ xorOf[mask ^ (1 << msb)]);
    }


    vector<int> res;

    ll remain = options;
    int idx = 0;
    for (int kth = 0; kth < k; kth++) {
        res.push_back(xorOf[idx]);
        remain--;
        if (!remain) {
            remain = options;
            idx++;
        }
    }

    for (auto x : res) cout << x << " ";
}