// https://leetcode.com/problems/remove-duplicates-from-sorted-array-ii/description/
// Difficulty: Medium
// tags: two pointers

// Solution
// O(n) time and O(1) space. Initialize two pointers at the beginning, a read and a write. Keep a memo for the last element the read pointer has seen, to know if we are seeing a new element or not. If the read pointer sees a new element, write writes, and both increment. If it sees an old element, we check how many times write has seen that and act accordingly.

const removeDuplicates = function (nums) {
  let read = 0;
  let write = 0;
  let memo = Number.NEGATIVE_INFINITY; // a unique number so read sees a new number at the beginning
  let writeSeen = 0;
  while (read < nums.length) {
    // new number
    if (nums[read] !== memo) {
      memo = nums[read];
      nums[write] = nums[read];
      write++;
      read++;
      writeSeen = 1;
    }
    // same number
    else {
      if (writeSeen === 2) {
        read++;
      } else if (writeSeen < 2) {
        nums[write] = nums[read];
        write++;
        read++;
        writeSeen++;
      }
    }
  }
  return write;
};

/* read
    V
   [1, 1, 1, 5, 5, 6]
    ^
    Read sees a new value as per the memo, write pointer has never seen this value, it is the first time, so write updates and both increment, write logs it has seen the current memo once

       V
   [1, 1, 1, 5, 5, 6]
       ^
    read sees the same number as memo, write has seen it once, write updates and they both increment, write has now seen it twice


          V
   [1, 1, 1, 5, 5, 6]
          ^
   Read sees the same number as the memo, but write has already seen it twice, so read increments.


             V
   [1, 1, 1, 5, 5, 6]
          ^
    Read sees a new number, so write updates, they both increment, the memo changes, and the write-seen count gets set to 1


*/
