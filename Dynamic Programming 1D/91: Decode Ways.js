// https://leetcode.com/problems/decode-ways/description/
// Difficulty: Medium
// tags: dynamic programming 1d

// Problem
/*
Simplified:

Example 2:

Input: s = "226"
Output: 3
Explanation: "226" could be decoded as "BZ" (2 26), "VF" (22 6), or "BBF" (2 2 6).


Detailed:

A message containing letters from A-Z can be encoded into numbers using the following mapping:

'A' -> "1"
'B' -> "2"
...
'Z' -> "26"
To decode an encoded message, all the digits must be grouped then mapped back into letters using the reverse of the mapping above (there may be multiple ways). For example, "11106" can be mapped into:

"AAJF" with the grouping (1 1 10 6)
"KJF" with the grouping (11 10 6)
Note that the grouping (1 11 06) is invalid because "06" cannot be mapped into 'F' since "6" is different from "06".

Given a string s containing only digits, return the number of ways to decode it.

The test cases are generated so that the answer fits in a 32-bit integer.
*/

// Solution, O(n^2) time and O(1) space, iterative dp.

/*
Say we have 226.

6 is our base case, we can form 1 encoding, since 6 is non-zero.

At 2 (since it is non-zero), we can form:

The number of subsequences starting at 6, assuming we treat 2 as a single digit.

Or, the number of subsequences starting from the digit after 6, assuming 26 is valid. We default this `dp2` to start at 1.

So fill out the tabulation, but we only need to memoize two values. I did it starting from the back, but we can also fill out the dp starting from the front, and looking at n prior elements (either left to right or right to left);
*/

var numDecodings = function (s) {
  // store the dp for future cells that we can convert. for instance in the string '123', we need to initially solve for the number of ways we can make at char 2. if we treat a 2 as is, one type of way is we take the number of ways starting from 3. if we take '23', then another way is the number of ways starting from after the 3. we add these together to get the number of ways starting from 2.
  let dp1 = s[s.length - 1] === "0" ? 0 : 1; // initially, number of ways starting from the last digit. if the last digit is 0, we have no ways, starting from the last digit, otherwise we have 1 way.
  let dp2 = 1; // initially, number of ways starting from after the last digit, in a way

  // checks if a 2-digit string forms a number <= 26, things like 07 don't count
  function isValid(str) {
    // leading 0s are not allowed
    if (str[0] === "0") {
      return false;
    }

    // leading 3s or higher are invalid
    if (Number(str[0]) > 2) {
      return false;
    }

    // a leading 1 is always valid
    if (str[0] === "1") {
      return true;
    }
    /* here, we have a leading two, which is only sometimes valid, for 26 or under */

    if (Number(str[1]) <= 6) {
      return true;
    }

    return false;
  }

  // start iterating from the second to last character, backwards
  for (let i = s.length - 2; i >= 0; i--) {
    // if the digit itself is a 0, it is impossible to form any solutions starting from there
    if (s[i] === "0") {
      dp2 = dp1;
      dp1 = 0;
      continue;
    }

    let newWays = dp1; // we can at least make as many ways as we did with the next digit

    // if our two digit substring is valid, we can also make some more ways
    const str = s.slice(i, i + 2); // two digit string
    if (isValid(str)) {
      newWays += dp2;
    }

    dp2 = dp1;
    dp1 = newWays;
  }

  return dp1;
};
