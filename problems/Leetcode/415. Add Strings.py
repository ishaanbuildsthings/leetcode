class Solution:
    def addStrings(self, num1: str, num2: str) -> str:
        # could do one while loop where we optionally add numbers if they fit in
        resArrBack = []
        i = len(num1)- 1
        j = len(num2) - 1
        carry = 0
        while i >= 0 and j >= 0:
            tot = carry + int(num1[i]) + int(num2[j])
            newCarry = tot // 10
            newVal = tot % 10
            resArrBack.append(str(newVal))
            carry = newCarry
            i -= 1
            j -= 1
        while i>=0:
            tot = carry + int(num1[i])
            newCarry = tot // 10
            newVal = tot % 10
            resArrBack.append(str(newVal))
            carry = newCarry
            i -=1
        while j>=0:
            tot = carry + int(num2[j])
            newCarry = tot // 10
            newVal = tot % 10
            resArrBack.append(str(newVal))
            carry = newCarry
            j -= 1
        if carry:
            resArrBack.append(str(carry))
        return ''.join(resArrBack[::-1])