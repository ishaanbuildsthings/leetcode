import sys
from collections import deque, defaultdict

def solve():

  data = sys.stdin.read().strip().split()
  it = iter(data)
  
  n, m = map(int, (next(it), next(it)))
  
  adj = defaultdict(lambda: defaultdict(set)) # adj[A][B] is a set of letters
  
  # adjacency list: g[u] = list of (v, ch)
  g = [[] for _ in range(n + 1)]
  
  for _ in range(m):
      a = int(next(it))
      b = int(next(it))
      c = next(it) # single-letter string
      
      adj[a][b].add(c)
      adj[b][a].add(c)
  
  
  
  q = deque()
  q.append((1, n))
  seen = set()
  seen.add((1, n))
  steps = 0
  while q:
    length = len(q)
    hasPlusOne = False
    for _ in range(length):
      node1, node2 = q.popleft()
      if node1 == node2:
        print(steps)
        return
      if node2 in adj[node1] and len(adj[node1][node2]):
        hasPlusOne = True
      for adj1 in adj[node1]:
        for adj2 in adj[node2]:
          for letter in adj[node1][adj1]:
            if letter in adj[node2][adj2]:
              newTup = (adj1, adj2)
              if newTup in seen:
                continue
              seen.add(newTup)
              q.append(newTup)
    if hasPlusOne:
      print(steps + 1)
      return
    steps += 2
  
  print(-1)
    
if __name__ == "__main__":
    solve()