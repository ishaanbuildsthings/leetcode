// https://leetcode.com/problems/total-cost-to-hire-k-workers/description/
// Difficulty: Medium
// tags: heap

// Problem
/*
Example:

Input: costs = [17,12,10,2,7,2,11,20,8], k = 3, candidates = 4
Output: 11
Explanation: We hire 3 workers in total. The total cost is initially 0.
- In the first hiring round we choose the worker from [17,12,10,2,7,2,11,20,8]. The lowest cost is 2, and we break the tie by the smallest index, which is 3. The total cost = 0 + 2 = 2.
- In the second hiring round we choose the worker from [17,12,10,7,2,11,20,8]. The lowest cost is 2 (index 4). The total cost = 2 + 2 = 4.
- In the third hiring round we choose the worker from [17,12,10,7,11,20,8]. The lowest cost is 7 (index 3). The total cost = 4 + 7 = 11. Notice that the worker with index 3 was common in the first and last four workers.
The total hiring cost is 11.

Detailed:
You are given a 0-indexed integer array costs where costs[i] is the cost of hiring the ith worker.

You are also given two integers k and candidates. We want to hire exactly k workers according to the following rules:

You will run k sessions and hire exactly one worker in each session.
In each hiring session, choose the worker with the lowest cost from either the first candidates workers or the last candidates workers. Break the tie by the smallest index.
For example, if costs = [3,2,7,7,1,2] and candidates = 2, then in the first hiring session, we will choose the 4th worker because they have the lowest cost [3,2,7,7,1,2].
In the second hiring session, we will choose 1st worker because they have the same lowest cost as 4th worker but they have the smallest index [3,2,7,7,2]. Please note that the indexing may be changed in the process.
If there are fewer than candidates workers remaining, choose the worker with the lowest cost among them. Break the tie by the smallest index.
A worker can only be chosen once.
Return the total cost to hire exactly k workers.
*/

// Solution, O(c log c + k log c) time, or O(c + k log c) time with proper heapify. O(n) space. c = candidates, n = total length of the array.
/*
Maintain a left min heap and a right min heap, so we can easily check the smallest from each size. Take out the smallest, then increment the heap, if they don't overlap.

We initially fill the heaps in c log c time, as the heaps are max size of c, and we add c elements. Worst case is we sift up c/2 leaf nodes in log c time. We can heapify instead, but I was lazy.

Then, for each hire, k, we do a log c operation to remove that candidate / add a new one if needed.
*/

class minHeap {
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

var totalCost = function (costs, k, candidates) {
  // if candidates is big enough to encompass all people, we just take the k smallesst people
  if (candidates * 2 >= costs.length) {
    const heap = new minHeap(costs.length);
    for (const cost of costs) {
      heap.insert(cost);
    }

    let result = 0;
    // hire k candidates
    for (let i = 0; i < k; i++) {
      const smallest = heap.remove();
      result += smallest;
    }

    return result;
  }

  // if we need two separate regions
  const leftHeap = new minHeap(candidates);
  const rightHeap = new minHeap(candidates);

  // fill heaps
  for (let i = 0; i < candidates; i++) {
    leftHeap.insert(costs[i]);
  }
  for (let i = costs.length - 1; i > costs.length - 1 - candidates; i--) {
    rightHeap.insert(costs[i]);
  }

  // as we hire from the left or right, stop incrementing the heaps if they will overlap
  let rightmostLeftHeapPointer = candidates - 1;
  let leftmostRightHeapPointer = costs.length - candidates;

  let result = 0;

  // hire k candidates
  for (let i = 0; i < k; i++) {
    let leftSmallest = leftHeap.peek() === null ? Infinity : leftHeap.peek(); // if a heap is empty, we say it's value is infinity, so we never consider that element
    let rightSmallest = rightHeap.peek() === null ? Infinity : rightHeap.peek();

    if (leftSmallest <= rightSmallest) {
      result += leftSmallest;
      leftHeap.remove();
      // if we can increment for the left heap, do so
      if (rightmostLeftHeapPointer + 1 < leftmostRightHeapPointer) {
        rightmostLeftHeapPointer++;
        leftHeap.insert(costs[rightmostLeftHeapPointer]);
      }
    } else {
      result += rightSmallest;
      rightHeap.remove();
      // if we can decrement for the right heap, do so
      if (leftmostRightHeapPointer - 1 > rightmostLeftHeapPointer) {
        leftmostRightHeapPointer--;
        rightHeap.insert(costs[leftmostRightHeapPointer]);
      }
    }
  }

  return result;
};
