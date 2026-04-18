// https://leetcode.com/problems/student-attendance-record-ii/description/
// Difficulty: Hard
// Tags: dynamic programming 2d

// Problem
/*
An attendance record for a student can be represented as a string where each character signifies whether the student was absent, late, or present on that day. The record only contains the following three characters:

'A': Absent.
'L': Late.
'P': Present.
Any student is eligible for an attendance award if they meet both of the following criteria:

The student was absent ('A') for strictly fewer than 2 days total.
The student was never late ('L') for 3 or more consecutive days.
Given an integer n, return the number of possible attendance records of length n that make a student eligible for an attendance award. The answer may be very large, so return it modulo 109 + 7.
*/

// Solution, O(n) time and O(n) space
/*
Store a memo for subproblems (attendances used, current lates in a row, days left to make), which ends up being 2*3*n. Each state takes constant time to solve also.
*/

const MOD = 10 ** 9 + 7;

var checkRecord = function (n) {
  // memo[absents used][current late in a row][days left to make] stores the answer to that subproblem
  const memo = new Array(2)
    .fill()
    .map(() => new Array(3).fill().map(() => new Array(n + 1).fill(-1)));

  function dp(absentsUsed, currentLateInARow, daysLeft) {
    if (daysLeft === 0) {
      return 1;
    }

    if (memo[absentsUsed][currentLateInARow][daysLeft] !== -1) {
      return memo[absentsUsed][currentLateInARow][daysLeft];
    }

    let resultForThis = 0;

    // if we have used no absents, we can take one
    if (absentsUsed === 0) {
      const ifAbsence = dp(1, 0, daysLeft - 1);
      resultForThis += ifAbsence;
    }

    // if we have 0 or 1 lates in a row, we can take a late
    if (currentLateInARow === 0 || currentLateInARow === 1) {
      const ifLate = dp(absentsUsed, currentLateInARow + 1, daysLeft - 1);
      resultForThis += ifLate;
    }

    // we can always take a present
    const ifPresent = dp(absentsUsed, 0, daysLeft - 1);
    resultForThis += ifPresent;

    memo[absentsUsed][currentLateInARow][daysLeft] = resultForThis % MOD;
    return resultForThis % MOD;
  }

  return dp(0, 0, n);
};
