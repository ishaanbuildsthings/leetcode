// https://leetcode.com/problems/strange-printer/description/
// Difficulty: Hard
// tags: dynamic programming 2d, top down recursion

// Problem
/*
There is a strange printer with the following two special properties:

The printer can only print a sequence of the same character each time.
At each turn, the printer can print new characters starting from and ending at any place and will cover the original existing characters.
Given a string s, return the minimum number of turns the printer needed to print it.
*/

// Solution, O(n^3) time and O(n^2) space, dynamic programming
/*
This is a very difficult question. Given the constraint n <= 100, it suggests we are looking for an n^3 solution.

To solve the general problem of printing, we can break it down to a subproblem. Say we our goal string is `a` followed by some string, maybe `ba`, so our total string is `aba`. Clearly we have two options:

1) We can print this `a` separately, meaning the total prints needed is 1 + the prints needed for `ba`.
2) We can print this `a` together with some later `a`, meaning at one point we print from [0, j] where j is the index of a later a. In this case, there is only one future `a`. Which means the solution is the minimum prints needed to print the stuff in-between, which is `b`, plus the number of prints needed to print the remaining portion, which is `a`, which totals to 2.

We need to consider all future a's, not just the first or last. We can see situations where we would want to print our `a` with the last `a`, such as `aba`. by printing 'with' something, it means when we print that sequence, the two characters do not get overwritten. in `zbabza`, when we try to print the a's together, optimally we should overwrite the first `a`, so they are printed separately. This counterexample was constructed by thinking of `baba`, then adding two letters to make printing the a's separately the uniquely optimal solution.

So, for each letter, we look at all future letters that are the same, and use the intermediate dps. There are n^2 subarrays and each subarray takes n time to iterate and check, so n^3 time.

To solve it with bottom up recursion, we need to solve all problems of length 1, then 2, etc. For each size, we choose a starting position, then iterate through the next `length` positions to see matching characters.
*/

var strangePrinter = function (s) {
  // dp[i][j] contains the answer for the substring from [i, j], 0 is a dummy value that implies we haven't solved it yet (as a minimum answer is always 1)
  const memo = new Array(s.length)
    .fill()
    .map(() => new Array(s.length).fill(0));

  /*
    to solve the problem of 'abax', we can look at the a, then for any future letter up to j, if that future letter equals a, we can create a sub problem, for instance

    solution to abax could be:
    a + bax (base case, we print it separately)
    b + ax, meaning we print the a with the ax
    */

  function dp(i, j) {
    // edge case, for instance in 'aa' we might end up calling dp(1, 0)
    if (i > j) {
      return 0;
    }

    if (memo[i][j]) {
      return memo[i][j];
    }

    // worst case, we print the starting letter as a separate operation from the remaining letters
    let minimum = 1 + dp(i + 1, j);

    for (let futureLetter = i + 1; futureLetter <= j; futureLetter++) {
      if (s[futureLetter] == s[i]) {
        minimum = Math.min(
          minimum,
          dp(i + 1, futureLetter - 1) + dp(futureLetter, j)
        );
      }
    }

    memo[i][j] = minimum;
    return minimum;
  }

  return dp(0, s.length - 1);
};
