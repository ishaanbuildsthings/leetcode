class Solution:
    def validWordAbbreviation(self, word: str, abbr: str) -> bool:
        buckets = []
        string = ''
        number = ''
        n = len(abbr)
        for i in range(n):
            if not abbr[i].isdigit():
                if number:
                    buckets.append(number)
                    number = ''
                string += abbr[i]
            else:
                if string:
                    buckets.append(string)
                    string = ''
                number += abbr[i]
                if number == '0':
                    return False
        if number:
            buckets.append(number)
        if string:
            buckets.append(string)
        
        i = 0
        for j in range(len(buckets)):
            block = buckets[j]
            if block[0].isalpha():
                for v in block:
                    if i == len(word):
                        return False
                    if word[i] != v:
                        return False
                    i += 1
            else:
                i += int(block)
                if i > len(word):
                    return False
                    
        return i == len(word)
                

                