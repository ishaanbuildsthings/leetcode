// https://leetcode.com/problems/construct-the-longest-new-string/description/
// Difficulty: Medium
// tags: dynamic programming 2d (4d)

// Problem
/*
You are given three integers x, y, and z.

You have x strings equal to "AA", y strings equal to "BB", and z strings equal to "AB". You want to choose some (possibly all or none) of these strings and concactenate them in some order to form a new string. This new string must not contain "AAA" or "BBB" as a substring.

Return the maximum possible length of the new string.

A substring is a contiguous non-empty sequence of characters within a string.


*/

// Solution, O(x*y*z*3) = x*y*z time, same with space. Dynamic programming 4d.

/*
Maintain a DP table of [x remaining][y remaining][z remaining][endingLetters] that maps to the longest string that can make.

To solve a case, we check our ending letters, see what other letters we can append to the end as long as we have enough of those strings, and consider those options.

The dp helps, for instance AA|BB|AB would map the same as BB|AA|AB, so we memoize that.

Also, do not forget when we allocate the x, y, and z dimensions of the dp, we need to add 1 to each, as we need to consider the case where we have 0 of each string left.
*/
// * Solution 2, greedy with math, O(1) time and O(1) space. We can use every AB by putting them together. AB+AB+AB etc. But we can't use AB to glue together AA and BB. For instance AA + AB + BB is invalid. BB + AB + AA is valid, but BB + AA was already valid. So we can greedily use every AB, then pairs of AA and BB, and one extra of them.

var longestString = function (x, y, z) {
  // maintain a dp that stores: x left, y left, z left, last two letters, mapped to the longest string they can make
  const dp = new Array(x + 1)
    .fill()
    .map(() =>
      new Array(y + 1)
        .fill()
        .map(() =>
          new Array(z + 1).fill().map(() => ({ AA: null, BB: null, AB: null }))
        )
    );

  function recurse(xLeft, yLeft, zLeft, endingLetters, currentStringLength) {
    if (dp[xLeft][yLeft][zLeft][endingLetters] !== null) {
      return dp[xLeft][yLeft][zLeft][endingLetters];
    }

    let maxLength = currentStringLength;

    // AA + BB
    if (endingLetters === "AA" && yLeft > 0) {
      const option1 = recurse(
        xLeft,
        yLeft - 1,
        zLeft,
        "BB",
        currentStringLength + 2
      );
      maxLength = Math.max(maxLength, option1);
    }

    // BB + AA
    if (endingLetters === "BB" && xLeft > 0) {
      const option2 = recurse(
        xLeft - 1,
        yLeft,
        zLeft,
        "AA",
        currentStringLength + 2
      );
      maxLength = Math.max(maxLength, option2);
    }

    // BB + AB
    if (endingLetters === "BB" && zLeft > 0) {
      const option3 = recurse(
        xLeft,
        yLeft,
        zLeft - 1,
        "AB",
        currentStringLength + 2
      );
      maxLength = Math.max(maxLength, option3);
    }

    // AB + AA
    if (endingLetters === "AB" && xLeft > 0) {
      const option4 = recurse(
        xLeft - 1,
        yLeft,
        zLeft,
        "AA",
        currentStringLength + 2
      );
      maxLength = Math.max(maxLength, option4);
    }

    // AB + AB
    if (endingLetters === "AB" && zLeft > 0) {
      const option5 = recurse(
        xLeft,
        yLeft,
        zLeft - 1,
        "AB",
        currentStringLength + 2
      );
      maxLength = Math.max(maxLength, option5);
    }

    dp[xLeft][yLeft][zLeft][endingLetters] = maxLength;
    return maxLength;
  }

  // try using 'AA' at the start
  let option1 = 0;
  if (x > 0) {
    option1 = recurse(x - 1, y, z, "AA", 2);
  }

  // try using 'BB' at the start
  let option2 = 0;
  if (y > 0) {
    option2 = recurse(x, y - 1, z, "BB", 2);
  }

  // try using 'AB' at the start
  let option3 = 0;
  if (z > 0) {
    option3 = recurse(x, y, z - 1, "AB", 2);
  }

  return Math.max(option1, option2, option3);
};
