// https://leetcode.com/problems/kth-largest-element-in-a-stream/description/
// Difficulty: Easy
// tags: heap

// Problem
/*
Design a class to find the kth largest element in a stream. Note that it is the kth largest element in the sorted order, not the kth distinct element.

Implement KthLargest class:

KthLargest(int k, int[] nums) Initializes the object with the integer k and the stream of integers nums.
int add(int val) Appends the integer val to the stream and returns the element representing the kth largest element in the stream.
*/

// Solution
// Time: O(n log k) time to construct. Each time we add an element to the heap, it takes log k time, since our heap has k elements. If we ever exceed k, we spend log k time popping from the heap. To add a new element, it takes O(log k) time, since the heap has k elements.

var KthLargest = function (k, nums) {
  this.heap = [null]; // 2i and 2i + 1. minheap

  this.pop = () => {
    // replace the first element of the heap with the last, then remove the last element
    this.heap[1] = this.heap[this.heap.length - 1];
    this.heap.pop(); // normal pop

    let i = 1; // tracks our current element
    // while we are bigger than at least one child, but have two, bubble to the smaller one
    while (
      (this.heap[i] > this.heap[2 * i] ||
        this.heap[i] > this.heap[2 * i + 1]) &&
      this.heap[2 * i] !== undefined &&
      this.heap[2 * i + 1] !== undefined
    ) {
      // if the left is smaller, bubble down there
      if (this.heap[2 * i] < this.heap[2 * i + 1]) {
        const temp = this.heap[2 * i];
        this.heap[2 * i] = this.heap[i];
        this.heap[i] = temp;
        i = 2 * i;
      }
      // otherwise bubble to the right
      else {
        const temp = this.heap[2 * i + 1];
        this.heap[2 * i + 1] = this.heap[i];
        this.heap[i] = temp;
        i = 2 * i + 1;
      }
    }

    // while we are bigger than just the left child, bubble there (when we no longer have two children)
    while (this.heap[i] > this.heap[2 * i]) {
      const temp = this.heap[2 * i];
      this.heap[2 * i] = this.heap[i];
      this.heap[i] = temp;
      i = 2 * i;
    }
  };

  this.push = (val) => {
    this.heap.push(val); // normal push
    let i = this.heap.length - 1;
    while (i > 1 && this.heap[i] < this.heap[Math.floor(i / 2)]) {
      const temp = this.heap[Math.floor(i / 2)];
      this.heap[Math.floor(i / 2)] = this.heap[i];
      this.heap[i] = temp;
      i = Math.floor(i / 2);
    }

    // if we are above k elements, pop
    if (this.heap.length > k + 1) {
      this.pop();
    }
  };

  // populate the heap
  for (const num of nums) {
    this.push(num);
  }
};

KthLargest.prototype.add = function (val) {
  this.push(val);
  return this.heap[1];
};
