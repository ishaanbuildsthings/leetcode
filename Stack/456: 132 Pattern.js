// https://leetcode.com/problems/132-pattern/description/
// Difficulty: Medium
// tags: monotonic stack, self balancing bst

// Problem
/*
Given an array of n integers nums, a 132 pattern is a subsequence of three integers nums[i], nums[j] and nums[k] such that i < j < k and nums[i] < nums[k] < nums[j].

Return true if there is a 132 pattern in nums, otherwise, return false.
*/

// Soltuion 1, O(n) time and O(1) space.
/*
Maintain a monotonic decreasing stack. We will store tuples of [num, lowest num on left]. When we see a bigger number, like [20, 15, 10, 9, 17] we start popping. So we get [20, 17] where 17 has seen a 10 on the left. Basically we found the biggest number to the right of 10 at the current point, but we have to keep the 20 as well in case a 132 pattern is formed with the 20. We can't rule out the 20 in case for instance it had a 1 on the left and we see a 19 later. We would then need to pop the 17 and see the 20 forms a pattern.

The code can be a bit simplified if we maintain a function global for the current minimum and just use that in the tuple, instead of the weird logic I used where we check the previous minimun. The top of the function I wrote out why we have to pop elements but the TLDR is so we can access potential elements further back left, like accessing the 20 with a 19.
*/
// Solution 2 is n log n time with a self balancing bst, for each number we find the largest number smalelr than itself, on the right, and the smallest number on the left.

var find132pattern = function (nums) {
  /*
    monotonically decreasing stack

    WHY WE NEED TO POP ELEMENTS:

    say we start to add elements:
    [20, 15, 10]

    then we add one that is increasing
    [20, 15, 10, 17]

    now 17 knows 10 is the lowest element to the left

    [20, 15, 10, 17_10]

    add 19
    [20, 15, 10, 17_10, 19_10]

    add 5
    [20, 15, 10, 17_10, 19_10, 5]

    but now when we add 16, we have a 132, 10 19 16, but we cannot see that. so we do need to pop elements.

    instead:

    [20, 15, 10]

    add one increasing: 17, and pop
    [20, 17_10]

    add 19

    [20, 19_10]

    add 5

    [20, 19_10, 5]

    store a number along with its range of lowest

    */
  const stack = [[nums[0], Infinity]]; // stores tuples of [num, lowest num on left]

  for (let i = 1; i < nums.length; i++) {
    let minOnLeft = stack[stack.length - 1][0];

    let stackNum = stack[stack.length - 1][0];
    let stackMinOnLeft = stack[stack.length - 1][1];

    // pop elements as long as our new element is monotonically increasing
    while (stack.length > 0 && stack[stack.length - 1][0] < nums[i]) {
      stackNum = stack[stack.length - 1][0];
      stackMinOnLeft = stack[stack.length - 1][1];
      minOnLeft = Math.min(minOnLeft, stackNum, stackMinOnLeft);
      stack.pop();
    }

    stack.push([nums[i], minOnLeft]);

    if (stack.length > 1) {
      stackNum = stack[stack.length - 2][0];
      stackMinOnLeft = stack[stack.length - 2][1];
    }

    // if our new number is in the middle, it is possible we found a 132 sequence
    if (
      nums[i] < stackNum &&
      nums[i] > stackMinOnLeft &&
      stackMinOnLeft < stackNum
    ) {
      return true;
    }
  }

  return false;
};

// Solution 2, O(n log n) time and O(n) space, using a self balancing bst.

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
