// https://leetcode.com/problems/minimum-absolute-difference-between-elements-with-constraint/
// Difficulty: Medium
// Tags: avl

// Problem
/*
You are given a 0-indexed integer array nums and an integer x.

Find the minimum absolute difference between two elements in the array that are at least x indices apart.

In other words, find two indices i and j such that abs(i - j) >= x and abs(nums[i] - nums[j]) is minimized.

Return an integer denoting the minimum absolute difference between two elements that are at least x indices apart.
*/

// Solution, O(n log n) time, O(n) space
/*
Maintain an AVL of the elements that aren't within x distance. As we slide, find the closest element to our current element. In the contest I did a worse implementation where I used two AVLs on the left and right but we can just use one.
*/

class Node {
  constructor(key) {
    this.key = key;
    this.height = 1;
    this.count = 1;
    this.left = null;
    this.right = null;
  }
}

class AVL {
  constructor() {
    this.root = null;
  }

  getHeight(node) {
    if (!node) return 0;
    return node.height;
  }

  updateHeight(node) {
    node.height =
      1 + Math.max(this.getHeight(node.left), this.getHeight(node.right));
  }

  getBalance(node) {
    if (!node) return 0;
    return this.getHeight(node.left) - this.getHeight(node.right);
  }

  leftRotate(x) {
    let y = x.right;
    let T2 = y.left;

    y.left = x;
    x.right = T2;

    this.updateHeight(x);
    this.updateHeight(y);

    return y;
  }

  rightRotate(y) {
    let x = y.left;
    let T2 = x.right;

    x.right = y;
    y.left = T2;

    this.updateHeight(y);
    this.updateHeight(x);

    return x;
  }

  insert(key) {
    this.root = this._insert(this.root, key);
  }

  _insert(root, key) {
    if (!root) return new Node(key);

    if (key === root.key) {
      root.count++;
      return root;
    }

    if (key < root.key) {
      root.left = this._insert(root.left, key);
    } else {
      root.right = this._insert(root.right, key);
    }

    this.updateHeight(root);

    let balance = this.getBalance(root);

    if (balance > 1) {
      if (key < root.left.key) return this.rightRotate(root);
      root.left = this.leftRotate(root.left);
      return this.rightRotate(root);
    }

    if (balance < -1) {
      if (key > root.right.key) return this.leftRotate(root);
      root.right = this.rightRotate(root.right);
      return this.leftRotate(root);
    }

    return root;
  }

  minValueNode(root) {
    let current = root;
    while (current.left) {
      current = current.left;
    }
    return current;
  }

  remove(key) {
    this.root = this._remove(this.root, key);
  }

  _remove(root, key) {
    if (!root) return root;

    if (key < root.key) {
      root.left = this._remove(root.left, key);
    } else if (key > root.key) {
      root.right = this._remove(root.right, key);
    } else {
      if (root.count > 1) {
        root.count--;
        return root;
      } else {
        if (!root.left) return root.right;
        else if (!root.right) return root.left;

        let temp = this.minValueNode(root.right);
        root.key = temp.key;
        root.right = this._remove(root.right, temp.key);
      }
    }

    this.updateHeight(root);

    let balance = this.getBalance(root);

    if (balance > 1) {
      if (this.getBalance(root.left) >= 0) return this.rightRotate(root);
      root.left = this.leftRotate(root.left);
      return this.rightRotate(root);
    }

    if (balance < -1) {
      if (this.getBalance(root.right) <= 0) return this.leftRotate(root);
      root.right = this.rightRotate(root.right);
      return this.leftRotate(root);
    }

    return root;
  }

  findClosest(key) {
    return this._findClosest(
      this.root,
      key,
      Number.MAX_VALUE,
      Number.MAX_VALUE
    );
  }

  _findClosest(root, key, closest, diff) {
    if (!root) return closest;

    let currentDiff = Math.abs(root.key - key);
    if (currentDiff < diff) {
      closest = root.key;
      diff = currentDiff;
    }

    if (key < root.key) {
      return this._findClosest(root.left, key, closest, diff);
    } else {
      return this._findClosest(root.right, key, closest, diff);
    }
  }
}

var minAbsoluteDifference = function (nums, x) {
  const leftAvl = new AVL();
  const rightAvl = new AVL();

  let result = Infinity;

  for (const num of nums) {
    rightAvl.insert(num);
  }

  // remove the first x numbers from the right avl
  for (let i = 0; i < x; i++) {
    const num = nums[i];
    rightAvl.remove(num);
  }

  // console.log(`right avl: ${JSON.stringify(rightAvl)}`);

  /*
    as we iterate through the avl, we remove numbers from the right, and add numbers to the left avl. then we find the closest to the left avl and the right avl
    */
  for (let i = 0; i < nums.length; i++) {
    // if we can add a number to our left avl, do so
    const leftMostIndexWeCanUse = i - x;
    if (i - x >= 0) {
      leftAvl.insert(nums[i - x]);
    }

    // remove a number from the right,
    const rightMostIndexWeTouch = i + x - 1;
    if (rightMostIndexWeTouch < nums.length) {
      rightAvl.remove(nums[rightMostIndexWeTouch]);
    }

    const closestToLeft = leftAvl.findClosest(nums[i]);
    const leftDifference = Math.abs(nums[i] - closestToLeft);
    const closestToRight = rightAvl.findClosest(nums[i]);
    const rightDifference = Math.abs(nums[i] - closestToRight);
    result = Math.min(result, leftDifference, rightDifference);
  }

  return result;
};
