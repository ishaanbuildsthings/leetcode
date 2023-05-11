// https://leetcode.com/problems/sliding-window-maximum/description/
// Difficulty: Hard
// tags: sliding window fixed

// Problem
/*
Simple explanation: return an array that contains the max for each sliding window of size k

You are given an array of integers nums, there is a sliding window of size k which is moving from the very left of the array to the very right. You can only see the k numbers in the window. Each time the sliding window moves right by one position.

Return the max sliding window.
*/

// Solution
// O(n) time and O(n) space. Use a deque to keep track of the maxes. The deque will always be sorted from largest to smallest. When we add a new element, we remove all elements smaller than it from the back of the deque. When we remove an element, we check if the element is the max, and if it is, we remove it from the front of the deque.

class Deque {
  constructor() {
    // when the head is bigger than the tail, they are crossed, and the deque is empty, otherwise the head and tail point to the head and tail elements
    this.headPosition = 0;
    this.tailPosition = -1;
    this.storage = {};
  }

  enqueueRight(val) {
    this.tailPosition++;
    this.storage[this.tailPosition] = val;
  }

  dequeueRight() {
    // trying to dequeue from an empty queue
    if (this.tailPosition < this.headPosition) {
      return null;
    }

    const value = this.storage[this.tailPosition];
    delete this.storage[this.tailPosition];
    this.tailPosition--;
    return value;
  }

  dequeueLeft() {
    // trying to dequeue from an empty queue
    if (this.tailPosition < this.headPosition) {
      return null;
    }

    const value = this.storage[this.headPosition];
    delete this.storage[this.headPosition];
    this.headPosition++;
    return value;
  }

  peekRight() {
    // trying to peek from an empty queue
    if (this.tailPosition < this.headPosition) {
      return null;
    }
    return this.storage[this.tailPosition];
  }

  peekLeft() {
    // trying to peek from an empty queue
    if (this.tailPosition < this.headPosition) {
      return null;
    }
    return this.storage[this.headPosition];
  }

  size() {
    return this.tailPosition - this.headPosition + 1;
  }
}

/**
 * @param {number[]} nums
 * @param {number} k
 * @return {number[]}
 */
var maxSlidingWindow = function (nums, k) {
  // initialize the deque with the initial sliding window
  const deque = new Deque();

  // populate the deque
  for (let i = 0; i < k; i++) {
    const num = nums[i];

    // if we have an empty deque, always enqueue
    if (deque.size() === 0) {
      deque.enqueueRight(num);
    }
    // if the new number is smaller than or equal to the rightmost number, we cannot remove any other numbs
    else if (num <= deque.peekRight()) {
      deque.enqueueRight(num);
    }
    // if the new number is bigger than the rightmost number, dequeue from the right until it isn't, then enqueue
    else if (num > deque.peekRight()) {
      // we need to keep dequeueing as long as there are numbers left and our number is bigger
      while (deque.size() > 0 && num > deque.peekRight()) {
        deque.dequeueRight();
      }
      deque.enqueueRight(num);
    }
  }

  const result = [];
  let l = 0;
  let r = k - 1;

  while (r < nums.length) {
    // * update result
    // for every window, we add the current biggest element in the window
    result.push(deque.peekLeft());

    // increment the pointers, when we increment from the left, we need to see if that was the biggest element in the window, if it was, dequeue it
    if (deque.peekLeft() === nums[l]) {
      deque.dequeueLeft();
    }
    // * update pointer
    l++;
    r++;

    // * update data (and also a few lines earlier, when we decremented from the left)
    // bring in the new number and determine what to do with it
    const newNum = nums[r];

    // if the new number is monotonically decreasing, we just add it to the queue
    if (newNum <= deque.peekRight()) {
      deque.enqueueRight(newNum);
    }
    // otherwise, dequeue from the right as long as the deck's right number is smaller and there are still numbers, then add it, to make it monotonically decreasing
    else if (newNum > deque.peekRight()) {
      while (deque.size() > 0 && newNum > deque.peekRight()) {
        deque.dequeueRight();
      }
      deque.enqueueRight(newNum);
    }
  }

  return result;
};
