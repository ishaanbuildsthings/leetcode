#include<bits/stdc++.h>
using namespace std;

// check if array contains a value
vector<int> arr(100);
int value = 10;
bool exists = find(arr.begin(), arr.end(), value) != arr.end();