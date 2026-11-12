#include <bits/stdc++.h>
using namespace std;
using ll = long long;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    string s; cin >> s;
    int n = s.size();
    set<int> alive; // holds all letters with frequency left

    set<pair<int,int>> countAndLetterNum; // holds [(count, letterNum), ...]
    vector<int> letterNumToFrq(26, 0);
    for (auto x : s) {
        letterNumToFrq[x - 'A']++;
        alive.insert(x - 'A');
    }
    for (int i = 0; i < 26; i++) {
        countAndLetterNum.insert({letterNumToFrq[i], i});
    }
    
    vector<int> res;
    for (int i = 0; i < n; i++) {
        
        vector<int> cands;
        int smallest = *alive.begin();
        cands.push_back(smallest);
        if (alive.size() > 1) {
            int smallest2 = *next(alive.begin());
            cands.push_back(smallest2);
        }
        auto [maxFrq, maxFrqLetter] = *countAndLetterNum.rbegin();
        cands.push_back(maxFrqLetter);

        for (auto cand : cands) {
            // cannot match previous
            if (res.size() && res.back() == cand) {
                continue;
            }

            int remainSlots = n - i - 1;
            // if we place this letter here, we only get ceil((remainSlots-1) / 2) other possible slots to put it in
            int newFrq = letterNumToFrq[cand] - 1;
            if (newFrq > ((remainSlots)/2)) {
                continue;
            }

            // also all OTHER letters get ceil(remainSlots/2) slots left, we just check the max
            auto it = countAndLetterNum.rbegin();
            auto [mx, mxLetter] = *it;
            if (mxLetter == cand) {
                it++;
                if (it != countAndLetterNum.rend()) {
                    tie(mx, mxLetter) = *it;
                } else {
                    mx = -1;
                }
            }
            if (mx > (remainSlots + 1) / 2) {
                continue;
            }

            res.push_back(cand);
            countAndLetterNum.erase({letterNumToFrq[cand], cand});
            if (letterNumToFrq[cand] > 1) {
                countAndLetterNum.insert({letterNumToFrq[cand] - 1, cand});
            }
            letterNumToFrq[cand]--;
            if (letterNumToFrq[cand] == 0) {
                alive.erase(cand);
            }
            break;
        }
        if ((int)res.size() != i + 1) {
            cout << -1;
            return 0;
        }
    }
    for (auto x : res) cout << char('A' + x);
}