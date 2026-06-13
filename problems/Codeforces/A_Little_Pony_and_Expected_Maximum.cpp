#include <bits/stdc++.h>
using namespace std;

int faces, rolls;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    cin >> faces >> rolls;

    // we could enumerate by checking the # of ways the max is X for all X
    // I think we force one die to be X (but don't define which one) and then do nCk on the remaining ones to all be less?
    // aggregate the # of ways and divide by all ways?

    // but that is a hint for linearity of expectation
    // denote i_1 as a 1 if we get a max >= 1 else 0
    // i_2 as a 1 if we get a max >= 2 else 0

    // remember events do not need to be disjoint, if we have a grid and two regions A and B that overlap
    // and shooting inside A or shooting inside B gives 1 point (the shared region gives 2)
    // then E[A+B] = E[A] = + E[B] intuitively and the middle shared portion gives 2 points
    //  E[i_1 + i_2 + i_3 + ... rolls] is E[i_1] + E[i_2] + ...

    double res = 0.0;
    for (int mx = 1; mx <= faces; mx++) {
      // chance of rolling that as an at least max is 1-(chance we do not roll)
      // chance we do not roll is (mx-1 / faces) ^ rolls
      // so chance of not rolling a 3 or higher on a 7 sided die is 2/7 ^ rolls
      double chanceNoRoll = pow((mx-1.0) / faces, rolls);
      double chanceRoll = 1.0 - chanceNoRoll;
      res += chanceRoll;
    }

    cout << fixed << setprecision(15) << res << endl;

    return 0;
}