// https://leetcode.com/problems/minimum-cost-to-connect-sticks/description/
// Difficulty: Medium
// Tags: greedy, heap

// Problem
/*
You have some number of sticks with positive integer lengths. These lengths are given as an array sticks, where sticks[i] is the length of the ith stick.

You can connect any two sticks of lengths x and y into one stick by paying a cost of x + y. You must connect all the sticks until there is only one stick remaining.

Return the minimum cost of connecting all the given sticks into one stick in this way.
*/

// Solution, O(n log n) time, O(n) space
/*
We want to connect small sticks first. For instance if we have sticks 1, 5, and 10. If we connect the 10 first, we have to pay the cost of 10 each future time. So we use a heap, connecting the two smallest sticks, and adding the new stick back in.
*/

class MinHeap {
  constructor(k) {
    this.heap = [null];
    this.maxSize = k;
  }

  remove() {
    if (this.heap.length === 1) {
      return null;
    }

    // replace the first element
    const result = this.heap[1];
    this.heap[1] = this.heap[this.heap.length - 1];
    this.heap.pop();

    let i = 1; // tracks where our element is

    while (true) {
      let smallest = i;
      let left = 2 * i;
      let right = 2 * i + 1;

      // if there is a left child and it's value is smaller, our smallest element will go there
      if (left < this.heap.length && this.heap[left] < this.heap[smallest]) {
        smallest = left;
      }

      // if there is a right child and it's value is smaller than our potentially updated smallest position, our smallest element will go there
      if (right < this.heap.length && this.heap[right] < this.heap[smallest]) {
        smallest = right;
      }

      // if we found a smaller child
      if (smallest !== i) {
        const temp = this.heap[i];
        this.heap[i] = this.heap[smallest];
        this.heap[smallest] = temp;
        i = smallest;
      } else {
        break;
      }
    }

    return result;
  }

  insert(val) {
    this.heap.push(val);
    let i = this.heap.length - 1; // tracks where our element currently is

    // percolate up, while our element is smaller than it's parent
    while (i > 1 && this.heap[i] < this.heap[Math.floor(i / 2)]) {
      const temp = this.heap[i];
      this.heap[i] = this.heap[Math.floor(i / 2)];
      this.heap[Math.floor(i / 2)] = temp;
      i = Math.floor(i / 2);
    }

    // pop if we exceed k elements
    if (this.size() > this.maxSize) {
      this.remove();
    }
  }

  size() {
    return this.heap.length - 1;
  }

  peek() {
    if (this.heap.length === 1) {
      return null;
    }
    return this.heap[1];
  }
}

var connectSticks = function (sticks) {
  const heap = new MinHeap();
  for (const stick of sticks) {
    heap.insert(stick);
  }

  let result = 0;

  // iterate until we make 1 stick
  while (heap.size() > 1) {
    const smallest = heap.remove();
    const secondSmallest = heap.remove();
    const cost = smallest + secondSmallest;
    result += cost;
    heap.insert(smallest + secondSmallest); // add the combined stick back in
  }

  return result;
};
