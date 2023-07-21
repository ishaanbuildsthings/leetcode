// https://leetcode.com/problems/number-of-longest-increasing-subsequence/description/
// Difficulty: Medium
// Tags: dynamic programming 2d, subsequence

// Problem
/*
Given an integer array nums, return the number of longest increasing subsequences.

Notice that the sequence has to be strictly increasing.
*/

// Solution, O(n^2) time and O(n) space. O(n log n) time is easily doable but I implemented this first.
/*
This question is very similar to a normal LIS problem, the only difference is, when we find a subsequence of a new longest length, we need to reset our result count. If we find a subsequence of the same length, we add to our result count.

We also need to importantly track how many ways a subsequence of a given length can be reached. For instance in [1, 1, 3], at 3, we have 2 subsequences of length 2, not just 1. So our memo array stores tuples of [length, count].

The n log n is doable with the binary search LIS version, I just don't think it is worth implementing unless needed to not TLE.
*/

var findNumberOfLIS = function (nums) {
  let result = 0;
  let longestLengthEver = 0;

  // memo[i] gives us a tuple of [longest increasing subsequence wher ethe last number is the ith number, # of increasing subsequences that can be made this way]
  const memo = new Array(nums.length).fill(-1);

  for (let i = 0; i < nums.length; i++) {
    const num = nums[i];
    // iterate through all prior numbers
    let longestForThisDp = 1; // worst case our longest increasing subsequence has length 1
    let numberOfSubsequencesWithLongestLengthForThisDp = 1;
    for (let j = 0; j < i; j++) {
      const priorNum = nums[j];
      // if the previous number is smaller than our current number, we can make a subsequence off of that
      if (num > priorNum) {
        const [previousSubsequenceLength, numberPrevSubsequences] = memo[j];
        const subsequenceLengthUsingThisPrior = previousSubsequenceLength + 1;

        // if using this prior number, we can't make a longer subsequence than what we have seen so far with num, we just ignore it
        if (subsequenceLengthUsingThisPrior < longestForThisDp) {
          continue;
        }
        /* here, the subsequence length using the prior is >= the longest we have been able to make for num */

        // if the subsequence we form is the same length as what we have already, we gain new subsequences of that length
        if (subsequenceLengthUsingThisPrior === longestForThisDp) {
          numberOfSubsequencesWithLongestLengthForThisDp +=
            numberPrevSubsequences;
        }

        // if the new subsequence is longer, we have to reset the longest for this dp, and the number of subsequences of that length
        else if (subsequenceLengthUsingThisPrior > longestForThisDp) {
          longestForThisDp = subsequenceLengthUsingThisPrior;
          numberOfSubsequencesWithLongestLengthForThisDp =
            numberPrevSubsequences;
        }
      }
    }
    memo[i] = [
      longestForThisDp,
      numberOfSubsequencesWithLongestLengthForThisDp,
    ];
    // update the result
    if (longestForThisDp > longestLengthEver) {
      result = numberOfSubsequencesWithLongestLengthForThisDp;
      longestLengthEver = longestForThisDp;
    } else if (longestForThisDp === longestLengthEver) {
      result += numberOfSubsequencesWithLongestLengthForThisDp;
    }
  }

  return result;
};
