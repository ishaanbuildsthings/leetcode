// https://leetcode.com/problems/reverse-linked-list/description/
// Difficulty: Easy
// tags: linked list
/*
Given the head of a singly linked list, reverse the list, and return the reversed list.
*/

// notes: see the bottom for a good way to write out recursive callstacks

// Solution 1, iterative
// O(n) time to iterate through the list and O(1) storage. Maintain a pointer to the previous node, memo the next node, rewire the connection, and iterate.

const reverseList = function (head) {
  let prev = null; // track the previous node
  while (head) {
    const next = head.next;
    head.next = prev;
    prev = head; // maintain a pointer for previous
    head = next; // iterate
  }
  return prev;
};

// Solution 2, recursive, O(n) time and O(n) space
/*
Iterate down until our base case, which is we are at the last node. If we are at the last node, bubble that node up to the top. After we bubble it up once, rewire the next node to point to the current node, and the current point. Rewiring the current node to point to null isn't super needed, because each nodes .next pointer gets rewired anyway, but for the new tail of the list it is needed. Also handle the edge case where the initial node passed in is null.
*/

var reverseList2 = function (node) {
  // if we are null, return nothing, edge case if the linked list being passed in is null
  if (!node) {
    return null;
  }

  // if we have another node, recurse on that node, then wire that node in, return our own node
  if (node.next) {
    const lastNode = reverseList(node.next);
    node.next.next = node;
    node.next = null;
    return lastNode;
  }

  // if we are the last node, return the last node
  return node;
};

// Solution 3, another form of recursion
/*
Do the same thing as solution 2, but grab the tail in a separate variable, and rewire the tail to point to null at the end. Use a closure as well.
*/

var reverseList3 = function (head) {
  if (!head) return null;

  let newHead;
  function recurse(node) {
    if (node.next === null) {
      newHead = node; // grab the new head for the return
      return node;
    } else {
      recurse(node.next);
      node.next.next = node;
      return node;
    }
  }

  recurse(head);
  head.next = null;
  return newHead;
};

// example of writing out recursive callstack, not necessarily correct steps for the recursive solutions here
/*
we have a list
1->2->3->
^
get the next node from recurse
1) wire 2 into 1, return 1


1->2->3->
   ^
   get the next node from recurse
   2) wire 3 into 2, return 2


1->2->3->
      ^
      1) we don't have another node, so return 3


*/
