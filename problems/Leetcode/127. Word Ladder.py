class Solution:
    def ladderLength(self, beginWord: str, endWord: str, wordList: List[str]) -> int:
        if endWord not in wordList:
            return 0
        wordList.append(beginWord)
        wordList.append(endWord)
        blanks = defaultdict(list) # abc_efg -> list of words with that format
        for w in wordList:
            for i in range(len(w)):
                nw = w[:i] + '_' + w[i+1:]
                blanks[nw].append(w)
        adj = defaultdict(list)
        for w in wordList:
            for i in range(len(w)):
                nw = w[:i] + '_' + w[i+1:]
                for adjNode in blanks[nw]:
                    if adjNode != w:
                        adj[w].append(adjNode)
        q = deque()
        q.append(beginWord)
        steps = 0
        seen = {beginWord}
        while q:
            length = len(q)
            for _ in range(length):
                w = q.popleft()
                if w == endWord:
                    return steps + 1
                for adjN in adj[w]:
                    if adjN in seen:
                        continue
                    seen.add(adjN)
                    q.append(adjN)
            steps += 1
        return 0