class Solution:
    def countValidWords(self, sentence: str) -> int:
        words = [w for w in sentence.split(' ') if w != '']

        def isValid(token):
            if any(token[i] in '!.,' for i in range(len(token) - 1)):
                return False
            if Counter(token)['-'] > 1:
                return False
            if any(token[i].isdigit() for i in range(len(token))):
                return False
            for i in range(len(token)):
                if token[i] == '-':
                    if not i or i == len(token) - 1:
                        return False
                    if not token[i-1].isalpha() or not token[i+1].isalpha():
                        return False
            return True
        
        return sum(
            isValid(w) for w in words
        )