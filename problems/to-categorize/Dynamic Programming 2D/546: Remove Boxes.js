// https://leetcode.com/problems/remove-boxes/description/
// Difficulty: Hard
// tags: dynamic programming 2d, top down recursion

// Problem
/*
Example:
Input: boxes = [1,3,2,2,2,3,4,3,1]
Output: 23
Explanation:
[1, 3, 2, 2, 2, 3, 4, 3, 1]
----> [1, 3, 3, 4, 3, 1] (3*3=9 points)
----> [1, 3, 3, 3, 1] (1*1=1 points)
----> [1, 1] (3*3=9 points)
----> [] (2*2=4 points)

Detailed:
You are given several boxes with different colors represented by different positive numbers.

You may experience several rounds to remove boxes until there is no box left. Each time you can choose some continuous boxes with the same color (i.e., composed of k boxes, k >= 1), remove them and get k * k points.

Return the maximum points you can get.
*/

// Solution, O(n^4) time and O(n^3) space
/*
Similar to the description in the dynamic programming txt file which explains reducing the solution space in a dp problem from n!->2^n->n^2.

If we try to remove some group of boxes, then another, and so on, we are n!. This is just brute force. If we memoize arrangements, so for instance in 1, 2, 3, we remove 2->1 or 1->2, we get the same memoized result, this means we have 2^n possible arrangements, since any group of boxes is either present or missing, and at most we have n unique groups. This is still too slow. But if we split the problem into a recurrence function using n^2 subarrays, with an extra n dimension of the number of similar boxes on the left, we have n^3 states to fill, each taking n time, by iterating through n future boxes to check what hapens if we remove those boxes together (meaning we remove everything in between them first).
*/

var removeBoxes = function (boxes) {
  // create a dp mapping of solutions for [l][r][leftCount]
  /*
    for instance, in 1, 2, 1
    the base case is we could remove the first 1 separately, so we get: score of 1 + solution for [2, 1]

    or, we could remove the 1 with some future 1, meaning all the numbers in between need to be removed first. in this case, there is only one future 1, the solution would be:

    the solution of the inbetween boxes [2], + the solution of the remaining portion on the right [1]

    but, since the score depends on how many consecutive boxes are removed, for that last 1, we also need to track a dp of how many boxes to the left we currently have that match

    so in 1, 1, 2, 1

    one way to solve this is to remove the initial 1 with the second 1, that means we have to first remove everything in between them (which is nothing), then add the solution for what is remaining

    dp[0, 3] (one way to do it):

    dp of what is between 0 and 1 (nothing) + dp[1, 3] = 2 total

    but actually, dp [1,3] isn't perfectly correct, because we have an extra 1 on the left, so it's
    dp[1][3][1], meaning the solution for range from 1 to 3 with a single extra 1 on the left

    and to solve the problem of dp(l, r, leftCount), when we remove the first character, if we remove it separately, we get extra points based on left count, if we remove it with a future one, we also get extra points
    */
  const memo = new Array(boxes.length)
    .fill()
    .map(() =>
      new Array(boxes.length)
        .fill()
        .map(() => new Array(boxes.length).fill(null))
    );

  function dp(l, r, leftCount) {
    // edge case, for instance in [5], we remove the digit, then compute dp[1, 0]
    if (l > r) {
      return 0;
    }

    if (memo[l][r][leftCount]) {
      return memo[l][r][leftCount];
    }

    const baseCase = (leftCount + 1) * (leftCount + 1) + dp(l + 1, r, 0); // we remove the digit separately from the rest
    let maximum = baseCase;
    for (let i = l + 1; i <= r; i++) {
      if (boxes[i] !== boxes[l]) {
        continue;
      }
      // 1, 2, 1, 5, 6, 7
      // one option is the things in between the 1s, so [2], plus the [1, 5, 6, 7] with an even higher amount of ones to the left
      const inbetween = dp(l + 1, i - 1, 0);
      const onTheRight = dp(i, r, leftCount + 1);
      maximum = Math.max(maximum, inbetween + onTheRight);
    }

    memo[l][r][leftCount] = maximum;
    return maximum;
  }

  return dp(0, boxes.length - 1, 0);
};
