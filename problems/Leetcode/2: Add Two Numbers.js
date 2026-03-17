// https://leetcode.com/problems/add-two-numbers/description/
// Difficulty: Medium

// Problem
/*
You are given two non-empty linked lists representing two non-negative integers. The digits are stored in reverse order, and each of their nodes contains a single digit. Add the two numbers and return the sum as a linked list.

You may assume the two numbers do not contain any leading zero, except the number 0 itself.
Input: l1 = [2,4,3], l2 = [5,6,4]
Output: [7,0,8]
Explanation: 342 + 465 = 807.
*/

// Solution, O(n) time and O(1) space
/*
Iterate over both linked lists, adding the results. If we get a carry, store that. On the next iteration, make sure to use that carry, then reset it before adding again. If we run out of a linked list, just keep adding the remaining linked list. If we end with a carry such as [9] + [9] then we need to add one more node to the end. I used a dummy node because it made more sense with the creation of the result nodes. For instance if we initialize a result node without a dummy, when we add two numbers we can populate the value, but if we create a new node for the next numbers to be added, we also have to check to make sure we have more numbers to add. Whereas the dummy node is offset by one, so every time we add, we create a node and append it to the dummy. We could also not use a dummy, but create the head of the linked list for the first time we add, though the code is more annoying to implement.
*/

var addTwoNumbers = function (l1, l2) {
  // will point to the head of our result
  const dummy = new ListNode();
  let head = dummy;

  let carry = 0;

  // while we at least one node, add them
  while (l1 || l2) {
    let sum;
    if (l1 && l2) {
      sum = l1.val + l2.val + carry;
    } else if (l1) {
      sum = l1.val + carry;
    } else if (l2) {
      sum = l2.val + carry;
    }
    // reset the carry after we use it
    carry = 0;
    if (sum >= 10) {
      carry = 1;
      sum = sum % 10;
    }
    head.next = new ListNode(sum);
    head = head.next;

    if (l1) {
      l1 = l1.next;
    }
    if (l2) {
      l2 = l2.next;
    }
  }
  if (carry === 1) {
    head.next = new ListNode(1);
  }

  return dummy.next;
};
