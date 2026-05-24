class Solution:
    def smallestPalindrome(self, s: str) -> str:
        c = Counter(s)
        ABC = 'abcdefghijklmnopqrstuvwxyz'
        resArr = [None] * len(s)
        i = 0 # letter pointer
        
        middleLetter = None
        for letter in ABC:
            if c[letter] % 2 == 1:
                middleLetter = letter
        
        # print(middleLetter)
        
        # result pointer
        for j in range(len(s)):
            if j == len(s) // 2:
                break
            # print(f'looping on j={j}')
            if resArr[j] is not None:
                break
            # find the next we can decrement
            while i < 26 and (c[ABC[i]] == 0 or c[ABC[i]] == 1):
                # print(f'i now: {i}')
                i += 1
            # print(f'i is: {i}')
                
            # print(f'taken letter: {ABC[i]}')
            resArr[j] = ABC[i]
            # print(f'j is: {j}')
            
            right = len(s) - j - 1
            resArr[right] = ABC[i]
            
            if right == j:
                break
                c[ABC[i]] -= 1
            else:
                c[ABC[i]] -= 2
                
        # print(middleLetter)
        
        if middleLetter is not None:
            middle = len(s) // 2
            resArr[middle] = middleLetter
        
        return ''.join(resArr)
            
            
                
            