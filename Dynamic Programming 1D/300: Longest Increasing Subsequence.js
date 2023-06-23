// https://leetcode.com/problems/longest-increasing-subsequence/description/
// Difficulty: Medium
// tags: dynamic programming 1d, bottom up recursion, binary search, self balancing BST

// Problem
/*
Input: nums = [10,9,2,5,3,7,101,18]
Output: 4
Explanation: The longest increasing subsequence is [2,3,7,101], therefore the length is 4.

Given an integer array nums, return the length of the longest strictly increasing
subsequence.
*/

/* WRITEUP

Relatively naive solution is to do tabulation starting from the end. We know 18 has a subsequence length of 1. We look at 101, and scan up to n elements to the right. We greedily select the longest continual subsequence, provided the number we look at is bigger than our current number. This results in n^2 time, and n memory for the tabulation.

We can also go left to right, storing a subsequence in an array. If we find the biggest element, add it onto the end. If we don't, replace the bigger element in the array with that new element. We find that with binary search, so n log n time. This is basically like using the array itself as a cache sort of, making the elements we track as good as possible.

We can also do the above using a self balancing BST.
*/

// Solution 1, tabulation, O(n^2) time, O(n) space
/*
* Solution 2 can be done in O(n log n) time. We iterate from the beginning. Say our sequence is 10, 9, 2, 5, 3, 1, 2, 3.
* At 10, our longest subsequence is [10]. At 9, we cannot add that onto the end. So we will use our current subsequence sort of as a cache. We overwrite the smallest value that is larger than 9, with 9. This is found in log n time with binary search. Now our subsequence is [9].
* At 2, we again ovewrite, making [2]. We add a 5, [2, 5]. At 3, we ovewrite the 5, [2, 3]. At 1, we overwrite the 2, [1, 3]. Note that what we store isn't necessarily the actual subsequence we have, rather we are sort of using the array as a cache. Now if we had say a 4, it would be greater than 3, so we could add it on. But [1, 3, 4] isn't our longest subequence, [2, 3, 4] would be. The 1 is just there in case we could make longer subsequences that fit in between. For instance if we had a 1.1, 1.2, and 1.3, we would overwrite the 3, overwrite the 4, then add on the 1.3.

*/
var lengthOfLIS = function (nums) {
  let tabulation = new Array(nums.length).fill(1); // to start, every elements longest subsequence is 1

  let result = 1;

  // iterate backwards, starting from the second to last element
  for (let i = tabulation.length - 2; i >= 0; i--) {
    const numWeAreSolvingFor = nums[i];
    let currentLongest = 1;
    // iterate forwards, starting from the element. if the number we see is bigger, we can greedily select a longer subsequence
    for (let j = i + 1; j < tabulation.length; j++) {
      const num = nums[j];
      if (num > numWeAreSolvingFor) {
        currentLongest = Math.max(currentLongest, 1 + tabulation[j]);
      }
    }
    tabulation[i] = currentLongest;
    result = Math.max(result, currentLongest);
  }

  return result;
};
