// https://leetcode.com/problems/k-closest-points-to-origin/description/
// tags: heap, quicksort

// TODO: quicksort

// Problem
/*
Simplified:
You are given n points [x, y]. Return the k closest points to the origin in any order.

Detailed:
Given an array of points where points[i] = [xi, yi] represents a point on the X-Y plane and an integer k, return the k closest points to the origin (0, 0).

The distance between two points on the X-Y plane is the Euclidean distance (i.e., √(x1 - x2)2 + (y1 - y2)2).

You may return the answer in any order. The answer is guaranteed to be unique (except for the order that it is in).
*/

// Solution 1, O(n log k) time and O(n) space.
/*
Maintain a max heap of size k. We track the k smallest elements, and have quick access to the largest of those. For every element in n, add it to the heap. If we exceed the size ever, we pop the largest element out of the heap. Then return what the heap contains. The heap also contains distances to the origin, so we know how to sort in the heap, but also the points themselves so we know what to return.
*/
// * Solution 2, O(n log n) time and O(sort) space. Just sort the array, then return the k closest.

// this heap stores tuples [distance, [x, y]], and ranks the points by distance
class MaxHeapMap {
  constructor(maxSize) {
    this.heap = [null];
    this.size = 0;
    this.maxSize = maxSize;
  }

  hPush(tuple) {
    this.heap.push(tuple);
    this.size++;
    let i = this.heap.length - 1; // where we inserted val into, tracks where our element is
    // percolate up while our element is bigger
    while (i > 1 && this.heap[Math.floor(i / 2)][0] < this.heap[i][0]) {
      [this.heap[i], this.heap[Math.floor(i / 2)]] = [
        this.heap[Math.floor(i / 2)],
        this.heap[i],
      ];
      i = Math.floor(i / 2);
    }

    if (this.size > this.maxSize) {
      this.hPop();
    }
  }

  hPop() {
    if (this.size === 0) {
      return null;
    }

    // replace the beginning with the end
    this.heap[1] = this.heap[this.heap.length - 1];
    this.heap.pop();

    let i = 1; // tracks where our current element is
    // while we have both children (2*i + 1 in range means 2*i will also be)
    // percolate down as our element is smaller
    while (2 * i + 1 < this.heap.length) {
      // if the left child is bigger than the right, and bigger than our element, percolate the element down
      if (
        this.heap[2 * i][0] >= this.heap[2 * i + 1][0] &&
        this.heap[2 * i][0] > this.heap[i][0]
      ) {
        [this.heap[2 * i], this.heap[i]] = [this.heap[i], this.heap[2 * i]];
        i = 2 * i;
      }
      // if the right child is bigger than the left and bigger than our element
      else if (
        this.heap[2 * i + 1][0] > this.heap[2 * i][0] &&
        this.heap[2 * i + 1][0] > this.heap[i][0]
      ) {
        [this.heap[2 * i + 1], this.heap[i]] = [
          this.heap[i],
          this.heap[2 * i + 1],
        ];
        i = 2 * i + 1;
      }
      // if neither child is bigger, we stop
      else {
        break;
      }
    }

    // if we have one child, it means we have one last left child to check
    if (2 * i < this.heap.length) {
      if (this.heap[2 * i][0] > this.heap[i][0]) {
        [this.heap[2 * i], this.heap[i]] = [this.heap[i], this.heap[2 * i]];
      }
    }

    this.size--;
  }

  getCoords() {
    return this.heap.slice(1).map((tuple) => tuple[1]);
  }
}

var kClosest = function (points, k) {
  const heap = new MaxHeapMap(k);
  for (const coords of points) {
    const distance = getDistance(coords);
    heap.hPush([distance, coords]);
  }

  return heap.getCoords();
};

function getDistance(coords) {
  const [x, y] = coords;
  return Math.sqrt(x * x + y * y);
}

// Solution 2, O(n log n). Get tuples with the distances and coordinates of everything, sort by distance, and return the first k coordinates.
// * Solution 3 is a more succinct version because it sorts the actual input.

var kClosest = function (points, k) {
  /*
        contains [ [distance, [x, y]], [distance, [x, y]] ]
        so we can sort the array by distance, then return a mapping of the tupples
    */
  const data = [];

  for (let i = 0; i < points.length; i++) {
    const tuple = points[i];
    const distance = getDistance(tuple);
    const datum = [distance, tuple];
    data.push(datum);
  }

  data.sort((a, b) => a[0] - b[0]);

  const result = [];
  for (let i = 0; i < k; i++) {
    result.push(data[i][1]);
  }

  return result;
};

function getDistance(coords) {
  const [x, y] = coords;
  return Math.sqrt(x * x + y * y);
}

// Solution 3, mutating the input array.

var kClosest = function (points, k) {
  points.sort((a, b) => getDistance(a) - getDistance(b));
  return points.slice(0, k);
};

function getDistance(coords) {
  const [x, y] = coords;
  return Math.sqrt(x * x + y * y);
}
