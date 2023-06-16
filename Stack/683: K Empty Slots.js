// https://leetcode.com/problems/k-empty-slots/description/
// Difficulty: Hard
// tags: bst (self balancing), monotonic deque

// Problem
/*
Simplified:
Input: bulbs = [1,3,2], k = 1
Output: 2
Explanation:
On the first day: bulbs[0] = 1, first bulb is turned on: [1,0,0]
On the second day: bulbs[1] = 3, third bulb is turned on: [1,0,1]
On the third day: bulbs[2] = 2, second bulb is turned on: [1,1,1]
We return 2 because on the second day, there were two on bulbs with one off bulb between them.

Detailed:

You have n bulbs in a row numbered from 1 to n. Initially, all the bulbs are turned off. We turn on exactly one bulb every day until all bulbs are on after n days.

You are given an array bulbs of length n where bulbs[i] = x means that on the (i+1)th day, we will turn on the bulb at position x where i is 0-indexed and x is 1-indexed.

Given an integer k, return the minimum day number such that there exists two turned on bulbs that have exactly k bulbs between them that are all turned off. If there isn't such day, return -1.
*/

// Solution 1, O(n^2) time and O(n) space
/*
Maintain an ordered array of bulbs. So on day 1, we turn on the bulb at position 3. [3]. The next day, we turn on 9, [3, 9], then we turn on 5, [3, 5, 9], etc. Every time we insert a bulb, check its neighbors to see if we fulfill the condition.

To insert a bulb, it takes n time, because we need to shift over elements. In my implementation, I used binary search to find the insert location, to at least speed it up a but.
*/

// * Solution 2 O(n log n) time and O(n) space
/*
The same as solution 1, but instead of a sorted array, we use a self balancing BST. This way, we can insert in O(log n) time, and check neighbors in O(log n) time. So the total time complexity is O(n log n). The space is still n.

Note: The code for solution 2 uses a copy pasted template for a self-balancing BST. I understand the implementation, but did not write the code for the class. This is the only time (thus far) I have copy pasted a template, as usually I implement them myself. However self-balancing BSTs are generally outside the scope of interviews, so I don't worry about implementing them myself.
*/

// * Solution 3, O(n) time and O(n) space
/*
Instead of considering which bulbs we turn on every unit of time, consder the bulbs in order. For instance we turn on bulb 1 on day 6. Then we turn on bulb 2 on day 9. If k=1, it's possible we could turn on bulb 3 before day 9, meaning we would be fulfilled. I haven't walked through the implementation but I think the key takeaway is that it is good to consider things from two perspectives, in this case, by bulb position as opposed to time.
*/

// * Solution 4, O(n*k) time, O(n) space. Maintain an array of size n. Every time we turn on a bulb, scan up to k to the left and k to the right to see if we meet the condition.

// Solution 1

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
    }

    return result;
  }
}

var kEmptySlots = function (bulbs, k) {
  // bulbs maps the day to the bulb we turn on on that day

  // const orderedBulbs = []; // maintains positions for the bulbs that are turned on, in order. so on day x when we turn on bulb at position 5, we insert the 5 in order. we can see its left and right neighbors and determine if one is k away.
  const bst = new SelfBalancingBST();

  // iterate through each day
  for (let day = 0; day < bulbs.length; day++) {
    const positionOfBulbTurnedOnThatDay = bulbs[day];
    bst.insert(positionOfBulbTurnedOnThatDay);
    const largestSmaller = bst.getSmaller(positionOfBulbTurnedOnThatDay);
    if (largestSmaller !== null) {
      if (positionOfBulbTurnedOnThatDay - largestSmaller === k + 1) {
        return day + 1;
      }
    }

    const smallestLarger = bst.getLarger(positionOfBulbTurnedOnThatDay);
    if (smallestLarger !== null) {
      if (smallestLarger - positionOfBulbTurnedOnThatDay === k + 1) {
        return day + 1;
      }
    }
    //    const insertionPoint = insert(orderedBulbs, positionOfBulbTurnedOnThatDay);
    //    if (orderedBulbs[insertionPoint] - orderedBulbs[insertionPoint - 1] - 1 === k) {
    //        return day + 1; // days are 1-indexed
    //    }

    //    if (orderedBulbs[insertionPoint + 1] - orderedBulbs[insertionPoint] - 1 === k) {
    //        return day + 1; // days are 1-indexed
    //    }
  }

  return -1;
};

// takes in a sorted array and a number, does a binary search (log n) to find the insertion point, then splices (n) the value in
// also returns the index that bulb was inserted at
function insert(sortedArr, insertThisNum) {
  // we will binary search for the index of the largest number smaller than num
  let l = 0;
  let r = sortedArr.length - 1;

  while (l <= r) {
    const m = Math.floor((r + l) / 2);
    const num = sortedArr[m];
    // if the number we are looking at is smaller, that is good. we can potentially look to the right
    if (num < insertThisNum) {
      l = m + 1;
    }

    // if the number we are looking at is too big, we must look left
    else if (num > insertThisNum) {
      r = m - 1;
    }
    // num will never equal insertThisNum because the problem yields strictly unique numbers
  }
  // here, r is the index of the largest number smaller than n

  sortedArr.splice(r + 1, 0, insertThisNum);

  return r + 1;
}

// Solution 2, using the copy pasted template as noted

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
    }

    return result;
  }
}

var kEmptySlots = function (bulbs, k) {
  // bulbs maps the day to the bulb we turn on on that day

  // const orderedBulbs = []; // maintains positions for the bulbs that are turned on, in order. so on day x when we turn on bulb at position 5, we insert the 5 in order. we can see its left and right neighbors and determine if one is k away.
  const bst = new SelfBalancingBST();

  // iterate through each day
  for (let day = 0; day < bulbs.length; day++) {
    const positionOfBulbTurnedOnThatDay = bulbs[day];
    bst.insert(positionOfBulbTurnedOnThatDay);
    const largestSmaller = bst.getSmaller(positionOfBulbTurnedOnThatDay);
    if (largestSmaller !== null) {
      if (positionOfBulbTurnedOnThatDay - largestSmaller === k + 1) {
        return day + 1;
      }
    }

    const smallestLarger = bst.getLarger(positionOfBulbTurnedOnThatDay);
    if (smallestLarger !== null) {
      if (smallestLarger - positionOfBulbTurnedOnThatDay === k + 1) {
        return day + 1;
      }
    }
    //    const insertionPoint = insert(orderedBulbs, positionOfBulbTurnedOnThatDay);
    //    if (orderedBulbs[insertionPoint] - orderedBulbs[insertionPoint - 1] - 1 === k) {
    //        return day + 1; // days are 1-indexed
    //    }

    //    if (orderedBulbs[insertionPoint + 1] - orderedBulbs[insertionPoint] - 1 === k) {
    //        return day + 1; // days are 1-indexed
    //    }
  }

  return -1;
};

// takes in a sorted array and a number, does a binary search (log n) to find the insertion point, then splices (n) the value in
// also returns the index that bulb was inserted at
function insert(sortedArr, insertThisNum) {
  // we will binary search for the index of the largest number smaller than num
  let l = 0;
  let r = sortedArr.length - 1;

  while (l <= r) {
    const m = Math.floor((r + l) / 2);
    const num = sortedArr[m];
    // if the number we are looking at is smaller, that is good. we can potentially look to the right
    if (num < insertThisNum) {
      l = m + 1;
    }

    // if the number we are looking at is too big, we must look left
    else if (num > insertThisNum) {
      r = m - 1;
    }
    // num will never equal insertThisNum because the problem yields strictly unique numbers
  }
  // here, r is the index of the largest number smaller than n

  sortedArr.splice(r + 1, 0, insertThisNum);

  return r + 1;
}
