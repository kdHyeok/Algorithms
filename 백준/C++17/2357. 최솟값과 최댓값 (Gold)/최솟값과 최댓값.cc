#define _CRT_SECURE_NO_WARNINGS
#include<iostream>
#include<algorithm>
#include<climits>

using namespace std;
#define ll long long

struct dict {
	long long minV, maxV;
};

dict arr[4'000'001];

int N, M;
ll inC;

ll minVal = LLONG_MAX;
ll maxVal = LLONG_MIN;

void init(int index, int left, int right) {
	if (left == right) {
		cin >> arr[index].minV;
		arr[index].maxV = arr[index].minV;
		return;
	}
	int mid = left + (right - left) / 2;

	init(index * 2, left, mid);
	init(index * 2 + 1, mid + 1, right);

	arr[index].minV = min(arr[index * 2].minV, arr[index * 2 + 1].minV);
	arr[index].maxV = max(arr[index * 2].maxV, arr[index * 2 + 1].maxV);
}

ll rangeMin(int index, int left, int right, int st, int ed) {
	if (ed < left || right < st)
		return LLONG_MAX;

	if ((left == right) || (st <= left && right <= ed)) {
		return arr[index].minV;
	}

	int mid = left + (right - left) / 2;

	ll leftN = rangeMin(index * 2, left, mid, st, ed);
	ll rightN = rangeMin(index * 2 + 1, mid + 1, right, st, ed);
	return min(leftN, rightN);
}
ll rangeMax(int index, int left, int right, int st, int ed) {
	if (ed < left || right < st)
		return LLONG_MIN;

	if ((left == right) || (st <= left && right <= ed)) {
		return arr[index].maxV;
	}

	int mid = left + (right - left) / 2;

	ll leftN = rangeMax(index * 2, left, mid, st, ed);
	ll rightN = rangeMax(index * 2 + 1, mid + 1, right, st, ed);
	return max(leftN, rightN);
}

int main() {
	ios_base::sync_with_stdio(false);
	cin.tie(NULL);
	cout.tie(NULL);
	//freopen("sample_input.txt","r",stdin);
	int a, b;

	cin >> N >> M;
	init(1, 1, N);
	for (int i = 1; i <= M; i++) {
		cin >> a >> b;
		minVal = rangeMin(1, 1, N, a, b);
		maxVal = rangeMax(1, 1, N, a, b);
		cout << minVal << " " << maxVal << "\n";
	}
}