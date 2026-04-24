#include <bits/stdc++.h>
using namespace std;

// #define LOCAL

#ifdef LOCAL
#define dbg(x) cerr << #x << " = " << (x) << endl
#define dbgv(v) do { cerr << #v << " = ["; for (auto& _x : v) cerr << _x << ", "; cerr << "]\n"; } while(0)
#define dbg2d(v) do { cerr << #v << ":\n"; for (auto& _r : v) { cerr << "  ["; for (auto& _x : _r) cerr << _x << ", "; cerr << "]\n"; } } while(0)
#else
#define dbg(x)
#define dbgv(v)
#define dbg2d(v)
#endif

void solve() {
    int n, numAnimal, L; cin >> n >> numAnimal >> L;
    vector<int> times(n); for (int i = 0; i < n; i++) cin >> times[i];
    set<int> timeSet(times.begin(), times.end());

    // if we have animals <= flashlights we're basically going to just keep cycling
    int amt = min(numAnimal, n + 1);

    int flashlightsUsed = 0;

    vector<int> animals(amt); // I am adversaral, trying to increment only n+1 animals, you will flash N of them
    for (int second = 1; second <= L; second++) {

        

        // adversary increments the minimum value
        int idx = min_element(animals.begin(), animals.end()) - animals.begin();
        animals[idx]++;

        dbgv(animals);

        if (timeSet.count(second) == 0) continue;

        flashlightsUsed++;
        int flashlightsRemain = n - flashlightsUsed;

        // we shine a flashlight at the biggest one
        idx = max_element(animals.begin(), animals.end()) - animals.begin();
        animals[idx] = 0;

        // if you have X flashlights, I maintain X+1 people I increment
        if (animals.size() > flashlightsRemain + 1) {
            animals.erase(animals.begin() + idx);
        }
    }

    int idx = max_element(animals.begin(), animals.end()) - animals.begin();
    cout << animals[idx] << endl;
}

int main() {
    int t; cin >> t;
    while (t--) {
        solve();
    }
}