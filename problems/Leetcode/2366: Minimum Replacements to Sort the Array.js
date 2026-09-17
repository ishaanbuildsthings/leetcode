// https://leetcode.com/problems/minimum-replacements-to-sort-the-array/description/
// Difficulty: Hard

// Problem
/*
You are given a 0-indexed integer array nums. In one operation you can replace any element of the array with any two elements that sum to it.

For example, consider nums = [5,6,7]. In one operation, we can replace nums[1] with 2 and 4 and convert nums to [5,2,4,7].
Return the minimum number of operations to make an array that is sorted in non-decreasing order.
*/

// Solution, O(n) time and O(1) space
/*
When we consider a number, we need to know if we should split it or not. We should split it if at some point a future number will be smaller than the current number. For instance in [4, 5, 4], when we look at the first 4, we need to know the future 5 will be split. We can work backwards (when solving the problem I determined an intuition but I've forgotten why now). I think it's one of those things where working backwards helps us determine some information we would have needed to know in advance.

By working backwards, a given number needs to be smaller than all future numbers. If it isn't, split until it is, and update the new smallest.

We do this for each number. To solve a given number, we use the `split` function which is a clever way to split things.
*/

/**
 * @param {number[]} nums
 * @return {number}
 */
var minimumReplacement = function (nums) {
  // takes a number that needs to be split, and a threshold such that all splits must be under that, returns the number of splits made, and the new smallest number lead
  function split(num, threshold) {
    if (num % threshold === 0) {
      return [num / threshold - 1, threshold];
    }
    const splitsMade = Math.floor(num / threshold);
    const pieces = splitsMade + 1;
    return [Math.floor(num / threshold), Math.floor(num / pieces)];
  }

  let smallest = Infinity;
  let result = 0;
  for (let i = nums.length - 1; i >= 0; i--) {
    // if our number is bigger than the smallest on the right, split it
    if (nums[i] > smallest) {
      const [splitsMade, newSmallest] = split(nums[i], smallest);
      smallest = newSmallest;
      result += splitsMade;
    }
    smallest = Math.min(smallest, nums[i]);
  }

  return result;
};

/*

have to split when our number is bigger than the smallest number on the right subproblem

when we split, we need our ending number to be <= the smallest on the right
we need our starting to be bigger than the largest on the left
*/
