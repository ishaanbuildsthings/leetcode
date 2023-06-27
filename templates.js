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

class minHeap {
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
