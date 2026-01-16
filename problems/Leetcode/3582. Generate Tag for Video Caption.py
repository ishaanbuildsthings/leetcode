class Solution:
    def generateTag(self, caption: str) -> str:        
        arr = []
        word = []
        for c in caption:
            if c == ' ':
                if word:
                    arr.append(''.join(word))
                    word = []
            else:
                word.append(c)
        if word:
            arr.append(''.join(word))

        if not arr:
            return '#'

        for i in range(len(arr)):
            w = arr[i]
            w = w.lower()
            if i != 0:
                w = w[:1].upper() + w[1:]
            else:
                w = w
            arr[i] = w

        final = '#' + ''.join(arr)
        final = final[:100]
        return final
            
    