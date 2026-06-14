class Solution {
    public:
        int lengthAfterTransformations(string s, int t) {
            const int MOD = 1e9 + 7;
            vector<long long> c(26, 0);
    
            for (char ch : s) {
                c[ch - 'a']++;
            }
    
            vector<vector<long long>> transformations(t + 1, vector<long long>(26, 0));
            transformations[0] = c;
    
            bool cycleDetected = false;
            int cycleLength = 0;
    
            for (int i = 1; i <= t; ++i) {
                vector<long long> newC(26, 0);
                for (int j = 0; j < 26; ++j) {
                    if (c[j] == 0) continue;
                    if (j < 25) {
                        newC[j + 1] = (newC[j + 1] + c[j]) % MOD;
                    } else {
                        newC[0] = (newC[0] + c[j]) % MOD;
                        newC[1] = (newC[1] + c[j]) % MOD;
                    }
                }
    
                if (newC == transformations[i - 1]) {
                    cycleDetected = true;
                    cycleLength = i;
                    break;
                }
    
                transformations[i] = newC;
                c = newC;
            }
    
            vector<long long>& finalCounts = cycleDetected ? transformations[t % cycleLength] : transformations[t];
    
            long long result = 0;
            for (int j = 0; j < 26; ++j) {
                result = (result + finalCounts[j]) % MOD;
            }
    
            return result;
        }
    };