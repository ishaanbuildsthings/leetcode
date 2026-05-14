// https://leetcode.com/problems/minimum-operations-to-halve-array-sum/description/
// difficulty: Medium
// tags: heap

// Problem
/*
You are given an array nums of positive integers. In one operation, you can choose any number from nums and reduce it to exactly half the number. (Note that you may choose this reduced number in future operations.)

Return the minimum number of operations to reduce the sum of nums by at least half.
*/

// Solution, O(n log n) time, O(n) space
/*
Just simulate it, pull a number, halve it, then add it back. I also spent n log n time doing a fake heapify but it could be done in linear time. In the worst case (all elements are the same), we halve each element once, so n log n time.
*/

class MaxHeap {
  constructor() {
    this.heap = [null];
  }

  insert(val) {
    this.heap.push(val);
    let i = this.heap.length - 1; // tracks where our element is
    // percolate up
    while (i > 1) {
      const parent = Math.floor(i / 2);
      // if the parent is smaller, move up
      if (this.heap[parent] < this.heap[i]) {
        const temp = this.heap[parent];
        this.heap[parent] = this.heap[i];
        this.heap[i] = temp;
        i = parent;
      } else {
        break;
      }
    }
  }

  remove() {
    if (this.heap.length === 1) {
      return undefined;
    }

    const result = this.heap[1];
    // overwrite the first element with the last
    this.heap[1] = this.heap[this.heap.length - 1];
    this.heap.pop();

    // percloate down
    let i = 1; // tracks where our element is
    let largest = i;
    while (true) {
      const left = largest * 2;
      const right = largest * 2 + 1;

      if (left < this.heap.length && this.heap[left] > this.heap[largest]) {
        largest = left;
      }

      if (right < this.heap.length && this.heap[right] > this.heap[largest]) {
        largest = right;
      }

      if (largest === i) {
        break;
      }

      // swap the parent element with the new largest
      [this.heap[i], this.heap[largest]] = [this.heap[largest], this.heap[i]];

      i = largest;
    }

    return result;
  }

  size() {
    return this.heap.length - 1;
  }

  peek() {
    if (this.heap.length === 1) {
      return undefined;
    }
    return this.heap[1];
  }
}

var halveArray = function (nums) {
  const heap = new MaxHeap();
  for (const num of nums) {
    heap.insert(num);
  }

  const totalSum = nums.reduce((acc, val) => acc + val, 0);
  let amountStillInNums = totalSum;

  let result = 0;

  while (amountStillInNums > totalSum / 2) {
    result++;
    const biggestNum = heap.remove();
    heap.insert(biggestNum / 2);
    amountStillInNums -= biggestNum / 2;
  }

  return result;
};
