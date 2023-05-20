// https://leetcode.com/problems/lru-cache/description/
// Difficulty: Medium
// tags: linked list

// Problem
/*
Simplified:
Make an LRU cache. When we add a key value pair, it should do so in O(1), either creating a new pair or updating the existing key. Move this to be most recently used. When we get(key), return the value if it exists, and update it to be most recently used. When we exceed a capacity, the least recently used key should be evicted.

Detailed:
Implement the LRUCache class:

LRUCache(int capacity) Initialize the LRU cache with positive size capacity.
int get(int key) Return the value of the key if the key exists, otherwise return -1.
void put(int key, int value) Update the value of the key if the key exists. Otherwise, add the key-value pair to the cache. If the number of keys exceeds the capacity from this operation, evict the least recently used key.
The functions get and put must each run in O(1) average time complexity.
*/

// Solution: O(1) time for all operations, O(n) space

/*
To make this structure, we need to be able to have O(1) deletion from every position, since at any time we can access any element and update it to be most recently used. To do this, we need a linked list. We maintain a map of keys to nodes, so that when we need to delete a certain node, we can instantly have a reference to that node. We use a doubly linked list so that we can delete that node without needing a reference to the node before it. When we get an element, look up the key, find the node, and return the value. Pop that node out, and append it to the right head. When we put a key, if it doesn't exist, add it to the right. If it does exist, pop it out and add it to the right. When we exceed capacity, we need to pop the leftmost node out. But we also need to delete it from our storage, though we don't have a way to do that, because we don't know where that node is in the storage. To fix this, make sure nodes contain keys as well, so we can look up the key in storage to find where the node was in storage, and delete that.
*/

// We can't use a deque, because we can't delete really from the middle in O(1). If we tried to just delete a key or clear out a cell in the deque, we are basically leaving a tombstone / empty spot. The problem is now we have a hole, so when we try to pop from the left and we are at the hole, we might need to iterate over all the holes to find an element to actually pop. Consider a deque of size 10 and we delete 8 elements, leaving 8 holes, after we fill up 8 more elements, then another to oveflow, we need to start popping the smallest keys in the deque. But once we reach the hole, we have no way to know what key is next. The linkedlist basically fixes this by having each cell point to the next one. Our tail pointer won't be maintained properly since when we do this.tailPointer++; it might end up at a hole.

class Node {
  constructor(key, val) {
    this.key = key;
    this.val = val;
    this.next = null;
    this.prev = null;
  }
}

class LinkedList {
  constructor() {
    const dummyL = new Node();
    this.left = dummyL;
    const dummyR = new Node();
    this.right = dummyR;
    dummyL.next = dummyR;
    dummyR.prev = dummyL;
    this.storage = {}; // maps keys to nodes. so when we look up a key we can find the node in constant time
    this.size = 0;
  }
}

var LRUCache = function (capacity) {
  this.capacity = capacity;
  this.list = new LinkedList();
};

// do we need doubly linked list
// is deque with hashmap different than deque with linked list, cause we have random access vs o(1) deletion
LRUCache.prototype.get = function (key) {
  if (key in this.list.storage) {
    const nodeWithVal = this.list.storage[key];

    // o(1) delete the element
    const elementToRight = nodeWithVal.next;
    const elementToLeft = nodeWithVal.prev;
    elementToLeft.next = elementToRight;
    elementToRight.prev = elementToLeft;

    // o(1) insert the element to the head
    const rightHead = this.list.right.prev;
    this.list.right.prev = nodeWithVal;
    nodeWithVal.next = this.list.right;
    nodeWithVal.prev = rightHead;
    rightHead.next = nodeWithVal;

    return nodeWithVal.val;
  }
  return -1;
};

/**
 * @param {number} key
 * @param {number} value
 * @return {void}
 */
LRUCache.prototype.put = function (key, value) {
  // if we already have a node
  if (key in this.list.storage) {
    const nodeWithVal = this.list.storage[key];

    // o(1) delete the element
    const elementToRight = nodeWithVal.next;
    const elementToLeft = nodeWithVal.prev;
    elementToLeft.next = elementToRight;
    elementToRight.prev = elementToLeft;

    // o(1) insert the element to the head
    const rightHead = this.list.right.prev;
    this.list.right.prev = nodeWithVal;
    nodeWithVal.next = this.list.right;
    nodeWithVal.prev = rightHead;
    rightHead.next = nodeWithVal;

    nodeWithVal.val = value;
    return;
  }

  // create a new node, assign it in storage so we can look it up by key later, and insert it into the right
  const newNode = new Node(key, value);
  this.list.storage[key] = newNode;
  const rightHead = this.list.right.prev;
  this.list.right.prev = newNode;
  newNode.next = this.list.right;
  newNode.prev = rightHead;
  rightHead.next = newNode;

  // if we exceeded our capacity, we need to delete the left most node, but we also need to delete it from storage, which requires the key being stored in the node
  this.list.size++;
  if (this.list.size > this.capacity) {
    const nodeToBePopped = this.list.left.next;
    const key = nodeToBePopped.key;
    delete this.list.storage[key]; // remove the key : node mapping
    this.list.left.next = this.list.left.next.next;
    this.list.left.next.prev = this.list.left;
    this.list.size--;
  }
};

/**
 * Your LRUCache object will be instantiated and called as such:
 * var obj = new LRUCache(capacity)
 * var param_1 = obj.get(key)
 * obj.put(key,value)
 */
