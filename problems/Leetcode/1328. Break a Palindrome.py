class Solution:
    def breakPalindrome(self, palindrome: str) -> str:
        if len(palindrome) == 1:
            return ''
        if palindrome.count('a') == len(palindrome):
            return ('a' * (len(palindrome) - 1)) + 'b'
        
        # not all a's, we want to turn any letter into an a (except the middle letter)
        for i in range(len(palindrome)):
            if len(palindrome) % 2 == 1 and i == len(palindrome) // 2:
                continue
            if palindrome[i] != 'a':
                return palindrome[:i] + 'a' + palindrome[i+1:]
        
        # failsafe for case like aba
        return palindrome[:-1] + 'b'