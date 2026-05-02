#include <bits/stdc++.h>
using namespace std;
using ll = long long;

int main() {
    cin.tie(nullptr);
    ios::sync_with_stdio(false);
	int n; cin >> n;
	vector<vector<int>> adj(n);
	for (int i = 0; i < n - 1; i++) {
	    int a, b; cin >> a >> b; a--; b--;
	    adj[a].push_back(b);
	    adj[b].push_back(a);
	}
	
	vector<char> isPrime(n, 1); // 1 means prime
	isPrime[0] = 0;
	isPrime[1] = 0;
	for (int factor = 2; factor < n; factor++) {
	    if (isPrime[factor] == 0) continue;
	    for (int mult = 2; factor * mult < n; mult++) {
	        isPrime[factor * mult] = 0;
	    }
	}
	
	vector<int> primes;
	for (int i = 0; i < n; i++) {
	    if (isPrime[i]) primes.push_back(i);
	}

	vector<int> distCount(n); // count of distances
	vector<char> removed(n, 0);
	vector<int> sz(n);
	int maxTouchedDist = 0;
	
	auto getSize = [&](auto&& self, int node, int parent) -> void {
	    int szHere = 1;
	    for (auto adjN : adj[node]) {
	        if (adjN == parent) continue;
	        if (removed[adjN]) continue;
	        self(self, adjN, node);
	        szHere += sz[adjN];
	    }
	    sz[node] = szHere;
	};
	
	auto findCentroid = [&](auto&& self, int node, int parent, int pieceSize) -> int {
	  int mxSz = 0;
	  int heavy = -1;
	  for (auto adjN : adj[node]) {
	      if (adjN == parent) continue;
	      if (removed[adjN]) continue;
	      if (sz[adjN] > mxSz) {
	          mxSz = sz[adjN];
	          heavy = adjN;
	      }
	  }
	  if (mxSz <= pieceSize / 2) {
	      return node;
	  }
	  return self(self, heavy, node, pieceSize);
	};
	
    auto fillBranch = [&](auto&& self, int node, int parent, int dist) -> void {
        distCount[dist]++;
        for (auto adjN : adj[node]) {
            if (adjN == parent || removed[adjN]) continue;
            self(self, adjN, node, dist + 1);
        }
    };
    
    ll primePaths = 0;
    
    auto scoreBranch = [&](auto&& self, int node, int parent, int dist) -> void {
        maxTouchedDist = max(maxTouchedDist, dist);
          for (int prime : primes) {
              int req = prime - dist;
              if (req < 0) continue;
              primePaths += distCount[req];
          }
          for (auto adjN : adj[node]) {
              if (adjN == parent || removed[adjN]) continue;
              self(self, adjN, node, dist + 1);
          }
    };
    
    auto decompose = [&](auto&& self, int entry) -> void {
        getSize(getSize, entry, -1);
        int pieceSize = sz[entry];
        
        int centroid = findCentroid(findCentroid, entry, -1, pieceSize);
        
        distCount[0] = 1;
        
        for (auto adjN : adj[centroid]) {
            if (removed[adjN]) continue;
            scoreBranch(scoreBranch, adjN, centroid, 1);
            fillBranch(fillBranch, adjN, centroid, 1);
        }
        
        for (int distance = 0; distance <= maxTouchedDist; distance++) {
            distCount[distance] = 0;
        }
        maxTouchedDist = 0;
        
        removed[centroid] = true;
        
        for (auto adjN : adj[centroid]) {
            if (removed[adjN]) continue;
            self(self, adjN);
        }
    };
    
    decompose(decompose, 0);
    
    ll paths = (ll)n * (n - 1) / 2;
    
    cout << fixed << setprecision(10) << (double)primePaths / (double)paths << '\n';
}
