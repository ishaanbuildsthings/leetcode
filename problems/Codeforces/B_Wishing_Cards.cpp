// O(k^3) push dp, had to use C++ to pass, but see O(k^3) push DP in python for notes
#include <bits/stdc++.h>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int T;
    cin >> T;
    while (T--) {
        int n, k;
        cin >> n >> k;
        vector<int> A(n);
        for (int i = 0; i < n; i++) cin >> A[i];

        vector<pair<int,int>> people;
        int mx = 0;
        for (int i = 0; i < n; i++) {
            int v = A[i];
            if (v > mx) {
                mx = v;
                people.push_back({v, i}); // holds (maxStorage, originalIndex)
            }
        }

        if (people.empty()) {
            cout << 0 << "\n";
            continue;
        }

        vector<int> segLen;
        for (int i = 0; i + 1 < (int)people.size(); i++) {
            segLen.push_back(people[i + 1].second - people[i].second);
        }
        segLen.push_back(n - people.back().second);

        auto make = [&]() {
            vector<vector<double>> dp(k + 1, vector<double>(k + 1, -numeric_limits<double>::infinity()));
            dp[k][0] = 0; // dp[budgetLeft][currMax] is the answer as we loop over each item and the choices we make at that item
            return dp;
        };

        auto dp = make();

        // Pull DP
        // Loop over new states (k^2)
        // Loop over incoming DP edges (predecessors) of this state
        for (int i = 0; i < (int)people.size(); i++) {
            int maxStorage = people[i].first;
            int originalIndex = people[i].second;

            auto ndp = make(); // cloning the old dp here would be a trap, as evne if we do nothing as this new element, we still get to walk forward steps and gain happiness

            // we are going to need the best dp[fixedBudget][upToThisMax], so compute a prefix
            auto pref = make();
            for (int budget = 0; budget <= k; budget++) {
                double maxScore = 0;
                for (int currMax = 0; currMax <= k; currMax++) {
                    maxScore = max(maxScore, dp[budget][currMax]);
                    pref[budget][currMax] = maxScore;
                }
            }

            // looping over new states
            for (int newBudgetLeft = 0; newBudgetLeft <= k; newBudgetLeft++) {
                for (int newCurrMax = 0; newCurrMax <= maxStorage; newCurrMax++) {

                    // to reach this state after this item, we could have been at this state already before this item, and done nothing with this item
                    // doing nothing with this person would still gain us score for the walk to the next length
                    ndp[newBudgetLeft][newCurrMax] = max(ndp[newBudgetLeft][newCurrMax], dp[newBudgetLeft][newCurrMax] + (1LL * segLen[i] * newCurrMax)); // TODO: is max needed

                    // or, we could have come from any old current max state, we just now spent money to reach the new current max and smaller budget
                    int budgetBeforeSpendingHere = newBudgetLeft + newCurrMax;
                    if (budgetBeforeSpendingHere > k) {
                        continue;
                    }
                    ndp[newBudgetLeft][newCurrMax] = max(ndp[newBudgetLeft][newCurrMax], 1LL * segLen[i] * newCurrMax + pref[budgetBeforeSpendingHere][newCurrMax]);
                    // for oldCurrentMax in range(newCurrMax):
                    //     ndp[newBudgetLeft][newCurrMax] = max(ndp[newBudgetLeft][newCurrMax], dp[budgetBeforeSpendingHere][oldCurrentMax] + (segLen[i] * newCurrMax))
                }
            }

            dp = std::move(ndp);
        }

        double res = 0;
        for (auto &row : dp) {
            for (auto &c : row) {
                res = max(res, c);
            }
        }
        long long ans = (long long)res;
        cout << ans << "\n";
    }

    return 0;
}

// # O(k^3) push DP (TLE from constant factor)
// fmax = lambda x, y: x if x > y else y
// T = int(input())
// for _ in range(T):
//     n, k = map(int, input().split())
//     A = list(map(int, input().split()))

//     people = []
//     mx = 0
//     for i, v in enumerate(A):
//         if v > mx:
//             mx = v
//             people.append((v, i)) # holds (maxStorage, originalIndex)

//     if not people:
//         print(0)
//         continue

//     segLen = []
//     for i in range(len(people) - 1):
//         segLen.append(people[i + 1][1] - people[i][1])
//     segLen.append(n - people[-1][1])

//     def make():
//         dp = [
//             [
//                 float('-inf') for _ in range(k + 1)
//             ] for _ in range(k + 1)
//         ]
//         dp[k][0] = 0 # dp[budgetLeft][currMax] is the answer as we loop over each item and the choices we make at that item
//         return dp

//     dp = make()

//     # Pull DP
//     # Loop over new states (k^2)
//     # Loop over incoming DP edges (predecessors) of this state
//     for i, (maxStorage, originalIndex) in enumerate(people):
//         ndp = make() # cloning the old dp here would be a trap, as evne if we do nothing as this new element, we still get to walk forward steps and gain happiness

//         # we are going to need the best dp[fixedBudget][upToThisMax], so compute a prefix
//         pref = make()
//         for budget in range(k + 1):
//             maxScore = 0
//             for currMax in range(k + 1):
//                 maxScore = fmax(maxScore, dp[budget][currMax])
//                 pref[budget][currMax] = maxScore


//         # looping over new states
//         for newBudgetLeft in range(k + 1):
//             for newCurrMax in range(maxStorage + 1):
                    

//                 # to reach this state after this item, we could have been at this state already before this item, and done nothing with this item
//                 # doing nothing with this person would still gain us score for the walk to the next length
//                 ndp[newBudgetLeft][newCurrMax] = fmax(ndp[newBudgetLeft][newCurrMax], dp[newBudgetLeft][newCurrMax] + (segLen[i] * newCurrMax)) # TODO: is max needed

//                 # or, we could have come from any old current max state, we just now spent money to reach the new current max and smaller budget
//                 budgetBeforeSpendingHere = newBudgetLeft + newCurrMax
//                 if budgetBeforeSpendingHere > k:
//                     continue
//                 ndp[newBudgetLeft][newCurrMax] = fmax(ndp[newBudgetLeft][newCurrMax], segLen[i] * newCurrMax + pref[budgetBeforeSpendingHere][newCurrMax])
//                 # the O(k^4) version
//                 # for oldCurrentMax in range(newCurrMax):
//                 #     ndp[newBudgetLeft][newCurrMax] = max(ndp[newBudgetLeft][newCurrMax], dp[budgetBeforeSpendingHere][oldCurrentMax] + (segLen[i] * newCurrMax))

//         dp = ndp
    
//     res = 0 
//     for row in dp:
//         for c in row:
//             res = fmax(res, c)
//     print(res)




// k^4 pull DP
// Loop over items (k)
// Loop over new states of newBudget and newCurrMax (k^2)
// Loop over incoming predecessor states
// T = int(input())
// for _ in range(T):
//     n, k = map(int, input().split())
//     A = list(map(int, input().split()))

//     people = []
//     mx = 0
//     for i, v in enumerate(A):
//         if v > mx:
//             mx = v
//             people.append((v, i)) # holds (maxStorage, originalIndex)

//     if not people:
//         print(0)
//         continue

//     segLen = []
//     for i in range(len(people) - 1):
//         segLen.append(people[i + 1][1] - people[i][1])
//     segLen.append(n - people[-1][1])

//     dp = [
//         [
//             float('-inf') for _ in range(k + 1)
//         ] for _ in range(k + 1)
//     ] 
//     dp[k][0] = 0 # dp[budgetLeft][currMax] is the answer as we loop over each item and the choices we make at that item

//     # Pull DP
//     # Loop over new states (k^2)
//     # Loop over incoming DP edges (predecessors) of this state
//     for i, (maxStorage, originalIndex) in enumerate(people):
//         ndp = [
//             [
//             float('-inf') for _ in range(k + 1)
//             ] for _ in range(k + 1)
//         ] # cloning the old dp here would be a trap, as evne if we do nothing as this new element, we still get to walk forward steps and gain happiness
//         ndp[k][0] = 0

//         # looping over new states
//         for newBudgetLeft in range(k + 1):
//             for newCurrMax in range(maxStorage + 1):

//                 # to reach this state after this item, we could have been at this state already before this item, and done nothing with this item
//                 # doing nothing with this person would still gain us score for the walk to the next length
//                 ndp[newBudgetLeft][newCurrMax] = max(ndp[newBudgetLeft][newCurrMax], dp[newBudgetLeft][newCurrMax] + (segLen[i] * newCurrMax)) # TODO: is max needed

//                 # or, we could have come from any old current max state, we just now spent money to reach the new current max and smaller budget
//                 budgetBeforeSpendingHere = newBudgetLeft + newCurrMax
//                 if budgetBeforeSpendingHere > k:
//                     continue
//                 for oldCurrentMax in range(newCurrMax):
//                     ndp[newBudgetLeft][newCurrMax] = max(ndp[newBudgetLeft][newCurrMax], dp[budgetBeforeSpendingHere][oldCurrentMax] + (segLen[i] * newCurrMax))

//         dp = ndp
    
//     res = 0 
//     for row in dp:
//         for c in row:
//             res = max(res, c)
//     print(res)






//     Push DP O(k^4)
//     Loop over items (k)
//     Loop over old states (k^2)
//     Loop over choices at the old state, how much to spend here (K)
//     Update the new state
//     # dp[budgetLeft][prevMax] is the answer for the items we have processed so far, at each person we need to try spending different amounts or not

//     for i, (maxStorage, originalIndex) in enumerate(people):

//         ndp = [
//             [
//                 float('-inf') for _ in range(k + 1)
//             ] for _ in range(k + 1)
//         ] 

//         ndp[k][0] = 0

//         seg = segLen[i]

//         # looping over old DP states
//         for oldBudgetLeft in range(k + 1):
//             for oldPrevMax in range(k + 1):

//                 # making choices for what we could have done at the old states

//                 # don't spend anything at the old state
//                 gainNoSpend = oldPrevMax * seg
//                 ndp[oldBudgetLeft][oldPrevMax] = dp[oldBudgetLeft][oldPrevMax] + gainNoSpend # not sure if we need to use a max here against the old ndp value

//                 # try different spend amounts from the previous states
//                 maxSpendable = min(oldBudgetLeft, maxStorage)
//                 for spendHere in range(oldPrevMax + 1, maxSpendable + 1):
//                     gainWithSpend = seg * spendHere
//                     ndp[oldBudgetLeft - spendHere][spendHere] = max(ndp[oldBudgetLeft - spendHere][spendHere], dp[oldBudgetLeft][oldPrevMax] + gainWithSpend)
        
//         dp = ndp
    
//     res = 0
//     for row in dp:
//         for c in row:
//             res = max(res, c)
    
//     print(res)