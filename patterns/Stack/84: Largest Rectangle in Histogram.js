// https://leetcode.com/problems/largest-rectangle-in-histogram/
// Difficulty: Hard
// tags: stack, monotonic stack

// Problem
/*
Given an array of integers heights representing the histogram's bar height where the width of each bar is 1, return the area of the largest rectangle in the histogram.
*/

// Solution 1, O(n) time and O(n) space.
/*
Iterate over the heights. Maintain a strictly increasing stack. Our goal is to determine the height of n rectangles, where each rectangle takes on the height of one specific height. For instance: [1, 5, 8, 4, 3], we should see how big the rectangle at height 1 is, 4, 7, 3, and 2. It doesn't make sense to check shorter ones, like height 2, because they will be subsets of potentially larger ones. If we checked height 3, it would line up with another constraint already (the height 3 at the end). If we see a smaller rectangle, for instance the 4, it should pop until we are increasing again, tracking how many it popped, so we know how many bigger ones are to its left. When we pop off an element, compute its area. For instance the 5 has height 5, width (0 + 1 + 1), as it had popped off 0 elements to its left, has width of 1 itself, and the 4 had popped off 1 element to its right. At the end we have a monotonically increasing stack so we need to compute that.
 */
// Solution 2, slightly easier to implement:
/*
Maintain a stack of [index, height]. [2, 1, 5, 6, 2, 3]. We add 2 that started at index 0. We add a 1, that is at index 1. But it can extend left, all the way to where the 2 started. So we can add [index=0, height=1] for the height of 1. Then we add [index=2,height=5], [index=3,height=6]. Then at 2, we pop the 6, calculate the 6 area. We pop the 5, calculate the area by using our current index for the 2 (index 4) and the index of the 5 (2). We can't pop anymore so we update that our new 2 ends at index 2 which is where the 5 ended. At the end we have a monotonically increasing stack so we need to compute that.
*/
// Solution 3, I rewrote this later in python, we don't need the "kill" counter. Instead, when an element on the right is small and pops us, we know our right cutoff. The left cutoff is always just the element directly to the left. For instance: 1 5 10 3. The 3 pops the 10. When the 3 pops the 5, the 5 knows it can go up to (but not including) the 3, we don't track the "kills". I store just indices in the stack. Also I added a 0 at the end of the heights to clean up the remaining stack at the end. I prepended a -1 to the stack which helps calculate the left boundary in the chance we don't have an element on the left normally. Code is at the bottom.

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

// Solution 3
// class Solution:
//     def largestRectangleArea(self, heights: List[int]) -> int:
//         heights.append(0)
//         stack = [-1]
//         ans = 0
//         for i in range(len(heights)):
//             while heights[i] < heights[stack[-1]]:
//                 h = heights[stack.pop()]
//                 w = i - 1 - stack[-1]
//                 ans = max(ans, h * w)
//             stack.append(i)
//         heights.pop() # clear out the 0, we could have just used a copied array too if we wanted
//         return ans
