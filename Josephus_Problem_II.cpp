#include <bits/stdc++.h>
#include <ext/pb_ds/assoc_container.hpp>
#include <ext/pb_ds/tree_policy.hpp>

using namespace std;
using namespace __gnu_pbds;

template<class T>
using orderedSet = tree<T, null_type, less<T>, rb_tree_tag, tree_order_statistics_node_update>;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int n, k; cin >> n >> k;
    // holds living indices, 1-indexed
    orderedSet<int> os;
    for (int i = 1; i <= n; i++) os.insert(i);

    int pos = 0; // current index we are at
    bool first = true;

    while (!os.empty()) {
        pos = (pos + k) % (long long)os.size(); // we have to remove the person at this index next
        auto it = os.find_by_order((int)pos);
        if (!first) cout << ' ';
        first = false;
        cout << *it;
        os.erase(it);
    }
}

// 0 1 2 3 4 5 6 7, k=2
//     ^
// 0 1 3 4 5 6 7
//         ^ now remove this, which is actually just our old index 2, plus k