// https://leetcode.com/problems/longest-arithmetic-subsequence/description/
// Difficulty: Medium
// tags: dynamic programming 2d

// Problem
/*
Simplified:

Input: nums = [20,1,15,3,10,5,8]
Output: 4
Explanation:  The longest arithmetic subsequence is [20,15,10,5].

Detailed:

Given an array nums of integers, return the length of the longest arithmetic subsequence in nums.

Note that:

A subsequence is an array that can be derived from another array by deleting some or no elements without changing the order of the remaining elements.
A sequence seq is arithmetic if seq[i + 1] - seq[i] are all the same value (for 0 <= i < seq.length - 1).
*/

// Solution, O(n^2) time and O(n^2) space

/*
Maintain a dp array of length n, where each element is a hash map. The hash map will map a diff to the length of the longest subsequence that ends at that index with that diff. For instance, if we have [9, 6, 3]. We start iterating from the 2nd to last element, backwards (last element is base case).

* We could also iterate from the beginning, and check prior elements (either left to right, or right to left), but in my opinion doing it the other way around is a bit simpler.

At 6, we start iterating for all future numbers. We see a 3, which makes a diff of -3. So we know the 6 has { -3 : 2 }, as in a sequence of length 2 can be made, starting at 6.

At 9, we look at 6. The diff is -3. 6 already has a subsequence using that diff, of length 2, so we extend the length, meaning at 9 we have { -3 : 3 }.

Be careful not to overwrite things:

say we had ths sequence 2, 5, 8, 5

    at the first 5, we know we can make a sequence of length 2, with a diff of +3
    so when we are solving for the 2, and we see that, we know we can make a sequence of length 3
    but when we get to the second 5, we also know that using a diff of +3 we can make a sequence of length 2 in this case, which is just the default.

    we shouldn't overwrite our +3 diff data, which is why we take the max of if we already had that diff, as well as the new sequence length
*/

var longestArithSeqLength = function (nums) {
  /*
   each element of the dp will hold a hash map for a diff to how long that subsequence is
    for instance in 1, 6, 3
    at 6:
    { -3 : 2 }

    at 1:
    { +5 : 2, +2 : 2 }

    so when we look at an earlier element in the dp, we scan across n elements to the right of it. for each element, we lookup the diff to determine how long we can make the current subsequence
   */
  const dp = new Array(nums.length).fill().map(() => ({}));

  let result = 2; // in the worst case, all arrays of length >= 2 have an arithmetic subsequence of at least 2, so we use this for the default value

  // start iterating from the second to last element, backwards
  for (let i = nums.length - 2; i >= 0; i--) {
    // for each number, iterate on all future numbers
    for (
      let futureNumIndex = i + 1;
      futureNumIndex < nums.length;
      futureNumIndex++
    ) {
      const diff = nums[futureNumIndex] - nums[i];
      const futureNumMapping = dp[futureNumIndex];

      let lengthOfSubsequenceUsingThisNumber = 2; // default, we can always form a subsequence of length 2 between 2 numbers
      if (diff in futureNumMapping) {
        lengthOfSubsequenceUsingThisNumber = 1 + futureNumMapping[diff];
      }

      /*
            say we had ths sequence 2, 5, 8, 5

            at the first 5, we know we can make a sequence of length 2, with a diff of +3
            so when we are solving for the 2, and we see that, we know we can make a sequence of length 3
            but when we get to the second 5, we also know that using a diff of +3 we can make a sequence of length 2 in this case, which is just the default.

            we shouldn't overwrite our +3 diff data, which is why we take the max of if we already had that diff, as well as the new sequence length
            */
      dp[i][diff] = Math.max(
        lengthOfSubsequenceUsingThisNumber,
        dp[i][diff] === undefined ? 0 : dp[i][diff]
      );
      result = Math.max(result, dp[i][diff]);
    }
  }

  return result;
};
