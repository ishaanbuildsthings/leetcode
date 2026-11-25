/**
 * Definition for singly-linked list.
 * function ListNode(val, next) {
 *     this.val = (val===undefined ? 0 : val)
 *     this.next = (next===undefined ? null : next)
 * }
 */
/**
 * @param {ListNode} head
 * @return {ListNode}
 */
var doubleIt = function(head) {
    const arrNum = [];
    let pointer = head;
    while (pointer) {
        arrNum.push(pointer.val);
        pointer = pointer.next;
    }
    let carry;
    function doubleArrNum(arr) {
        const reversedArr = arr.reverse();
        // console.log(`reversed arrayu: ${JSON.stringify(reversedArr)}`);
        const doubledArr = [];
        carry = 0;
        for (let i = 0; i < reversedArr.length; i++) {
            const num = reversedArr[i];
            // console.log(`num is: ${num}`);
            const doubledNum = num * 2;
            const finalNum = doubledNum + carry;
            // console.log(`final num is: ${finalNum}`);
            if (finalNum <= 9) {
                doubledArr.push(finalNum);
                carry = 0;
            }
            
            else if (finalNum > 9) {
                doubledArr.push(finalNum - 10);
                carry = 1;
            }
                
        }
        return doubledArr.reverse();
    }
    
    const reversedDoubled = doubleArrNum(arrNum);
    // console.log(`rev doubked: ${JSON.stringify(reversedDoubled)}`);
    
    let dummy = new ListNode();
    let pointer2 = dummy;
    let i = 0;
    for (let i = 0; i < reversedDoubled.length; i++) {
        const newNode = new ListNode(reversedDoubled[i]);
        pointer2.next = newNode;
        pointer2 = pointer2.next;
    }
    if (carry === 1) {
        const newHead = new ListNode(1);
        newHead.next = dummy.next;
        return newHead;
    }
    return dummy.next;
};