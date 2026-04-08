#define _CRT_SECURE_NO_WARNINGS
#include <iostream>
#include <vector>
#include <cstring>

using namespace std;

int D, W, K;
vector<vector<int>> map(21, vector<int>(21, 0));
vector<vector<int>> copy_map(21, vector<int>(21, 0));

bool test() {
	for (int col = 0; col < W; col++) {
		int type = map[0][col];
		int cnt = 1;
		for (int i = 1; i < D; i++)
		{
			if (type == map[i][col]) {
				cnt++;
				if (cnt >= K)
					break;
			}
			else {
				type = map[i][col];
				cnt = 1;
			}
		}
		if (cnt < K)
			return false;
	}
	return true;
}

void dfs(int& ans, int idx, int cnt) {
	if (ans <= cnt || cnt > K) return;
	

	// 검사
	if (idx == D) {
		if (test()) {
			if (ans > cnt)
				ans = cnt;
		}
		return;
	}
	
	dfs(ans, idx+1, cnt);

	for (int a : {1, 0}) {
		for (int w = 0; w < W; w++) map[idx][w] = a;

		dfs(ans, idx + 1, cnt + 1);
	}
	map[idx] = copy_map[idx];
}

void solve() {
	//freopen("test.txt", "r", stdin);
	int T;
	cin >> T;
	for (int tc = 1; tc <= T; tc++)
	{
		int answer = 21e8;
		cin >> D >> W >> K;
		for (int d = 0; d < D; d++) {
			for (int w = 0; w < W; w++) {
				cin >> map[d][w];
				copy_map[d][w] = map[d][w];
			}
		}
		
		answer = K;
		dfs(answer, 0, 0);

		cout << "#" << tc << " " << answer << "\n";
	}
}

int main() {
	ios::sync_with_stdio(0);
	cin.tie(0);

	solve();
}