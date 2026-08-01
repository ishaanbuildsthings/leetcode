class Solution:
    def interpret(self, command: str) -> str:
        resArr = []
        i = 0
        while i < len(command):
            c = command[i]
            if c == 'G':
                resArr.append('G')
                i += 1
            elif command[i + 1] == 'a':
                resArr.append('al')
                i += 4
            else:
                resArr.append('o')
                i += 2
        return ''.join(resArr)