// https://leetcode.com/problems/design-circular-queue/description/
// Difficulty: Medium

// Problem
/*
Design your implementation of the circular queue. The circular queue is a linear data structure in which the operations are performed based on FIFO (First In First Out) principle, and the last position is connected back to the first position to make a circle. It is also called "Ring Buffer".

One of the benefits of the circular queue is that we can make use of the spaces in front of the queue. In a normal queue, once the queue becomes full, we cannot insert the next element even if there is a space in front of the queue. But using the circular queue, we can use the space to store new values.

Implement the MyCircularQueue class:

MyCircularQueue(k) Initializes the object with the size of the queue to be k.
int Front() Gets the front item from the queue. If the queue is empty, return -1.
int Rear() Gets the last item from the queue. If the queue is empty, return -1.
boolean enQueue(int value) Inserts an element into the circular queue. Return true if the operation is successful.
boolean deQueue() Deletes an element from the circular queue. Return true if the operation is successful.
boolean isEmpty() Checks whether the circular queue is empty or not.
boolean isFull() Checks whether the circular queue is full or not.
You must solve the problem without using the built-in queue data structure in your programming language.
*/

// Solution: O(n) space, where n is the size allocated for the queue, if that is not considered, then O(1) space. O(1) time to enqueue, dequeue, peek front, or peek back

/*
Think of a circular array of size 3, first initialize: [_, _, _]
Maintain a pointer where we first insert into, and where we decrement from
V
_, _, _
^

Insert a 1, then move the insert pointer
   V
1, _, _
^

Insert a 2
      V
1, 2, _
^

Dequeue and increment pointer, write over the value as null to dequeue
      V
_, 2, _
   ^

At any time, if our pointers are pointing to the same spot, the queue is either empty or full, and we can verify by checking a value
*/

var MyCircularQueue = function (k) {
  this.storage = new Array(k).fill(null);
  this.insertPointer = 0;
  this.dqPointer = 0;
};

/**
 * @param {number} value
 * @return {boolean}
 */
MyCircularQueue.prototype.enQueue = function (value) {
  if (this.storage[this.insertPointer] !== null) {
    return false;
  }
  this.storage[this.insertPointer] = value;
  this.insertPointer++;
  if (this.insertPointer >= this.storage.length) {
    this.insertPointer = 0;
  }
  return true;
};

/**
 * @return {boolean}
 */
MyCircularQueue.prototype.deQueue = function () {
  if (this.storage[this.dqPointer] === null) {
    return false;
  }
  this.storage[this.dqPointer] = null;
  this.dqPointer++;
  if (this.dqPointer >= this.storage.length) {
    this.dqPointer = 0;
  }
  return true;
};

/**
 * @return {number}
 */
MyCircularQueue.prototype.Front = function () {
  if (this.storage[this.dqPointer] === null) {
    return -1;
  }
  return this.storage[this.dqPointer];
};

/**
 * @return {number}
 */
MyCircularQueue.prototype.Rear = function () {
  if (this.insertPointer === 0) {
    if (this.storage[this.storage.length - 1] !== null) {
      return this.storage[this.storage.length - 1];
    } else {
      return -1;
    }
  }
  if (this.storage[this.insertPointer - 1] === null) {
    return -1;
  }

  return this.storage[this.insertPointer - 1];
};

/**
 * @return {boolean}
 */
MyCircularQueue.prototype.isEmpty = function () {
  if (this.insertPointer !== this.dqPointer) {
    return false;
  }
  if (this.storage[this.insertPointer] === null) return true;
  return false;
};

/**
 * @return {boolean}
 */
MyCircularQueue.prototype.isFull = function () {
  if (
    this.insertPointer === this.dqPointer &&
    this.storage[this.insertPointer] !== null
  ) {
    return true;
  }
  return false;
};

/**
 * Your MyCircularQueue object will be instantiated and called as such:
 * var obj = new MyCircularQueue(k)
 * var param_1 = obj.enQueue(value)
 * var param_2 = obj.deQueue()
 * var param_3 = obj.Front()
 * var param_4 = obj.Rear()
 * var param_5 = obj.isEmpty()
 * var param_6 = obj.isFull()
 */
