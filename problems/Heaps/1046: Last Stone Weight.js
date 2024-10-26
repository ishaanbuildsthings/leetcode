// https://leetcode.com/problems/last-stone-weight/description/
// Difficulty: Easy
// tags: heap

// Problem
/*
You are given an array of integers stones where stones[i] is the weight of the ith stone.

We are playing a game with the stones. On each turn, we choose the heaviest two stones and smash them together. Suppose the heaviest two stones have weights x and y with x <= y. The result of this smash is:

If x == y, both stones are destroyed, and
If x != y, the stone of weight x is destroyed, and the stone of weight y has new weight y - x.
At the end of the game, there is at most one stone left.

Return the weight of the last remaining stone. If there are no stones left, return 0.
*/

// Solution, O(n log n) time as each insertion and removal takes log n time. O(n) space for the heap.
/*
Implement a max heap. The idea is we need to be able to grab the largest stones quickly. We smash them, produce a new stone, and add it to the heap. We can't do a linear solution, because when we smash the biggest stones, we need to insert the small stone back in, which takes O(n) time to add it to a sorted array, which would result in n^2 total time. Instead, we use a log n heap solution. Whenever we process two stones, we're guaranteed to be left with at most 1 stone, so we only need to do the log n operation up to n times.
*/

class MaxHeap {
  constructor() {
    this.heap = [null];
  }

  hPush(val) {
    this.heap.push(val);
    let i = this.heap.length - 1;
    // percolate up
    while (i > 1 && this.heap[i] > this.heap[Math.floor(i / 2)]) {
      const temp = this.heap[Math.floor(i / 2)];
      this.heap[Math.floor(i / 2)] = this.heap[i];
      this.heap[i] = temp;
      i = Math.floor(i / 2);
    }
  }

  hPop() {
    // we have no values in an empty heap
    if (this.heap.length === 1) {
      return null;
    }

    // memoize the value for later as we will remove it
    const result = this.heap[1];

    const lastValue = this.heap[this.heap.length - 1];
    this.heap[1] = lastValue;
    this.heap.pop(); // remove the last value from the end

    let i = 1;

    // while we have both children, and at least one is bigger, percolate to the bigger one
    while (
      this.heap[2 * i] !== undefined &&
      this.heap[2 * i + 1] !== undefined &&
      (this.heap[2 * i] > this.heap[i] || this.heap[2 * i + 1] > this.heap[i])
    ) {
      // percolate left
      if (this.heap[2 * i] >= this.heap[2 * i + 1]) {
        const temp = this.heap[2 * i];
        this.heap[2 * i] = this.heap[i];
        this.heap[i] = temp;
        i = 2 * i;
      }
      // percolate right
      else if (this.heap[2 * i + 1] > this.heap[2 * i]) {
        const temp = this.heap[2 * i + 1];
        this.heap[2 * i + 1] = this.heap[i];
        this.heap[i] = temp;
        i = 2 * i + 1;
      }
    }

    // if we just have a left child at the end, percolate left if needed
    if (this.heap[2 * i] !== undefined) {
      if (this.heap[2 * i] > this.heap[i]) {
        const temp = this.heap[2 * i];
        this.heap[2 * i] = this.heap[i];
        this.heap[i] = temp;
      }
    }

    return result;
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

var lastStoneWeight = function (stones) {
  const maxHeap = new MaxHeap();
  for (const stone of stones) {
    maxHeap.hPush(stone);
  }

  while (maxHeap.size() > 1) {
    const stone1 = maxHeap.hPop();
    const stone2 = maxHeap.hPop();
    const difference = Math.abs(stone1 - stone2);
    // if the stones break each other, they don't produce another stone
    if (difference === 0) {
      continue;
    }

    // if the stones don't break each other, they produce another stone
    maxHeap.hPush(difference);
  }

  return maxHeap.peek() ? maxHeap.peek() : 0;
};
