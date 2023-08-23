// https://leetcode.com/problems/maximum-score-of-spliced-array/description/
// Difficulty: Hard
// Tags: kadane's

// Problem
/*
You are given two 0-indexed integer arrays nums1 and nums2, both of length n.

You can choose two integers left and right where 0 <= left <= right < n and swap the subarray nums1[left...right] with the subarray nums2[left...right].

For example, if nums1 = [1,2,3,4,5] and nums2 = [11,12,13,14,15] and you choose left = 1 and right = 2, nums1 becomes [1,12,13,4,5] and nums2 becomes [11,2,3,14,15].
You may choose to apply the mentioned operation once or not do anything.

The score of the arrays is the maximum of sum(nums1) and sum(nums2), where sum(arr) is the sum of all the elements in the array arr.

Return the maximum possible score.

A subarray is a contiguous sequence of elements within an array. arr[left...right] denotes the subarray that contains the elements of nums between indices left and right (inclusive).
*/

// Solution, O(n) time, O(n) space
/*
Iterate over the arrays, finding the difference at that point if we used the other value instead. Now, iterate over nums1, and track our current gain if we only used nums2 numbers instead (by using the differences we generated). Any time it drops below 0, we wouldn't have used those numbers, so we reset to 0. Repeat for nums2.

/**
 * @param {number[]} nums1
 * @param {number[]} nums2
 * @return {number}
 */
var maximumsSplicedArray = function (nums1, nums2) {
  const diffs1 = [];
  const diffs2 = [];
  for (let i = 0; i < nums1.length; i++) {
    const diff1 = nums2[i] - nums1[i];
    const diff2 = nums1[i] - nums2[i];
    diffs1.push(diff1);
    diffs2.push(diff2);
  }

  const sum1 = nums1.reduce((acc, val) => acc + val, 0);
  const sum2 = nums2.reduce((acc, val) => acc + val, 0);

  let result = 0;

  let prefixBenefit1 = 0; // kadane's
  let maxGain1 = 0;
  // try bringing numbers from nums2 into nums1
  for (let i = 0; i < nums1.length; i++) {
    const potentialGain = diffs1[i];
    prefixBenefit1 += potentialGain;
    maxGain1 = Math.max(maxGain1, prefixBenefit1);
    prefixBenefit1 = Math.max(prefixBenefit1, 0);
  }

  // try bringing numbers from nums1 into nums2
  let prefixBenefit2 = 0;
  let maxGain2 = 0;
  for (let i = 0; i < nums2.length; i++) {
    const potentialGain = diffs2[i];
    prefixBenefit2 += potentialGain;
    maxGain2 = Math.max(maxGain2, prefixBenefit2);
    prefixBenefit2 = Math.max(prefixBenefit2, 0);
  }

  result = Math.max(sum1 + maxGain1, sum2 + maxGain2);
  return result;
};
