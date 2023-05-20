// https://leetcode.com/problems/largest-rectangle-in-histogram/
// Difficulty: Hard
// tags: stack

// Problem
/*
Given an array of integers heights representing the histogram's bar height where the width of each bar is 1, return the area of the largest rectangle in the histogram.
*/

// Solution 1, O(n) time and O(n) space.
/*
 */

var largestRectangleArea = function (heights) {
  let maxArea = -Infinity;

  const stack = []; // it will be monotonically increasing, as soon as we see a smaller rectangle, we know our large rectangle is cut off

  for (let i = 0; i < heights.length; i++) {
    // for every element, we need to track how many elements it has popped off
    /*
         say we have [ [4, 2], [6, 0] ], meaning the 4 previouly popped off two elements bigger than 4, so it can extend to the left by 2.
         Now a [2, 0] comes along, and pops the 6 off. The 6 has a width. The number of elements it has popped off to the left (0), itself (1), and the number of elements to the right that are being popped off, which is 0, as the [2, 0] hasn't popped anything off. So area = 6 * (0 + 1 + 0) = 6.
         Now we have [ [4, 2], [2, 1] ]
         But the 2 can also pop off the 4. The 2 also notably popped off 1 element bigger than the 4 (it must have been bigger due to the monotonic increasing nature). So our 4 can extend left by two, and right by 1, making the area 4*(2 + 1 + 1) = 16.

         The two now pops off the 4, but the 2 could also beat even more elements to the left, as indicated by how many the 4 beat, so we add those, along with beating the 4 itself
         [ [2, 4] ]
         In a way, biggerOnLeftOfNewcomer sort of acts like a dp/recursion. It starts at 0, and if it pops an element, it adds that count. Then any element that's more left can also be beaten, we will factor that in. If an element had already beaten some, like [2,0] [5,2], which might happen when we do [2,0] [10,0] [10,0], then we add a 5, those 10s that were bigger than 2 get stored inside the 5. 5 cannot pop the 2, but eventually when something pops the 2 by bottlenecking it, the 2 will see the number on the right.
         */
    let biggerOnLeftOfNewcomer = 0;
    while (stack.length > 0 && heights[i] < stack[stack.length - 1][0]) {
      const tuple = stack.pop();
      const height = tuple[0];
      const area = height * (tuple[1] + 1 + biggerOnLeftOfNewcomer);
      maxArea = Math.max(maxArea, area);
      biggerOnLeftOfNewcomer++; // for the element we just beat
      biggerOnLeftOfNewcomer += tuple[1]; // for the elements that element had already beaten
    }
    stack.push([heights[i], biggerOnLeftOfNewcomer]);
  }

  let totalPopped = 0;
  for (let i = stack.length - 1; i >= 0; i--) {
    const tuple = stack[i];
    totalPopped += tuple[1];
    const height = tuple[0];
    const numToRight = stack.length - (i + 1);
    const width = totalPopped + 1 + numToRight;
    const area = height * width;
    maxArea = Math.max(maxArea, area);
  }

  return maxArea;
};

// 7 6 5 4 3

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
