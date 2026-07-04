# """
# This is FontInfo's API interface.
# You should not implement it, or speculate about its implementation
# """
#class FontInfo(object):
#    Return the width of char ch when fontSize is used.
#    def getWidth(self, fontSize, ch):
#        """
#        :type fontSize: int
#        :type ch: char
#        :rtype int
#        """
# 
#    def getHeight(self, fontSize):
#        """
#        :type fontSize: int
#        :rtype int
#        """
class Solution:
    def maxFont(self, text: str, w: int, h: int, fonts: List[int], fontInfo : 'FontInfo') -> int:
        l = 0
        r = len(fonts) - 1
        resI = None
        while l <= r:
            m = (r + l) // 2 # the index in fonts we will try
            fontSize = fonts[m]
            width = 0
            height = fontInfo.getHeight(fontSize)
            for c in text:
                width += fontInfo.getWidth(fontSize, c)
            if height > h or width > w:
                r = m - 1
            else:
                resI = m
                l = m + 1
        
        return fonts[resI] if resI is not None else -1
            