class Solution:
    def reverseWords(self, s: List[str]) -> None:
        """
        Do not return anything, modify s in-place instead.
        """
        def reverseSection(l, r):
            i = l
            j = r
            while i < j:
                s[i], s[j] = s[j], s[i]
                i += 1
                j -= 1
            
        reverseSection(0, len(s) - 1) # 1: reverse whole string

        # 2: reverse each section
        i = 0
        while i < len(s):
            if s[i] == ' ':
                i += 1
                continue
            j = i
            ending = None
            while j < len(s):
                if s[j] == ' ':
                    ending = j - 1
                    break
                j += 1
            if ending is None:
                ending = len(s) - 1
            reverseSection(i, ending)
            i = j + 1
            
