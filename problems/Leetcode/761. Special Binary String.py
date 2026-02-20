class Solution:
    def makeLargestSpecial(self, s: str) -> str:
        blocks = [] # find smallest blocks that we can independently move around

        oneSurplus = 0
        start = 0

        for i, v in enumerate(s):
            if v == '1':
                oneSurplus += 1
            else:
                oneSurplus -= 1
            if oneSurplus == 0:
                blocks.append(s[start:i+1])
                start = i + 1
        
        # one single mountain
        if len(blocks) == 1:
            block = blocks[0]
            if len(block) == 2:
                return block
            return '1' + self.makeLargestSpecial(block[1:-1]) + '0'
        
        resArr = [
            self.makeLargestSpecial(b) for b in blocks
        ]
        resArr.sort(reverse=True)
        return ''.join(resArr)