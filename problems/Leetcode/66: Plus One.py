class Solution:
    def plusOne(self, digits: List[int]) -> List[int]:
        
        #adds 1 to last digit and sets pointer to last digit
        digits[-1] += 1
        pointer = len(digits) - 1
        
        
        #while the last digit is 10
        while digits[pointer] == 10:
            #incremenet the previous digit
            if pointer-1 < 0:
                digits.insert(0, 1)
                digits[pointer+1] = 0
                return digits
            else:
                digits[pointer-1] += 1
            #set the last digit to 0
            digits[pointer] = 0
            #move the pointer
            pointer -= 1
            
        
        return digits
        print(digits)
        
#9, 9
#9, 10
#10, 10
#


        
        
            