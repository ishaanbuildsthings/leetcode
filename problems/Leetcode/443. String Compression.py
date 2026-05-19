class Solution:
    def compress(self, chars: List[str]) -> int:
        read = write = 0
        n = len(chars)
        while read < n:
            # find consecutive streak
            j = read + 1
            # find first difference
            while j < n and chars[j] == chars[read]:
                j += 1
            # read...j-1 are the same
            width = (j-1) - read + 1
            if width == 1:
                chars[write] = chars[read]
                write += 1
                read += 1
                continue
            
            digits = str(width)
            chars[write] = chars[read]
            write += 1
            for i in range(len(digits)):
                chars[write] = digits[i]
                write += 1
            
            read = j
        
        return write

