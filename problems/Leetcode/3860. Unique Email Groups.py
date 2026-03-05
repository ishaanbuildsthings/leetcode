class Solution:
    def uniqueEmailGroups(self, emails: list[str]) -> int:
        s = set()
        for e in emails:
            l, r = e.split('@')
            l = l.split('+')[0]
            l = l.replace('.', '')
            l = l.lower()
            r = r.lower()
            s.add((l, r))
        return len(s)