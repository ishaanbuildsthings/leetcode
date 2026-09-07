// https://leetcode.com/problems/kth-smallest-element-in-a-sorted-matrix/description/

/*
Given an n x n matrix where each of the rows and columns is sorted in ascending order, return the kth smallest element in the matrix.

Note that it is the kth smallest element in the sorted order, not the kth distinct element.

You must find a solution with a memory complexity better than O(n2).
*/

// Solution, O(k log n) with proper heapify, or n log n without heapify, and O(n) space.
/*
Given the sorted matrix, we can just treat it almost like merging k linked lists (bili style solution). First add n elements to the heap. Then, k times, pop from the heap, and add a new number based on that cell. So our heap also stores coordinates of the number.

Technically, we can also add just the top left element to the heap and start there, I did this for other problem(s). The time complexity is the same though.

We start by adding n elements to the heap (n time if heapify, else n log n time). Then, k times, we pop and add to the heap, so k log n time. The heap stores at most n elements, so n space.
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
      if (
        left < this.heap.length &&
        this.heap[left][0] < this.heap[smallest][0]
      ) {
        smallest = left;
      }

      // if there is a right child and it's value is smaller than our potentially updated smallest position, our smallest element will go there
      if (
        right < this.heap.length &&
        this.heap[right][0] < this.heap[smallest][0]
      ) {
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
    while (i > 1 && this.heap[i][0] < this.heap[Math.floor(i / 2)][0]) {
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

var kthSmallest = function (matrix, k) {
  const WIDTH = matrix[0].length;

  const minHeap = new MinHeap(); // stores [value, row, column]
  for (let r = 0; r < matrix.length; r++) {
    minHeap.insert([matrix[r][0], r, 0]);
  }

  // pop k-1 elements from the heap while adding more, then the smallest is minHeap.peek()
  for (let i = 0; i < k - 1; i++) {
    const [val, r, c] = minHeap.remove();
    if (c + 1 < WIDTH) {
      minHeap.insert([matrix[r][c + 1], r, c + 1]);
    }
  }

  return minHeap.peek()[0];
};
