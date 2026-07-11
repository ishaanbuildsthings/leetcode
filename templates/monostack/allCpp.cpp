// nearest index to the left that is strictly smaller than arr[i]
// -1 if none, pop while arr[st.back()] >= arr[i]
template <typename T>
vector<int> rightmostOnLeftLtNum(const vector<T>& arr) {
    int n = arr.size();
    vector<int> st, res(n, -1);
    for (int i = 0; i < n; i++) {
        while (!st.empty() && arr[st.back()] >= arr[i]) st.pop_back();
        res[i] = st.empty() ? -1 : st.back();
        st.push_back(i);
    }
    return res;
}

// nearest index to the left that is smaller than or equal to arr[i]
// -1 if none, pop while arr[st.back()] > arr[i]
template <typename T>
vector<int> rightmostOnLeftLteNum(const vector<T>& arr) {
    int n = arr.size();
    vector<int> st, res(n, -1);
    for (int i = 0; i < n; i++) {
        while (!st.empty() && arr[st.back()] > arr[i]) st.pop_back();
        res[i] = st.empty() ? -1 : st.back();
        st.push_back(i);
    }
    return res;
}

// nearest index to the left that is strictly greater than arr[i]
// -1 if none, pop while arr[st.back()] <= arr[i]
template <typename T>
vector<int> rightmostOnLeftGtNum(const vector<T>& arr) {
    int n = arr.size();
    vector<int> st, res(n, -1);
    for (int i = 0; i < n; i++) {
        while (!st.empty() && arr[st.back()] <= arr[i]) st.pop_back();
        res[i] = st.empty() ? -1 : st.back();
        st.push_back(i);
    }
    return res;
}

// nearest index to the left that is greater than or equal to arr[i]
// -1 if none, pop while arr[st.back()] < arr[i]
template <typename T>
vector<int> rightmostOnLeftGteNum(const vector<T>& arr) {
    int n = arr.size();
    vector<int> st, res(n, -1);
    for (int i = 0; i < n; i++) {
        while (!st.empty() && arr[st.back()] < arr[i]) st.pop_back();
        res[i] = st.empty() ? -1 : st.back();
        st.push_back(i);
    }
    return res;
}

// nearest index to the right that is strictly smaller than arr[i]
// n if none, pop while arr[st.back()] >= arr[i]
template <typename T>
vector<int> leftmostOnRightLtNum(const vector<T>& arr) {
    int n = arr.size();
    vector<int> st, res(n, n);
    for (int i = n - 1; i >= 0; i--) {
        while (!st.empty() && arr[st.back()] >= arr[i]) st.pop_back();
        res[i] = st.empty() ? n : st.back();
        st.push_back(i);
    }
    return res;
}

// nearest index to the right that is smaller than or equal to arr[i]
// n if none, pop while arr[st.back()] > arr[i]
template <typename T>
vector<int> leftmostOnRightLteNum(const vector<T>& arr) {
    int n = arr.size();
    vector<int> st, res(n, n);
    for (int i = n - 1; i >= 0; i--) {
        while (!st.empty() && arr[st.back()] > arr[i]) st.pop_back();
        res[i] = st.empty() ? n : st.back();
        st.push_back(i);
    }
    return res;
}

// nearest index to the right that is strictly greater than arr[i]
// n if none, pop while arr[st.back()] <= arr[i]
template <typename T>
vector<int> leftmostOnRightGtNum(const vector<T>& arr) {
    int n = arr.size();
    vector<int> st, res(n, n);
    for (int i = n - 1; i >= 0; i--) {
        while (!st.empty() && arr[st.back()] <= arr[i]) st.pop_back();
        res[i] = st.empty() ? n : st.back();
        st.push_back(i);
    }
    return res;
}

// nearest index to the right that is greater than or equal to arr[i]
// n if none, pop while arr[st.back()] < arr[i]
template <typename T>
vector<int> leftmostOnRightGteNum(const vector<T>& arr) {
    int n = arr.size();
    vector<int> st, res(n, n);
    for (int i = n - 1; i >= 0; i--) {
        while (!st.empty() && arr[st.back()] < arr[i]) st.pop_back();
        res[i] = st.empty() ? n : st.back();
        st.push_back(i);
    }
    return res;
}