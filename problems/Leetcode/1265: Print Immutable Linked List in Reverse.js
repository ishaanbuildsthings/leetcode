// https://leetcode.com/problems/print-immutable-linked-list-in-reverse/description/
// Difficulty: Medium
// tags: Linked List, single branch (recursive or iterative), square root decomposition

// Problem
/*
Simplified:
We are given an immutable linked list, and an API that only supports printing the current node val, and getting the next node. Print the nodes in reverse order.

Detailed:
You are given an immutable linked list, print out all values of each node in reverse with the help of the following interface:

ImmutableListNode: An interface of immutable linked list, you are given the head of the list.
You need to use the following functions to access the linked list (you can't access the ImmutableListNode directly):

ImmutableListNode.printValue(): Print value of the current node.
ImmutableListNode.getNext(): Return the next node.
The input is only given to initialize the linked list internally. You must solve this problem without modifying the linked list. In other words, you must operate the linked list using only the mentioned APIs.
*/

// Solution 1, recursion, O(n) time and O(n) space. If we have a next value, recurse there. Otherwise, print the value.
var printLinkedListInReverse = function (head) {
  if (head.getNext()) {
    printLinkedListInReverse(head.getNext());
  }
  head.printValue();
};

// * Solution 2, square root decomposition, O(n) time and O(root n) space. Get the length of the linked list. Then, for every square-root-th element, store a pointer to it. So we have root n pointers in memory. Then print each root n section in reverse with recursion.

// * Solution 3, O(n^2) time and O(1) space. Just iterate to the relevant node each time.
