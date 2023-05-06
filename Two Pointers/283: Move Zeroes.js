// Difficulty: Easy
// tags: two pointers, quicksort

// Solution
// O(n) time and O(1) space. Initialize two pointers, one that tracks the position of the first zero in the array, and one that reads tracks the first non-zero. The objective is that whenever we see a non-zero, we want to swap it to the left, with the first zero (as tracked by the other pointer). Once the non-zero pointer reaches the end of the array, we exit the loop. When we increment the non-zero pointer, we must increment it until it is passed the firstZeroPointer, otherwise we would be swapping a zero to the left. Essentially, we need to skip swapping any non-zeroes with zeroes, if the non-zero number is to the left of the first zero. Once we havedo a initialized the firstZero and firstNonZero pointers, it is impossible for the firstZeroPointer to ever get ahead of the firstNonZero pointer, which is important, since if it were ahead, when we do a swap, we would be swapping a zero to the left and a number to the right, but our goal is to move numbers to the left.
// After we swap, we increment the nonZero pointer until we reach a nonZero, but we only need to increment the zeroPointer once. Consider:
/*
  nonZeroPointer
          V
  1 1 0 0 1 0 0 1
      ^
  zeroPointer

  After we swap them, there is another zero next to the zero pointer! But what if there isn't a zero there? Then the nonZeroPointer would be pointing at that instead, and when we do the swap the zeroPointer still only needs to increment once
*/

/* VERY SIMPLIFIED CODE */

function moveZeroes(nums) {
  let l = 0; // in general will point to a 0, but at the start it may point to a 1. This will cause the nonZeroPointer to point to the same thing, a 1, swap them for no reason, then continue. Eventually when the nonZeroPointer reaches a 0, it will skip over it, and the zeroPointer will stay behind at that zero
  for (let r = 0; r < nums.length; r++) {
    // if we found a nonZero, do something, otherwise keep looping
    if (nums[r]) {
      // swap the nonZero with the first zero
      let temp = nums[l];
      nums[l] = nums[r];
      nums[r] = temp;
      // increment the first zero pointer
      l++;
    }
  }
}

const moveZeroes = function (nums) {
  let firstZeroPointer = 0;
  while (nums[firstZeroPointer] !== 0 && firstZeroPointer < nums.length) {
    // if there are no zeroes, we don't want to keep iterating
    firstZeroPointer++;
  }
  // if there are no zeroes found return the original list
  if (firstZeroPointer === nums.length) return nums;

  // the read pointer should start reading from the first non-zero after the firstZeroPointer
  let readPointer = firstZeroPointer;
  while (nums[readPointer] === 0) {
    readPointer++;
  }

  while (readPointer < nums.length) {
    // swap
    nums[firstZeroPointer] = nums[readPointer];
    nums[readPointer] = 0;
    // increment firstZeroPointer, we only need to increment it once, because we are guaranteed to have a 0 at the next position
    firstZeroPointer++;

    // increment the first nonZeroPointer
    while (nums[readPointer] === 0) {
      readPointer++;
    }
  }
};

/*
 pointer for first zero
   V
   0 1 0 3 12
   ^
  read pointer

  read a 0, do nothing, increment

   V
   0 1 0 3 12
     ^
   read a non-zero, so swap it with the first possible zero

   V
   1 0 0 3 12
     ^
  now increment the zero pointer until a zero is found, and increment the read pointer since we processed that cell

     V
   1 0 0 3 12
       ^
    a zero is found, increment

     V
   1 0 0 3 12
         ^
    a non zero is found, swap
     V
   1 3 0 0 12
         ^

    now increment the zero pointer until the first 0 is found, and increment read pointer once

     V
   1 0 0 3 12
            ^
*/

// Solution 2, O(n^2) time due to the nested .splice, which is an O(n) operation

var moveZeroes2 = function (nums) {
  let l = 0;
  let r = nums.length - 1;

  while (l < r) {
    if (nums[l] === 0) {
      nums.splice(l, 1);
      nums.push(0);
      r--;
    } else {
      l++;
    }
  }
  return nums;
};
