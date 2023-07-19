// Self Balancing BST
/*
const bst = new SelfBalancingBST();
bst.insert(10);
bst.getSmaller(10); // get largest number smaller than 10
bst.getLarger(10); // get smallest number larger than 10
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
    }

    return result;
  }
}

// Deque

class Deque {
  constructor() {
    this.head = 0;
    this.tail = -1;
    this.storage = {};
  }

  push(val) {
    this.tail++;
    this.storage[this.tail] = val;
  }

  pop(val) {
    if (!(this.tail in this.storage)) {
      return null;
    }

    const popped = this.storage[this.tail];
    this.tail--;
    return popped;
  }

  shift() {
    if (!(this.head in this.storage)) {
      return null;
    }

    const popped = this.storage[this.head];
    this.head++;
    return popped;
  }

  unshift(val) {
    this.head--;
    this.storage[this.head] = val;
  }

  size() {
    return this.tail - this.head + 1;
  }
}

// minheap

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
      if (left < this.heap.length && this.heap[left] < this.heap[smallest]) {
        smallest = left;
      }

      // if there is a right child and it's value is smaller than our potentially updated smallest position, our smallest element will go there
      if (right < this.heap.length && this.heap[right] < this.heap[smallest]) {
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
    while (i > 1 && this.heap[i] < this.heap[Math.floor(i / 2)]) {
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

// _____________________________________________________MAX HEAP _____________________________________________________

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

// _____________________________________________________AVL TREE, with insert(val), remove(val), findMax() O(1), search(val) returns true or false, and supports duplicate values _____________________________________________________

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
