// https://leetcode.com/problems/add-two-numbers-ii/description/
// Difficulty: Medium
// Tags: linked list

// Problem
/*
You are given two non-empty linked lists representing two non-negative integers. The most significant digit comes first and each of their nodes contains a single digit. Add the two numbers and return the sum as a linked list.

You may assume the two numbers do not contain any leading zero, except the number 0 itself.
*/

// Solution, O(n) time, O(n) space
/*
First, create reversed linked lists. I ended up just storing nodes in reverse order in an array.

Then, as long as we have both digits, add and carry.

Once we run out of both digits, just add the leftover, remembering to carry it.

All while doing this, construct the new linked list, by tracking the previous node (node to be wired into).
*/

var addTwoNumbers = function (l1, l2) {
  // maps a node to its previous node for list
  const nodes1 = [];
  const nodes2 = [];

  let current = l1;
  while (current) {
    nodes1.push(current);
    current = current.next;
  }
  current = l2;
  while (current) {
    nodes2.push(current);
    current = current.next;
  }

  const list1Reversed = nodes1.reverse();
  const list2Reversed = nodes2.reverse();

  let i1 = 0;
  let i2 = 0;

  let nodeToBeWiredInto = null;
  let carry = 0;

  // add as long as we have both digits
  while (i1 < list1Reversed.length && i2 < list2Reversed.length) {
    const sum = list1Reversed[i1].val + list2Reversed[i2].val + carry;
    if (sum > 9) {
      carry = 1;
      const newSum = sum - 10;
      const newNode = new ListNode(newSum);
      newNode.next = nodeToBeWiredInto;
      nodeToBeWiredInto = newNode;
    } else if (sum <= 9) {
      carry = 0;
      const newNode = new ListNode(sum);
      newNode.next = nodeToBeWiredInto;
      nodeToBeWiredInto = newNode;
    }
    i1++;
    i2++;
  }

  // if we still have extra digits from l1, add those
  while (i1 < list1Reversed.length) {
    let newSum = list1Reversed[i1].val + carry;

    if (newSum > 9) {
      carry = 1;
      newSum -= 10;
    } else if (newSum <= 9) {
      carry = 0;
    }

    const newNode = new ListNode(newSum);
    newNode.next = nodeToBeWiredInto;
    nodeToBeWiredInto = newNode;
    i1++;
  }
  // or if we had extra digits from l2
  while (i2 < list2Reversed.length) {
    let newSum = list2Reversed[i2].val + carry;

    if (newSum > 9) {
      carry = 1;
      newSum -= 10;
    } else if (newSum <= 9) {
      carry = 0;
    }

    const newNode = new ListNode(newSum);
    newNode.next = nodeToBeWiredInto;
    nodeToBeWiredInto = newNode;
    i2++;
  }

  if (carry === 1) {
    const newNode = new ListNode(1);
    newNode.next = nodeToBeWiredInto;
    nodeToBeWiredInto = newNode;
  }

  return nodeToBeWiredInto;
};
