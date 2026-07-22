class Solution:
    def validIPAddress(self, queryIP: str) -> str:
        
        def is4(s):
            vals = s.split('.')
            if any(not x.isdigit() for x in vals):
                return False
            if len(vals) != 4:
                return False
            if any(x[0] == '0' and len(x) > 1 for x in vals):
                return False
            a, b, c, d = map(int, vals)
            if max(a, b, c, d) > 255:
                return False
            return True
        
        def is6(s):
            vals = s.split(':')
            if len(vals) != 8:
                return False
            if any(len(x) > 4 or len(x) == 0 for x in vals):
                return False
            if any(not y.isdigit() and y not in 'abcdefABCDEF' for x in vals for y in x):
                return False
            return True
        
        if is4(queryIP):
            return 'IPv4'
        if is6(queryIP):
            return 'IPv6'
        return 'Neither'
            
