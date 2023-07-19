// https://leetcode.com/problems/minimum-difference-in-sums-after-removal-of-elements/description/
// Difficulty: Hard
// Tags: heaps, avl tree

// Problem
/*
You are given a 0-indexed integer array nums consisting of 3 * n elements.

You are allowed to remove any subsequence of elements of size exactly n from nums. The remaining 2 * n elements will be divided into two equal parts:

The first n elements belonging to the first part and their sum is sumfirst.
The next n elements belonging to the second part and their sum is sumsecond.
The difference in sums of the two parts is denoted as sumfirst - sumsecond.

For example, if sumfirst = 3 and sumsecond = 2, their difference is 1.
Similarly, if sumfirst = 2 and sumsecond = 3, their difference is -1.
Return the minimum difference possible between the sums of the two parts after the removal of n elements.
*/

// Solution, O(n log n) time, O(n) space
/*
Given we have 3n elements, say: [0, 1, 2, 3, 4, 5]

Clearly we need at least n elements in the left and right region. For instance:
0, 1 | 2, 3, 4, 5
0, 1, 2 | 3, 4, 5
0, 1, 2, 3 | 4, 5

Where at each split point, we have to remove the largest elements from the left, and the smallest elements from the right.

To remove the smallest elements from the left, we can just maintain a heap, and as we increment the split point, find the new smallest element. We also track the running sum of smallest elements, and the running sum of the entire left region, to determine how to maximize the left region.

For the right region, it is a bit trickier. For instance if we had a heap of all the initial elements, as we increment the split point, we need to remove an element from the data first, then see the sum of the remaining largest elements. I ended up using an avl tree because I thought I needed the remove(val) function. But actually, we can use another heap, and preprocess data, kind of like a suffix list.
*/

class Node {
  constructor(value) {
    this.value = value;
    this.height = 1; // height of node in tree
    this.count = 1; // count of duplicates
    this.left = null;
    this.right = null;
  }
}

class AVLTree {
  constructor() {
    this.root = null;
  }

  // Insert a value into the tree
  insert(value) {
    this.root = this._insert(this.root, value);
  }

  _insert(node, value) {
    // Perform standard BST insert
    if (node === null) {
      return new Node(value);
    }

    if (value < node.value) {
      node.left = this._insert(node.left, value);
    } else if (value > node.value) {
      node.right = this._insert(node.right, value);
    } else {
      // handle duplicate value
      node.count++;
      return node;
    }

    // Update height
    node.height =
      1 + Math.max(this._getHeight(node.left), this._getHeight(node.right));

    // Rebalance tree
    let balance = this._getBalance(node);
    if (balance > 1 && value < node.left.value) {
      return this._rotateRight(node);
    }
    if (balance < -1 && value > node.right.value) {
      return this._rotateLeft(node);
    }
    if (balance > 1 && value > node.left.value) {
      node.left = this._rotateLeft(node.left);
      return this._rotateRight(node);
    }
    if (balance < -1 && value < node.right.value) {
      node.right = this._rotateRight(node.right);
      return this._rotateLeft(node);
    }

    return node;
  }

  // Remove a value from the tree
  remove(value) {
    this.root = this._remove(this.root, value);
  }

  // For simplicity, removal of duplicate values isn't fully handled here
  _remove(node, value) {
    // Standard BST removal
    if (node === null) {
      return node;
    }

    if (value < node.value) {
      node.left = this._remove(node.left, value);
    } else if (value > node.value) {
      node.right = this._remove(node.right, value);
    } else {
      // handle removing duplicate or unique value
      if (node.count > 1) {
        node.count--;
        return node;
      } else if (!node.left) {
        node = node.right;
      } else if (!node.right) {
        node = node.left;
      } else {
        let temp = this._minValueNode(node.right);
        node.value = temp.value;
        node.right = this._remove(node.right, temp.value);
      }
    }

    if (node === null) return node;

    // Update height
    node.height =
      1 + Math.max(this._getHeight(node.left), this._getHeight(node.right));

    // Rebalance tree
    let balance = this._getBalance(node);
    if (balance > 1 && this._getBalance(node.left) >= 0) {
      return this._rotateRight(node);
    }
    if (balance < -1 && this._getBalance(node.right) <= 0) {
      return this._rotateLeft(node);
    }
    if (balance > 1 && this._getBalance(node.left) < 0) {
      node.left = this._rotateLeft(node.left);
      return this._rotateRight(node);
    }
    if (balance < -1 && this._getBalance(node.right) > 0) {
      node.right = this._rotateRight(node.right);
      return this._rotateLeft(node);
    }

    return node;
  }

  // Find max value
  findMax() {
    let node = this.root;
    while (node.right) node = node.right;
    return node.value;
  }

  // Rotate tree node with right child to balance the tree
  _rotateLeft(z) {
    let y = z.right;
    let T2 = y.left;
    y.left = z;
    z.right = T2;
    z.height = Math.max(this._getHeight(z.left), this._getHeight(z.right)) + 1;
    y.height = Math.max(this._getHeight(y.left), this._getHeight(y.right)) + 1;
    return y;
  }

  // Rotate tree node with left child to balance the tree
  _rotateRight(y) {
    let x = y.left;
    let T2 = x.right;
    x.right = y;
    y.left = T2;
    y.height = Math.max(this._getHeight(y.left), this._getHeight(y.right)) + 1;
    x.height = Math.max(this._getHeight(x.left), this._getHeight(x.right)) + 1;
    return x;
  }

  // Helper function to get height of a node
  _getHeight(node) {
    if (node === null) {
      return 0;
    }
    return node.height;
  }

  // Get balance factor of a node
  _getBalance(node) {
    if (node === null) {
      return 0;
    }
    return this._getHeight(node.left) - this._getHeight(node.right);
  }

  // Get node with min value (used for deletion)
  _minValueNode(node) {
    let current = node;
    while (current.left !== null) {
      current = current.left;
    }
    return current;
  }

  // Search for a value in the tree
  search(value) {
    return this._search(this.root, value);
  }

  _search(node, value) {
    // If the node is null or the node's value matches the search value
    if (node === null || node.value === value) {
      return node !== null;
    }

    // If the search value is less than the node's value, search the left subtree
    if (value < node.value) {
      return this._search(node.left, value);
    }

    // If the search value is greater than the node's value, search the right subtree
    return this._search(node.right, value);
  }
}

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

var minimumDifference = function (nums) {
  const heap = new MaxHeap();
  const NUMS_EACH_SIDE = nums.length * (1 / 3);
  for (let i = 0; i < NUMS_EACH_SIDE; i++) {
    heap.insert(nums[i]);
  }

  // initially the sum of the first n/3 elements
  let leftSum = heap.heap.slice(1).reduce((acc, val) => acc + val, 0);

  const totalSum = nums.reduce((acc, val) => acc + val, 0);
  // the sum of the last 2n/3 elements
  let rightSum = totalSum - leftSum;

  const rightTree = new AVLTree();

  // the smallest elements in the right portion
  const rightPortion = nums.slice(NUMS_EACH_SIDE);
  rightPortion.sort((a, b) => a - b);
  let rightSmallestSum = 0;
  for (let i = 0; i < rightPortion.length / 2; i++) {
    const num = rightPortion[i];
    rightSmallestSum += num;
    rightTree.insert(num);
  }

  let result = leftSum - (rightSum - rightSmallestSum);

  // [:i] denotes the left region
  for (let i = NUMS_EACH_SIDE; i < nums.length - NUMS_EACH_SIDE; i++) {
    const num = nums[i];
    // add new element to the left, pop out the smallest
    leftSum += num;
    heap.insert(num);
    const smallest = heap.remove();
    leftSum -= smallest;

    // if we don't lose a number in smallest
    if (!rightTree.search(num)) {
      rightSum -= num;
      const largestSmallest = rightTree.findMax();
      rightSmallestSum -= largestSmallest;
      rightTree.remove(largestSmallest);
    }

    // if we do lose a number in smallest
    else {
      rightSum -= num;
      rightSmallestSum -= num;
      rightTree.remove(num);
    }

    result = Math.min(result, leftSum - (rightSum - rightSmallestSum));
  }

  return result;
};
