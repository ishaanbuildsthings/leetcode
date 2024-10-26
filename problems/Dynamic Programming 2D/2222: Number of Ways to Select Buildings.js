// Problem: https://leetcode.com/problems/number-of-ways-to-select-buildings/description/
// difficulty: medium
// tags: dynamic programming 2d

// Problem
/*
You are given a 0-indexed binary string s which represents the types of buildings along a street where:

s[i] = '0' denotes that the ith building is an office and
s[i] = '1' denotes that the ith building is a restaurant.
As a city official, you would like to select 3 buildings for random inspection. However, to ensure variety, no two consecutive buildings out of the selected buildings can be of the same type.

For example, given s = "001101", we cannot select the 1st, 3rd, and 5th buildings as that would form "011" which is not allowed due to having two consecutive buildings of the same type.
Return the number of valid ways to select 3 buildings.
*/

// Solution, O(n) time and space
// I had to use JS since Python hit the time limit. It's an O(n) time solution since the other parameters are constant.

var numberOfWays = function (s) {
  let rightDifferent = {}; // maps an index to the first index on the right with a different index, or undefined
  let rightZero = undefined;
  let rightOne = undefined;

  for (let i = s.length - 1; i >= 0; i--) {
    if (s[i] === "1") {
      rightDifferent[i] = rightZero;
      rightOne = i;
    } else {
      rightDifferent[i] = rightOne;
      rightZero = i;
    }
  }

  let memo = {};

  function dp(prevSelected, numSelected, i) {
    // base case
    if (numSelected === 3) {
      return 1;
    }
    if (i === undefined || i >= s.length) {
      return 0;
    }

    let key = prevSelected + "-" + numSelected + "-" + i;
    if (memo[key] !== undefined) {
      return memo[key];
    }

    let resForThis = 0;

    if (s[i] !== prevSelected) {
      resForThis += dp(s[i], numSelected + 1, rightDifferent[i]);
    }

    resForThis += dp(prevSelected, numSelected, i + 1);

    memo[key] = resForThis;
    return resForThis;
  }

  return dp("N", 0, 0); // Using 'N' to represent None in Python
};
