// https://leetcode.com/problems/remove-duplicates-from-sorted-array/description/
// Difficulty: Easy
// tags: two pointers

// Solution
// O(n) time and O(1) space. Initialize two pointers at the beginning, a read and write pointer. The read pointer reads values and maintains a memo for the last value it has seen. The write pointer overrides values in place as needed. We can use constant storage because the array is sorted so we only need to track the last element we saw to know if read has seen a new element or not.

const removeDuplicates = function (nums) {
  let read = 0;
  let write = 0;
  let memo = Number.NEGATIVE_INFINITY; // outside range of valid numbers to ensure first number read sees is new
  while (read < nums.length) {
    // new number
    if (nums[read] !== memo) {
      memo = nums[read];
      nums[write] = nums[read];
      write++;
      read++;
    }
    // repeat number
    else {
      read++;
    }
  }
  return write;
};

/*  read
    V
   [1, 1, 3, 5, 5]
    ^
read sees a number it hasn't seen before, write writes it, both increment
       V
   [1, 1, 3, 5, 5]
       ^
read sees a number it has seen, so it increments
          V
   [1, 1, 3, 5, 5]
       ^
read sees a new number, so write writes it, and both increment

             V
   [1, 3, 3, 5, 5]
          ^
*/
