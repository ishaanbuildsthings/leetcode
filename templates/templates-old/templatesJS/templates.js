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

// union find by rank

class UnionFind {
  constructor() {
    this.parents = {}; // maps a cell to its parent, we will use COLS * r + c
    this.ranks = {}; // maps a representative cell to its island size
  }

  find(node) {
    // node is COLS * r + c
    let current = node;
    while (this.parents[current] !== current) {
      const tempParent = this.parents[current];
      this.parents[current] = this.parents[tempParent];
      current = tempParent;
    }
    return current;
  }

  union(node1, node2) {
    const parent1 = this.find(node1);
    const parent2 = this.find(node2);

    const rank1 = this.ranks[parent1];
    const rank2 = this.ranks[parent2];

    // if they're already unioned, return false, the union was unsuccessful
    if (parent1 === parent2) {
      return false;
    }

    if (rank1 < rank2) {
      this.parents[parent1] = parent2;
      delete this.ranks[parent1];
    } else if (rank1 > rank2) {
      this.parents[parent2] = parent1;
      delete this.ranks[parent2];
    } else {
      this.parents[parent2] = parent1;
      delete this.ranks[parent2];
      this.ranks[parent1]++; // if the trees have the same rank, the size must increase by 1
    }

    return true;
  }
}

// splay tree

///////////////////// Template ///////////////////////
class SplayNode {
  constructor(value) {
    this.parent = null;
    this.left = null;
    this.right = null;
    this.val = value;
    this.sum = value;
    this.sz = 1;
  }
  update() {
    this.sz =
      (this.left != null ? this.left.sz : 0) +
      (this.right != null ? this.right.sz : 0) +
      1;
    this.sum =
      (this.left != null ? this.left.sum : 0) +
      (this.right != null ? this.right.sum : 0) +
      this.val;
  }
  isLeft() {
    return this.parent != null && this.parent.left == this;
  }
  isRight() {
    return this.parent != null && this.parent.right == this;
  }
  isRoot(guard = null) {
    return this.parent == guard;
  }
}

// MultiSet
class SplayTree {
  constructor() {
    this.root = null;
    this.cmp = (x, y) => (x >= y ? 0 : 1);
  }
  zig(x) {
    // right rotation
    let y = x.parent;
    if (x.right != null) x.right.parent = y;
    y.left = x.right;
    x.right = y;
    if (y.isLeft()) {
      y.parent.left = x;
    } else if (y.isRight()) {
      y.parent.right = x;
    }
    x.parent = y.parent;
    y.parent = x;
    y.update();
    x.update();
  }
  zag(x) {
    // left rotation
    let y = x.parent;
    if (x.left != null) x.left.parent = y;
    y.right = x.left;
    x.left = y;
    if (y.isLeft()) {
      y.parent.left = x;
    } else if (y.isRight()) {
      y.parent.right = x;
    }
    x.parent = y.parent;
    y.parent = x;
    y.update();
    x.update();
  }
  zigzig(x) {
    // RR
    this.zig(x.parent);
    this.zig(x);
  }
  zigzag(x) {
    // RL
    this.zig(x);
    this.zag(x);
  }
  zagzag(x) {
    // LL
    this.zag(x.parent);
    this.zag(x);
  }
  zagzig(x) {
    // LR
    this.zag(x);
    this.zig(x);
  }
  splay(node, guard = null) {
    // splay node under guard, default splay to root
    while (!node.isRoot(guard)) {
      if (node.parent.isRoot(guard)) {
        if (node.isLeft()) {
          this.zig(node);
        } else {
          this.zag(node);
        }
      } else {
        if (node.parent.isLeft()) {
          if (node.isLeft()) {
            this.zigzig(node);
          } else {
            this.zagzig(node);
          }
        } else {
          if (node.isRight()) {
            this.zagzag(node);
          } else {
            this.zigzag(node);
          }
        }
      }
    }
    if (guard == null) this.root = node;
  }
  LastNode(x) {
    this.splay(x);
    let node = x.left;
    if (node == null) return null;
    while (node.right != null) node = node.right;
    this.splay(node);
    return node;
  }
  NextNode(x) {
    this.splay(x);
    let node = x.right;
    if (node == null) return null;
    while (node.left != null) node = node.left;
    this.splay(node);
    return node;
  }
  find(value) {
    return this.findFirstOf(value);
  }
  findFirstOf(value) {
    let node = this.root,
      res = null,
      last_visited = null;
    while (node != null) {
      last_visited = node;
      if (this.cmp(value, node.val)) {
        node = node.left;
      } else if (this.cmp(node.val, value)) {
        node = node.right;
      } else {
        res = node;
        node = node.left;
      }
    }
    if (last_visited != null) this.splay(last_visited);
    return res;
  }
  findLastOf(value) {
    let node = this.root,
      res = null,
      last_visited = null;
    while (node != null) {
      last_visited = node;
      if (this.cmp(value, node.val)) {
        node = node.left;
      } else if (this.cmp(node.val, value)) {
        node = node.right;
      } else {
        res = node;
        node = node.right;
      }
    }
    if (last_visited != null) this.splay(last_visited);
    return res;
  }
  findRankOf(node) {
    this.splay(node);
    return node.left == null ? 0 : node.left.sz;
  }
  findSuccessorOf(value) {
    let node = this.root,
      res = null,
      last_visited = null;
    while (node != null) {
      last_visited = node;
      if (this.cmp(value, node.val)) {
        res = node;
        node = node.left;
      } else {
        node = node.right;
      }
    }
    if (last_visited != null) this.splay(last_visited);
    return res;
  }
  findPrecursorOf(value) {
    let node = this.root,
      res = null,
      last_visited = null;
    while (node != null) {
      last_visited = node;
      if (this.cmp(node.val, value)) {
        res = node;
        node = node.right;
      } else {
        node = node.left;
      }
    }
    if (last_visited != null) this.splay(last_visited);
    return res;
  }
  findKthNode(rank) {
    if (rank < 0 || rank >= this.size()) return null;
    let node = this.root;
    while (node != null) {
      let leftsize = node.left == null ? 0 : node.left.sz;
      if (leftsize == rank) break;
      if (leftsize > rank) {
        node = node.left;
      } else {
        rank -= leftsize + 1;
        node = node.right;
      }
    }
    this.splay(node);
    return node;
  }
  make(value) {
    return new SplayNode(value);
  }
  removeNode(node) {
    node = null;
  }

  // -------------------------------- Public Usage --------------------------------------
  insert(value) {
    // allow duplicates  LST.set()
    if (this.root == null) {
      this.root = this.make(value);
      return this.root;
    }
    let node = this.root;
    while (node != null) {
      if (this.cmp(value, node.val)) {
        if (node.left == null) {
          node.left = this.make(value);
          node.left.parent = node;
          node = node.left;
          break;
        }
        node = node.left;
      } else {
        if (node.right == null) {
          node.right = this.make(value);
          node.right.parent = node;
          node = node.right;
          break;
        }
        node = node.right;
      }
    }
    this.splay(node);
    return node;
  }
  remove(value) {
    // remove one node, not all   LST.unset()
    let node = this.find(value);
    if (node == null) return false;
    this.splay(node);
    if (node.left == null) {
      this.root = node.right;
      if (node.right != null) node.right.parent = null;
      this.removeNode(node);
      return true;
    }
    if (node.right == null) {
      this.root = node.left;
      if (node.left != null) node.left.parent = null;
      this.removeNode(node);
      return true;
    }
    let last_node = this.LastNode(node);
    let next_node = this.NextNode(node);
    this.splay(last_node);
    this.splay(next_node, last_node);
    this.removeNode(next_node.left);
    next_node.left = null;
    next_node.update();
    last_node.update();
    return true;
  }
  has(value) {
    // LST.get()
    return this.count(value) > 0;
  }
  count(value) {
    let x = this.findFirstOf(value);
    if (x == null) return 0;
    let rank_x = this.findRankOf(x);
    let y = this.findLastOf(value);
    let rank_y = this.findRankOf(y);
    return rank_y - rank_x + 1;
  }
  rankOf(value) {
    // The number of elements strictly less than value
    let x = this.findPrecursorOf(value);
    return x == null ? 0 : this.findRankOf(x) + 1;
  }
  findKth(rank) {
    // (0-indexed)
    let x = this.findKthNode(rank);
    return x == null ? null : x.val;
  }
  higher(value) {
    // > upper_bound()  LST.next(value)
    let node = this.findSuccessorOf(value);
    return node == null ? null : node.val;
  }
  lower(value) {
    // <  LST.prev(value - 1)
    let node = this.findPrecursorOf(value);
    return node == null ? null : node.val;
  }
  ceiling(value) {
    // >=
    return this.has(value) ? value : this.higher(value);
  }
  floor(value) {
    // <=
    return this.has(value) ? value : this.lower(value);
  }
  first() {
    return this.findKth(0);
  }
  last() {
    return this.findKth(this.size() - 1);
  }
  poll() {
    let res = this.first();
    this.remove(res);
    return res;
  }
  pollLast() {
    let res = this.last();
    this.remove(res);
    return res;
  }
  size() {
    return this.root == null ? 0 : this.root.sz;
  }
  isEmpty() {
    return this.root == null;
  }
  show() {
    let res = [];
    const dfs = (x) => {
      if (x == null) return;
      dfs(x.left);
      res.push(x.val);
      dfs(x.right);
    };
    dfs(this.root);
    return res;
  }
}
