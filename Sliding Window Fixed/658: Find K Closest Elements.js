// https://leetcode.com/problems/find-k-closest-elements/description/
// Difficulty: Medium
// Tags: sliding window fixed

// Problem
/*
Simplifed: Find the k closest elements to x. An element is closer if its distance from x is smaller. If the distance is the same, pick the smaller element.

Detailed:
Given a sorted integer array arr, two integers k and x, return the k closest integers to x in the array. The result should also be sorted in ascending order.

An integer a is closer to x than an integer b if:

|a - x| < |b - x|, or
|a - x| == |b - x| and a < b
*/

// Solution
// O(log n + k) time and O(1) space. We could also make it O(log(n-k) + k) time by adjusting the binary search area.
/*
First, locate the closest element to x with binary search. Since we use Math.floor, our searched index is always on the left. This means we can correctly return the left element, or incorrectly return the right element, in an array of length 2. Consider [0, 100] and the target is 1. 0 is too small, so we would return 100. We need to adjust for this by comparing the two values.

After that, just create a sliding window that moves out to the left or right until a window of k is reached.

*/
var findClosestElements = function (arr, k, x) {
  let l = 0;
  let r = arr.length - 1;
  let m = Math.floor((r + l) / 2);
  while (l < r) {
    m = Math.floor((r + l) / 2);
    if (arr[m] >= x) {
      r = m;
    } else if (arr[m] < x) {
      l = m + 1;
    }
  }

  // in case our binary search ended up too big, adjust it
  if (l > 0) {
    if (Math.abs(arr[l - 1] - x) <= Math.abs(arr[l] - x)) {
      l = l - 1;
    }
  }
  // l always points to the closest element now
  let windowL = l;
  let windowR = l;
  while (windowR - windowL + 1 < k) {
    if (windowR === arr.length - 1) {
      windowL--;
    } else if (windowL === 0) {
      windowR++;
    } else {
      const potentialRightDifference = Math.abs(arr[windowR + 1] - x);
      const potentialLeftDifference = Math.abs(arr[windowL - 1] - x);
      if (potentialRightDifference < potentialLeftDifference) {
        windowR++;
      } else {
        windowL--;
      }
    }
  }
  return arr.slice(windowL, windowR + 1);
};

// Solution 2
// O(n) time and O(1) space
// Create a fixed sliding window, increment over the array. Maintain a dp for the sum of all the differences between x and each number in the window. Also maintain a dp for the minimum difference the furthest boundary from x. The k-closest elements can never contain a number that has a bigger difference than our minimum seen difference. But if we have two arrays that have the same biggest difference, we need to check the actual net differences for each element

var findClosestElements = function (arr, k, x) {
  let l = 0;
  let r = k - 1;
  let bestLeft;
  let bestRight;
  let minDistance = Infinity;

  let minimumDifferences = 0;
  for (let i = 0; i < k; i++) {
    const differenceFromX = Math.abs(x - arr[i]);
    minimumDifferences += differenceFromX;
  }

  let currentDifferences = minimumDifferences;

  while (r < arr.length) {
    const furthestDistance = Math.max(
      Math.abs(arr[r] - x),
      Math.abs(arr[l] - x)
    );
    if (furthestDistance < minDistance) {
      bestLeft = l;
      bestRight = r;
      minDistance = furthestDistance;
      minimumDifferences = currentDifferences;
    } else if (furthestDistance === minDistance) {
      if (currentDifferences < minimumDifferences) {
        bestLeft = l;
        bestRight = r;
        minimumDifferences = currentDifferences;
      }
    }
    r++;
    l++;
    currentDifferences += Math.abs(arr[r] - x);
    currentDifferences -= Math.abs(arr[l - 1] - x);
  }
  return arr.slice(bestLeft, bestRight + 1);
};
