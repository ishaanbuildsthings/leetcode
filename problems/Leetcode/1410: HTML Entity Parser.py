# https://leetcode.com/problems/html-entity-parser/
# difficulty: medium
# tags: rolling hash

# Problem
# HTML entity parser is the parser that takes HTML code as input and replace all the entities of the special characters by the characters itself.

# The special characters and their entities for HTML are:

# Quotation Mark: the entity is &quot; and symbol character is ".
# Single Quote Mark: the entity is &apos; and symbol character is '.
# Ampersand: the entity is &amp; and symbol character is &.
# Greater Than Sign: the entity is &gt; and symbol character is >.
# Less Than Sign: the entity is &lt; and symbol character is <.
# Slash: the entity is &frasl; and symbol character is /.
# Given the input text string to the HTML parser, you have to implement the entity parser.

# Return the text after replacing the entities by the special characters.

# Solution
# Kind of reminds me of building a regex engine, we can use a rolling hash or other tricks potentially if needed

HTML_CODES = {
    '&quot;' : '"',
    '&apos;': "'",
    '&amp;': '&',
    '&gt;': '>',
    '&lt;': '<',
    '&frasl;': '/',
}

class Solution:
    def entityParser(self, text: str) -> str:
        resArr = []
        i = 0
        while i < len(text):
            normalCharFlag = True
            for htmlCode in HTML_CODES:
                substring = ''.join(text[i:i + len(htmlCode)])
                if substring == htmlCode:
                    normalCharFlag = False
                    resArr.append(HTML_CODES[htmlCode])
                    i += len(htmlCode)
                    break
            if normalCharFlag:
                resArr.append(text[i])
                i += 1
        return ''.join(resArr)
