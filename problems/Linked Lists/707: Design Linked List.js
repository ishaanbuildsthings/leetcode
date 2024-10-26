// https://leetcode.com/problems/design-linked-list/description/
// Difficulty: Medium
// tags: linked list

/*
The main important part of this solution was that I used a dummy node to make things easier. The dummy node always points to the head of the linked list. If I need to get a certain element, I start iterating from the head, and counting how many elements I have seen. If I need to add something to the head, I simply rewire it. If I need to add to the tail, I iterate to the end of the tail and add a node, etc.
*/

class Node {
  constructor(val) {
    this.val = val;
    this.next = null;
  }
}

var MyLinkedList = function () {
  const dummy = new Node(null);
  this.dummy = dummy; // the head will always be dummy.next
};

/**
DONE
 * @param {number} index
 * @return {number}
 */
// normal indexing
MyLinkedList.prototype.get = function (index) {
  let tail = this.dummy.next;
  let currentIndex = 0; // 0th index points to first node
  while (tail) {
    if (currentIndex === index) {
      return tail.val;
    }
    tail = tail.next;
    currentIndex++;
  }

  // if we didn't find a match, index was too big
  return -1;
};

/**
DONE
 * @param {number} val
 * @return {void}
 */
MyLinkedList.prototype.addAtHead = function (val) {
  const headNode = new Node(val);
  const oldHead = this.dummy.next;
  headNode.next = oldHead;
  this.dummy.next = headNode; // repoint the dummy
};

/**
DONE
 * @param {number} val
 * @return {void}
 */
MyLinkedList.prototype.addAtTail = function (val) {
  const newNode = new Node(val);

  // if we don't have any nodes at all, make the node node the head
  if (!this.dummy.next) {
    this.dummy.next = newNode;
    return;
  }

  let tail = this.dummy.next;
  // we can also iterate using while (tail.next), then after the while loop tail will be pointing at the last element
  while (tail) {
    // we are at the last element, but we need to catch the pointer to tail here before we increment too far
    if (!tail.next) {
      tail.next = newNode;
      break;
    }
    tail = tail.next;
  }
};

/**
 * @param {number} index
 * @param {number} val
 * @return {void}
 DONE
 */
// normal indexing
MyLinkedList.prototype.addAtIndex = function (index, val) {
  const newNode = new Node(val);

  let tail = this.dummy; // start at dummy, since we need to track the pointer before the index
  let currentIndex = 0; // whenever currentIndex equals index, tail is poting where we need to add the insertion

  // also handles the case where index = the length of the linked list, as newNode.next is null, so tail.next will be null
  while (tail) {
    if (currentIndex === index) {
      newNode.next = tail.next;
      tail.next = newNode;
      return;
    }
    tail = tail.next;
    currentIndex++;
  }

  // don't do anything if index was greater than length
};

/**
 * @param {number} index
 * @return {void}
 */
// normal indexing
MyLinkedList.prototype.deleteAtIndex = function (index) {
  let tail = this.dummy; // need to track the previous pointer, so if we need to delete the 0th element, we use dummy to skip over the 0th element
  let currentIndex = 0;

  while (tail.next) {
    // we need to make the deletion, use tail to skip over
    if (currentIndex === index) {
      tail.next = tail.next.next;
      return;
    }
    tail = tail.next;
    currentIndex++;
  }
};

/**
 * Your MyLinkedList object will be instantiated and called as such:
 * var obj = new MyLinkedList()
 * var param_1 = obj.get(index)
 * obj.addAtHead(val)
 * obj.addAtTail(val)
 * obj.addAtIndex(index,val)
 * obj.deleteAtIndex(index)
 */
