class Solution:
    def findWords(self, words: List[str]) -> List[str]:
        rows = [
            'qwertyuiop',
            'asdfghjkl',
            'zxcvbnm'
        ]
        # can simplify
        return [
            w for w in words if all(
                c.lower() in rows[0] for c in w
            ) or all(
                c.lower() in rows[1] for c in w
            ) or all(
                c.lower() in rows[2] for c in w
            )
        ]