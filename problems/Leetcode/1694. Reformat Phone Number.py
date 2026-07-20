class Solution:
    def reformatNumber(self, number: str) -> str:
        a = [char for char in number if char not in ' -']
        print(a)

        blocks = []
        remain = len(a)
        currI = 0
        while remain > 4:
            block = [a[currI], a[currI+1], a[currI+2]]
            currI += 3
            blocks.append(block)
            remain -= 3
        remaining = a[currI:]
        if len(remaining) == 4:
            blocks.append([a[currI], a[currI+1]])
            blocks.append([a[currI+2],a[currI+3]])
        else:
            blocks.append(a[currI:])
        blocks = [''.join(block) for block in blocks]
        return '-'.join(blocks)