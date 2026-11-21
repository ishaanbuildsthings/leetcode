// https://leetcode.com/problems/reverse-nodes-in-k-group/description/
// Difficulty: Hard

// Problem
/*
Simplified:
1->2->3->4->5->
return: 2->1->4->3->5->

Given a linked list, reverse the nodes of a linked list k at a time and return its modified list. If there are fewer than k elements in a group, leave them.
*/

// Solution 1, O(n) time and O(1) space, using an iterative solution
/*
Create a dummy pointing to the head, so at the end we can return dummy.next. Find a group head, validate its long enough, reverse the group, rewiring things as needed (see solution 2 for more details on the rewiring), then update the group head.
*/
var reverseKGroup = function (head, k) {
  let groupHead = head;
  const dummy = new ListNode();
  dummy.next = head;
  let prev = dummy;

  while (groupHead) {
    let savePrev = prev; // we need to rewire the previous into the start of the newly reversed list, so D->1->2 becomes D<-1<-2, then rewire so D points to to

    // validate length
    let steps = 0;
    let groupTail = groupHead;
    while (groupTail && steps < k) {
      groupTail = groupTail.next;
      steps++;
    }
    if (steps < k) {
      break;
    }

    // reverse the group
    let reversalSteps = 0;
    while (reversalSteps < k) {
      const temp = groupHead.next;
      groupHead.next = prev;
      prev = groupHead;
      groupHead = temp;
      reversalSteps++;
    }
    // now, previous is the head of our reversed list, groupHead is the head of the next list to be reversed

    const tailOfReversed = savePrev.next;
    savePrev.next = prev; // rewire D into new head
    tailOfReversed.next = groupHead;
    prev = tailOfReversed; // set up the new previous one for next loop
  }

  return dummy.next;
};

// Solution, O(n) time and O(n/k) space, due to the recursive call stack

/*
Consider this list: 1->2->3->4->5->

What we need to do is:
1) determine if we have enough elements to reverse
2) if we don't, we are done, return the head
3) if we do, reverse the elements: 2->1->3->4->5->
4) call the function again on the next group, which starts at 3
5) we also need to wire the 1 into the 4, since after we reverse 3->4 to be 4->3, 1 needs to point to 4

To do this, we can make a function accept the head of the list we are trying reverse, and the previous list ending which should be wired in. Then check if we have enough elements to reverse. If we do, reverse it. Then call the function again on the the next group head, and the current group ending.

Use a dummy node as our initial 'previous list ending', then, dummy.next will automatically be the final head of the list. See Solution 2 for the way to do it without the dummy node, which is basically the same thing, but checking if the previousEnding is null.

*/

var reverseKGroup = function (head, k) {
  const dummy = new ListNode();
  dummy.next = head;

  // take in a list node
  function reverseGroup(groupHead, previousEnding) {
    // validate we have enough to flip
    let curr = groupHead;
    let stepsTaken = 0;
    while (curr && stepsTaken < k) {
      curr = curr.next;
      stepsTaken++;
    }
    // if we didn't have enough elements to reverse, we are DONE
    if (stepsTaken < k) {
      return;
    }

    // we need to reverse into this
    let prev = curr;

    // reverse
    curr = groupHead;
    for (let i = 0; i < k; i++) {
      const temp = curr.next;
      curr.next = prev;
      prev = curr;
      curr = temp;
    }
    // now curr points to the head of the next group we need to reverse
    // prev points to the head of the list

    // groupHead points to the last element in our newly reversed list, since it started as the head but is now reversed

    if (previousEnding) {
      previousEnding.next = prev;
    }

    reverseGroup(curr, groupHead);
  }

  reverseGroup(head, dummy);

  return dummy.next;
};

/*
1->2->3->4->5->

2->1->3->4->5->

identify previous as the 3, reverse down
then, run the function again at 3

*/

// * Solution 2, same thing but no dummy node

var reverseKGroup = function (head, k) {
  let finalHead;

  // take in a list node
  function reverseGroup(groupHead, previousEnding) {
    // validate we have enough to flip
    let curr = groupHead;
    let stepsTaken = 0;
    while (curr && stepsTaken < k) {
      curr = curr.next;
      stepsTaken++;
    }
    // if we didn't have enough elements to reverse, we are DONE
    if (stepsTaken < k) {
      return;
    }

    // we need to reverse into this
    let prev = curr;

    // reverse
    curr = groupHead;
    for (let i = 0; i < k; i++) {
      const temp = curr.next;
      curr.next = prev;
      prev = curr;
      curr = temp;
    }
    // now curr points to the head of the next group we need to reverse
    // prev points to the head of the list
    if (previousEnding === null) {
      finalHead = prev;
    }

    // groupHead points to the last element in our newly reversed list, since it started as the head but is now reversed

    if (previousEnding) {
      previousEnding.next = prev;
    }

    reverseGroup(curr, groupHead);
  }

  reverseGroup(head, null);

  return finalHead;
};

/*
1->2->3->4->5->

2->1->3->4->5->

identify previous as the 3, reverse down
then, run the function again at 3

*/
