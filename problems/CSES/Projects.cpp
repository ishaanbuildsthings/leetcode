#include <iostream>
#include <vector>
#include <algorithm>
#include <map>
using namespace std;
 
struct Project {
    long long start, end, val;
    bool operator<(const Project& other) const {
        return start < other.start;
    }
};
 
int numProjects;
vector<Project> projects;
vector<long long> starts;
map<int, long long> cache;
 
int firstIndexGT(vector<long long>& arr, long long threshold) {
    return upper_bound(arr.begin(), arr.end(), threshold) - arr.begin();
}
 
long long dp(int i) {
    if (i == projects.size()) {
        return 0;
    }
    if (cache.find(i) != cache.end()) {
        return cache[i];
    }
    long long ifTake = projects[i].val + dp(firstIndexGT(starts, projects[i].end));
    long long ifSkip = dp(i + 1);
    long long ans = max(ifSkip, ifTake);
    cache[i] = ans;
    return ans;
}
 
int main() {
    cin >> numProjects;
    projects.resize(numProjects);
    starts.resize(numProjects);
 
    for (int i = 0; i < numProjects; i++) {
        cin >> projects[i].start >> projects[i].end >> projects[i].val;
        starts[i] = projects[i].start;
    }
 
    sort(starts.begin(), starts.end());
    sort(projects.begin(), projects.end());
 
    cout << dp(0) << endl;
 
    return 0;
}