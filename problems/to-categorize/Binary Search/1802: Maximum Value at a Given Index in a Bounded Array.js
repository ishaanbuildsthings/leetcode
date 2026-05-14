// https://leetcode.com/problems/maximum-value-at-a-given-index-in-a-bounded-array/description/
// Difficulty: Medium
// tags: binary search, math

// Problem
/*
Simplified:
Input: n = 4, index = 2,  maxSum = 6
Output: 2
Explanation: nums = [1,2,2,1] is one array that satisfies all the conditions.
There are no arrays that satisfy all the conditions and have nums[2] == 3, so 2 is the maximum nums[2].

You are given three positive integers: n, index, and maxSum. You want to construct an array nums (0-indexed) that satisfies the following conditions:

nums.length == n
nums[i] is a positive integer where 0 <= i < n.
abs(nums[i] - nums[i+1]) <= 1 where 0 <= i < n-1.
The sum of all the elements of nums does not exceed maxSum.
nums[index] is maximized.
Return nums[index] of the constructed array.

Note that abs(x) equals x if x >= 0, and -x otherwise.
*/

// Solution, O(log k), where k is the max sum. O(1) space.
/*
Do a binary search for the max that we can assign to the number at position `index`. When we assign it, determine the sums on the left and right using triangle numbers. We needed to cast to BigInt to avoid overflow, but probably could have avoided it with a different formula.
*/

// returns the sum of the first n triangle numbers, starting at 1
function sumNTriangles(n) {
  if (n < 0) {
    return BigInt(0);
  }
  return (BigInt(n) * (BigInt(n) + 1n)) / 2n;
}

var maxValue = function (n, index, maxSum) {
  const elementsToLeft = index;
  const elementsToRight = n - index - 1;

  // binary search boundaries, testing the maximum value we can store at index
  let l = 1;
  let r = maxSum;
  while (l <= r) {
    const m = Math.floor((r + l) / 2); // m is a value we will test for the number at index

    // the sum of numbers to the left of index will be composed of two triangle numbers, and maybe some 1s
    /*
         _ _ 4 _ _ _ _
               ^
               m - 1 triangle number is added
               3+2+1

               if m-1 is under elementsToRight, we add extra 1s, same with the left side.

            ^
            m-1 triangle number is added, 3+2+1
            we also subtract the triangle number 1, which is m-1-elementsToLeft

        */
    const biggerLeftTriangle = sumNTriangles(m - 1);
    const smallerLeftTriangle = sumNTriangles(m - 1 - elementsToLeft);
    const sumToLeft = biggerLeftTriangle - smallerLeftTriangle;

    // same with the sum on the right
    const biggerRightTriangle = sumNTriangles(m - 1);
    const smallerRightTriangle = sumNTriangles(m - 1 - elementsToRight);
    const sumToRight = biggerRightTriangle - smallerRightTriangle;

    let onesOnRight = 0;
    if (elementsToRight > m - 1) {
      onesOnRight = elementsToRight - (m - 1);
    }
    let onesOnLeft = 0;
    if (elementsToLeft > m - 1) {
      onesOnLeft = elementsToLeft - (m - 1);
    }

    // console.log(`sum to left is: ${sumToLeft + onesOnLeft}`);

    // console.log(`sum to right is: ${sumToRight + onesOnRight}`);

    const totalSum =
      BigInt(m) +
      sumToLeft +
      sumToRight +
      BigInt(onesOnRight) +
      BigInt(onesOnLeft);

    if (totalSum <= maxSum) {
      l = m + 1;
    }
    // else if (totalSum === maxSum) return m;
    else {
      r = m - 1;
    }
  }

  return r; // can also return l - 1
};
