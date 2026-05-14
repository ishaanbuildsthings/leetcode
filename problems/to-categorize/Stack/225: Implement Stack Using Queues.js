// https://leetcode.com/problems/implement-stack-using-queues/description/
// Difficulty: Easy
// tags: stack, queue

// Problem
/*
Simplfied: Implement a stack using only queue(s), queues can only do pop and dequeue.
Detailed:
Implement a last-in-first-out (LIFO) stack using only two queues. The implemented stack should support all the functions of a normal stack (push, top, pop, and empty).

Implement the MyStack class:

void push(int x) Pushes element x to the top of the stack.
int pop() Removes the element on the top of the stack and returns it.
int top() Returns the element on the top of the stack.
boolean empty() Returns true if the stack is empty, false otherwise.
*/

// Solution: Time: O(n) for push, O(1) for pop. Space: O(n) if you count the space used by the queue. This implementation assumes an O(1) dequeue but in practice the native JS shift operation is O(n).
/*
Consider a stack and a queue:
stack: [
queue: [
  Push a 1
stack: [1
queue: [1
  Push a 2
  Now we can't just push a 2 on top, because when we dequeue we will get a 1. So add the 2, then dequeue all elements in front of the 2 (O(n)) and add them to the back
  stack:[1, 2
  queue:[2, 1

  To pop, just dequeue.

We can also reverse it, so O(1) for push and O(n) for pop. Simply always push to the back in O(1), but when it is time to pop then dequeue all the elements except the last one (return that element), and add the dequeued elements to the back.

Two queue solutions are the same but just using a second queue to re-arrange things.
*/

var MyStack = function () {
  this.queue = [];
};

MyStack.prototype.push = function (x) {
  const size = this.queue.length;
  this.queue.push(x);
  for (let i = 0; i < size; i++) {
    const element = this.queue.shift();
    this.queue.push(element);
  }
};

MyStack.prototype.pop = function () {
  return this.queue.shift();
};

MyStack.prototype.top = function () {
  return this.queue[0];
};

MyStack.prototype.empty = function () {
  if (this.queue.length === 0) return true;
  return false;
};

/**
 * Your MyStack object will be instantiated and called as such:
 * var obj = new MyStack()
 * obj.push(x)
 * var param_2 = obj.pop()
 * var param_3 = obj.top()
 * var param_4 = obj.empty()
 */
