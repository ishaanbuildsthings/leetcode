// https://leetcode.com/problems/find-median-from-data-stream/description/
// Difficulty: Hard
// tags: heap

// Problem
/*
Simplified:
We receive a stream of data, at any point we need to either add a data point, or find the median of our current data.

Detailed:
The median is the middle value in an ordered integer list. If the size of the list is even, there is no middle value, and the median is the mean of the two middle values.

For example, for arr = [2,3,4], the median is 3.
For example, for arr = [2,3], the median is (2 + 3) / 2 = 2.5.
Implement the MedianFinder class:

MedianFinder() initializes the MedianFinder object.
void addNum(int num) adds the integer num from the data stream to the data structure.
double findMedian() returns the median of all elements so far. Answers within 10-5 of the actual answer will be accepted.
 */

// Solution, O(1) time to find median, O(log (n/2)) (I think this cannot be simplified) time to add an element.
/*
Maintain two heaps, a smallest half (max heap) and largest half (min heap).

Compare the new element to the largest from the bottom half, if it is smaller, add it to the bottom, else the top.

If the difference in heap sizes is 2, we rebalance.
*/

class MinHeap {
  constructor() {
    this.heap = [null];
  }

  insert(val) {
    this.heap.push(val);
    let i = this.heap.length - 1; // tracks where our element is
    // percolate up
    while (i > 1) {
      const parent = Math.floor(i / 2);
      // if the parent is bigger, move up
      if (this.heap[parent] > this.heap[i]) {
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
    let smallest = i;
    while (true) {
      const left = smallest * 2;
      const right = smallest * 2 + 1;

      if (left < this.heap.length && this.heap[left] < this.heap[smallest]) {
        smallest = left;
      }

      if (right < this.heap.length && this.heap[right] < this.heap[smallest]) {
        smallest = right;
      }

      if (smallest === i) {
        break;
      }

      // swap the parent element with the new smallest
      [this.heap[i], this.heap[smallest]] = [this.heap[smallest], this.heap[i]];

      i = smallest;
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

// ______________________________________________________________________________________________________

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

// ____________________________________________________________________________________________________________

var MedianFinder = function () {
  this.minHeap = new MinHeap(); // tracks the largest half
  this.maxHeap = new MaxHeap(); // tracks the smallest half
};

/**
 * @param {number} num
 * @return {void}
 */
MedianFinder.prototype.addNum = function (num) {
  const bottomMedian = this.maxHeap.peek();
  // if our number is smaller than the bottom half cutoff, add it to the bottom half
  if (num <= bottomMedian || bottomMedian === undefined) {
    this.maxHeap.insert(num);
  } else {
    this.minHeap.insert(num);
  }

  // if our minheap became too big then we need to resize, otherwise we wouldn't get the median, same with maxheap. there must always be a difference of at most one
  if (this.minHeap.size() - 2 === this.maxHeap.size()) {
    const addToMaxHeap = this.minHeap.remove();
    this.maxHeap.insert(addToMaxHeap);
  } else if (this.maxHeap.size() - 2 === this.minHeap.size()) {
    const addToMinHeap = this.maxHeap.remove();
    this.minHeap.insert(addToMinHeap);
  }
};

/**
 * @return {number}
 */
MedianFinder.prototype.findMedian = function () {
  const totalElementsInserted = this.minHeap.size() + this.maxHeap.size();
  // if we have an even amount of elements, the median is the largest from the bottom half, plus the smallest from the top half. we don't worry about the heap sizes for even, since they never differ by more than one (and they can't differ by one since the total size is even)
  if (totalElementsInserted % 2 === 0) {
    return (this.minHeap.peek() + this.maxHeap.peek()) / 2;
  }
  /* here, the heap sizes differ by one */
  if (this.minHeap.size() > this.maxHeap.size()) {
    return this.minHeap.peek();
  }

  return this.maxHeap.peek();
};

/**
 * Your MedianFinder object will be instantiated and called as such:
 * var obj = new MedianFinder()
 * obj.addNum(num)
 * var param_2 = obj.findMedian()
 */
