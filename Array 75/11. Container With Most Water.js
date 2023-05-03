// https://leetcode.com/problems/container-with-most-water/description/
// Difficulty: Medium
// tags: two pointers

// Solution O(n) time and O(1) space. Initialize two pointers, compute the area and update the max area. Whichever side is smaller should be moved inwards. Moving the bigger side won't do anything since the area is constrainted by the smaller one.

const maxArea = function (heights) {
  let l = 0;
  let r = heights.length - 1;
  let maxArea = 0;
  while (l < r) {
    // compute area
    let minHeight = Math.min(heights[l], heights[r]);
    let distance = r - l;
    let area = minHeight * distance;
    // update area
    maxArea = Math.max(maxArea, area);
    // move a pointer
    if (heights[l] < heights[r]) {
      l++;
    } else {
      r--;
    }
  }
  return maxArea;
};
