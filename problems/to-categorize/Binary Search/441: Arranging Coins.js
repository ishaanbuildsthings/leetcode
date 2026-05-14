// https://leetcode.com/problems/arranging-coins/description/
// Difficulty: Easy
// tags: math, binary search

// Problem
/*
You have n coins and you want to build a staircase with these coins. The staircase consists of k rows where the ith row has exactly i coins. The last row of the staircase may be incomplete.

Given the integer n, return the number of complete rows of the staircase you will build.
*/

// Solution 1, O(n)/O(1) time, O(1) space
/*
The sum of the first k natural numbers is: k(k + 1) / 2
we need to find the largest k(k+1)/2 that fits under n, which is the largest k^2 + k that fits under 2n
We can set up a relation: k(k + 1)/2 = 2n
Here, if we provide n coins, we get how many rows we can fill with that, but we may get a decimal, we need to floor it to see how many complete rows we can get
use complete the square:
1k^2 + 1k = 2n
b=1, so we add 0.5b squared
1k^2 + 1k + 0.25 = 2n + 0.25
complete the square
(1k + 0.5)^2 = 2n + 0.25
k + 0.5 = sqrt(2n + 0.25)
k = sqrt(2n + 0.25)
answer = floor(k)

Can be either O(1) or O(n) depending on how sqrt is implemented / the constraints, for instance sqrt can be bounded by some property if the integer has a max limit
*/
var arrangeCoins = function (n) {
  return Math.floor(Math.sqrt(2 * n + 0.25) - 0.5);
};

// Solution 2, log n time, O(1) space
// do a binary search to find the number of rows

var arrangeCoins = function (n) {
  // n(n + 1) / 2 is the total number of coins needed for n rows

  let l = 0;
  let r = n;
  let m = Math.floor((r + l) / 2);
  // do a binary search to find out how many rows we need
  while (l < r) {
    m = Math.floor((r + l) / 2);
    const coinsNeeded = (m * (m + 1)) / 2;

    // if we need fewer than n coins, we can potentially do more rows
    if (coinsNeeded < n) {
      l = m + 1;
    }
    // if we need more than n coins or exactly n coins to fill the row, we can at most do m rows
    else if (coinsNeeded >= n) {
      r = m;
    }
  }

  // if we weren't able to fill out our last row, return l-1
  if ((l * (l + 1)) / 2 > n) {
    return l - 1;
  }
  return l;
};
