// https://leetcode.com/problems/132-pattern/description/
// Difficulty: Medium
// tags: stack, self balancing bst

// Problem
/*
Given an array of n integers nums, a 132 pattern is a subsequence of three integers nums[i], nums[j] and nums[k] such that i < j < k and nums[i] < nums[k] < nums[j].

Return true if there is a 132 pattern in nums, otherwise, return false.
*/

class TreeNode {
  constructor(value) {
    this.value = value;
    this.left = null;
    this.right = null;
    this.height = 1; // height of node for AVL tree balancing
  }
}

class SelfBalancingBST {
  constructor() {
    this.root = null;
  }

  // Utility function to get the height of a node
  height(node) {
    return node ? node.height : 0;
  }

  // Rotate left to fix the balance
  rotateLeft(z) {
    const y = z.right;
    const T2 = y.left;

    y.left = z;
    z.right = T2;

    z.height = Math.max(this.height(z.left), this.height(z.right)) + 1;
    y.height = Math.max(this.height(y.left), this.height(y.right)) + 1;

    return y;
  }

  // Rotate right to fix the balance
  rotateRight(y) {
    const x = y.left;
    const T2 = x.right;

    x.right = y;
    y.left = T2;

    y.height = Math.max(this.height(y.left), this.height(y.right)) + 1;
    x.height = Math.max(this.height(x.left), this.height(x.right)) + 1;

    return x;
  }

  getBalance(node) {
    return this.height(node.left) - this.height(node.right);
  }

  // Inserts a value into the self-balancing BST
  insert(value) {
    const insertNode = (node, value) => {
      if (node === null) return new TreeNode(value);

      if (value < node.value) {
        node.left = insertNode(node.left, value);
      } else if (value > node.value) {
        node.right = insertNode(node.right, value);
      } else {
        return node; // Duplicates are not allowed
      }

      node.height =
        1 + Math.max(this.height(node.left), this.height(node.right));

      const balance = this.getBalance(node);

      if (balance > 1) {
        if (value < node.left.value) {
          return this.rotateRight(node);
        } else {
          node.left = this.rotateLeft(node.left);
          return this.rotateRight(node);
        }
      }

      if (balance < -1) {
        if (value > node.right.value) {
          return this.rotateLeft(node);
        } else {
          node.right = this.rotateRight(node.right);
          return this.rotateLeft(node);
        }
      }

      return node;
    };

    this.root = insertNode(this.root, value);
  }

  // Returns the largest number that is smaller than num
  getSmaller(num) {
    let current = this.root;
    let result = null;

    while (current) {
      if (current.value < num) {
        result = current.value;
        current = current.right;
      } else {
        current = current.left;
      }
    }

    return result;
  }

  // Returns the smallest number that is larger than num
  getLarger(num) {
    let current = this.root;
    let result = null;

    while (current) {
      if (current.value > num) {
        result = current.value;
        current = current.left;
      } else {
        current = current.right;
      }
      456;
    }

    return result;
  }
}

var find132pattern = function (nums) {
  const mapping = {}; // maps an index to the smallest number to the left of it

  let smallestNumber = Infinity;

  for (let i = 0; i < nums.length; i++) {
    mapping[i] = smallestNumber;
    if (nums[i] < smallestNumber) {
      smallestNumber = nums[i];
    }
  }

  const bst = new SelfBalancingBST();

  const largeMapping = {}; // maps an index to the largest number to its right, that is smaller than the number itself

  for (let i = nums.length - 1; i >= 0; i--) {
    const num = nums[i];
    // for each number, see what is the largest number that is smaller than it, and add that to the mapping
    const largestSmaller = bst.getSmaller(num);
    if (largestSmaller === null) {
      largeMapping[i] = Infinity;
    } else {
      largeMapping[i] = largestSmaller;
    }

    bst.insert(num);
  }

  for (let i = 0; i < nums.length; i++) {
    const num = nums[i];
    const smallestLeft = mapping[i];
    const largestSmaller = largeMapping[i];

    if (
      smallestLeft < num &&
      num > largestSmaller &&
      smallestLeft < largestSmaller
    ) {
      return true;
    }
  }

  return false;
};
// smallest to left:   I 3
//                     3 5 4 2
