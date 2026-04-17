class Solution:
    def simplifyPath(self, path: str) -> str:
        dirs = path.split('/')
        stack = []
        for dir in dirs:
            if dir == '..' and stack:
                stack.pop()
            elif dir not in ['.', '..', '']:
                stack.append(dir)
        return '/' + '/'.join(stack)