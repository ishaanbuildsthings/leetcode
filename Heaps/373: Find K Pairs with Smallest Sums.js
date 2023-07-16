// https://leetcode.com/problems/find-k-pairs-with-smallest-sums/description/
// Difficulty: Medium
// Tags: heap

// Problem
/*
You are given two integer arrays nums1 and nums2 sorted in non-decreasing order and an integer k.

Define a pair (u, v) which consists of one element from the first array and one element from the second array.

Return the k pairs (u1, v1), (u2, v2), ..., (uk, vk) with the smallest sums.
*/

// Solution
/*
Another tpical doubly sorted matrix problem. I added the top left element of the matrix to the heap, along with its coordinates. We could also just add the entire left column, but the time complexity is the same. We have at most k elements in the heap, and we do at most k operations on the heap, so the time complexity is O(k log k). The space complexity is O(k).
*/

// stores tuples of [sum, row, col]
class MinHeap {
  constructor() {
    this.heap = [null];
  }

  remove() {
    if (this.heap.length === 1) {
      return null;
    }

    // overwrite the first element with the last
    const result = this.heap[1];
    this.heap[1] = this.heap[this.heap.length - 1];
    this.heap.pop();

    // tracks where our element is
    let i = 1;

    while (true) {
      let smallest = i;
      let left = 2 * i;
      let right = 2 * i + 1;

      if (
        left < this.heap.length &&
        this.heap[left][0] < this.heap[smallest][0]
      ) {
        smallest = left;
      }

      if (
        right < this.heap.length &&
        this.heap[right][0] < this.heap[smallest][0]
      ) {
        smallest = right;
      }

      if (smallest !== i) {
        [this.heap[i], this.heap[smallest]] = [
          this.heap[smallest],
          this.heap[i],
        ];
        i = smallest;
      } else {
        break;
      }
    }

    return result;
  }

  insert(tuple) {
    this.heap.push(tuple);
    let i = this.heap.length - 1;

    while (i > 1 && this.heap[i][0] < this.heap[Math.floor(i / 2)][0]) {
      [this.heap[i], this.heap[Math.floor(i / 2)]] = [
        this.heap[Math.floor(i / 2)],
        this.heap[i],
      ];
      i = Math.floor(i / 2);
    }
  }

  peek() {
    return this.heap[this.heap.length - 1];
  }
}

var kSmallestPairs = function (nums1, nums2, k) {
  const HEIGHT = nums2.length;
  const WIDTH = nums1.length;

  const visited = new Set(); // contains keys for cells we have already seen, indexed by WIDTH * row + col
  visited.add(0); // we have visited the top left cell

  const result = [];

  const heap = new MinHeap(); // stores the smallest values in a tuple, along with their coordinates
  heap.insert([nums1[0] + nums2[0], 0, 0]);

  while (result.length < k) {
    // sometimes k can be less than the total number of pairs, weird edge case
    if (heap.peek() === null) {
      return result;
    }

    const [_, row, col] = heap.remove();
    result.push([nums1[col], nums2[row]]);

    // if the bottom cell is in range, and not visited, add it to the heap and mark it as visited
    if (row + 1 < HEIGHT && !visited.has(WIDTH * (row + 1) + col)) {
      heap.insert([nums2[row + 1] + nums1[col], row + 1, col]);
      visited.add(WIDTH * (row + 1) + col);
    }

    // if the right cell is in range, and not visited, add it to the heap and mark it as visited
    if (col + 1 < WIDTH && !visited.has(WIDTH * row + col + 1)) {
      heap.insert([nums2[row] + nums1[col + 1], row, col + 1]);
      visited.add(WIDTH * row + col + 1);
    }
  }

  return result;

  /*
          3,    10,    11


    2    5      12    13

    4    7      40    44

    6    9      16    17



    5 is always initially the smallest, we seed the result: [5]. now we must consider two neighbors, 7 and 12. 7 is smaller. 7 is smaller, so we will add 7 to our result, and add 12 to the heap.

    result: 5, 7
    heap: 12

    at 7, we have two neighbors, 9, and 40. 9 is smaller than 40, and the heap. we add 9 to the result, and 40 to the heap:

    result: 5, 7, 9
    heap: 12, 40

    at 9, we have one neighbor, 16. 16 is larger than the heap. we add 16 to the heap, and add the heap element to the result:

    result: 5, 7, 9, 12
    heap: 16, 40

    at 12, we have neighbors 13 and 40. 13 is smallest. We don't add 40 because it's already visited.

    result: 5, 7, 9, 12, 13
    heap: 16, 40

    At 13, we have neighbor 44. heap is smaller.

    result: 5, 7, 9, 12, 13, 16
    heap: 40, 44

    at 16, we have neighbor 17, it is smaller than heap.
    result: 5, 7, 9, 12, 13, 16, 17
    heap: 40, 44

    at 17, we have no neighbor, but 40 and 44 in the heap.

    */
};
