// https://leetcode.com/problems/largest-rectangle-in-histogram/
// Difficulty: Hard
// tags: stack

// Problem
/*
Given an array of integers heights representing the histogram's bar height where the width of each bar is 1, return the area of the largest rectangle in the histogram.
*/

// Solution 2, O(n^2) time and O(1) space. Iterate over the histogram, and for each point, iterate a second variable. At each step, determine the height constraint, calculate the max area with those boundaries, and update the global max area. Gets TLE.

var largestRectangleArea = function (heights) {
  let maxArea = 0;
  for (let i = 0; i < heights.length; i++) {
    // initialize default values
    let heightConstraint = Number.POSITIVE_INFINITY;
    let currentArea;
    for (let j = i; j < heights.length; j++) {
      heightConstraint = Math.min(heightConstraint, heights[j]);
      currentWidth = j - i + 1;
      currentArea = heightConstraint * currentWidth;
      maxArea = Math.max(maxArea, currentArea);
    }
  }
  return maxArea;
};

/* i:  V
      [2, 1, 5, 6, 2, 3]
       ^
We start from the beginning, heightConstraint=2, width=1, area=2, maxarea=2
we then increment j


       V
      [2, 1, 5, 6, 2, 3]
          ^
heightConstraint lowered to 1, width=2, area=2, maxarea = 2
increment j again


       V
      [2, 1, 5, 6, 2, 3]
             ^
heightConstraint still 1, width=3, area=3, maxarea=3
... until j reaches the end, then i increments



          V
      [2, 1, 5, 6, 2, 3]
          ^
heightConstraint=1, width=1, area=1, maxarea=6(from before)

*/
