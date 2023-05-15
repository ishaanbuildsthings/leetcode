// https://leetcode.com/problems/design-an-atm-machine/description/
// Difficulty: Medium
// tags: arrays

// Problem
/*
There is an ATM machine that stores banknotes of 5 denominations: 20, 50, 100, 200, and 500 dollars. Initially the ATM is empty. The user can use the machine to deposit or withdraw any amount of money.

When withdrawing, the machine prioritizes using banknotes of larger values.

For example, if you want to withdraw $300 and there are 2 $50 banknotes, 1 $100 banknote, and 1 $200 banknote, then the machine will use the $100 and $200 banknotes.
However, if you try to withdraw $600 and there are 3 $200 banknotes and 1 $500 banknote, then the withdraw request will be rejected because the machine will first try to use the $500 banknote and then be unable to use banknotes to complete the remaining $100. Note that the machine is not allowed to use the $200 banknotes instead of the $500 banknote.
*/

// Solution
/*
Deposit is simple, we just add the relevant notes to the ATM. For withdrawing, our main loop condition is that we can loop over each bill type, withdrawing as many as possible until we cannot anymore, then proceeding. Instead of withdrawing one at a time, comparing our remaining amount, and loop (total time complexity = # of bills in the machine, since we could draw each bill one by one), we can calculate with math exactly how many we could withdraw, and the time complexity becomes bound by the # of bill types.
*/

// O(k) time where k is the # of bill types (in this case it's constant), and O(k) space

var ATM = function () {
  this.notes = {
    20: 0,
    50: 0,
    100: 0,
    200: 0,
    500: 0,
  };
};

ATM.prototype.deposit = function (banknotesCount) {
  this.notes[20] += banknotesCount[0];
  this.notes[50] += banknotesCount[1];
  this.notes[100] += banknotesCount[2];
  this.notes[200] += banknotesCount[3];
  this.notes[500] += banknotesCount[4];
};

const BILL_TYPES = [20, 50, 100, 200, 500];

ATM.prototype.withdraw = function (amount) {
  const billsWithdrawn = {
    20: 0,
    50: 0,
    100: 0,
    200: 0,
    500: 0,
  };
  let withdrawn = 0;

  // iterate through the bill types backwards
  for (let i = BILL_TYPES.length - 1; i >= 0; i--) {
    const denomination = BILL_TYPES[i];
    let amountLeftNeeded = amount - withdrawn;
    let maxBeforeOverflow = Math.floor(amountLeftNeeded / denomination);
    const maxWithdrawable = Math.min(
      maxBeforeOverflow,
      this.notes[denomination]
    );
    withdrawn += maxWithdrawable * denomination;
    billsWithdrawn[denomination] += maxWithdrawable;
  }

  if (withdrawn !== amount) {
    return [-1];
  }

  const result = [];
  for (const billType in billsWithdrawn) {
    result.push(billsWithdrawn[billType]);
    this.notes[billType] -= billsWithdrawn[billType];
  }

  return result;
};

/**
 * Your ATM object will be instantiated and called as such:
 * var obj = new ATM()
 * obj.deposit(banknotesCount)
 * var param_2 = obj.withdraw(amount)
 */
