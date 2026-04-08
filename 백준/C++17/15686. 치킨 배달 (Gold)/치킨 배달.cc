#define _CRT_SECURE_NO_WARNINGS
#include <iostream>
#include <cstring>
#include <vector>
#include <queue>
#include <algorithm>
#include <cmath>

using namespace std;

const int MAX_N = 51;
const int MAX_M = 14;

struct pos{
	int y, x;
};

int map[MAX_N][MAX_N];
int N, M;
int answer = 999999;

vector<pos> hub_list;
vector<pos> cluster_list;

int dist_func(pos st, pos ed) {
	return abs(st.y - ed.y) + abs(st.x - ed.x);
}

int calculate_dist(const vector<pos>& selected) {
	int dist_sum = 0; 

	for (auto& c : cluster_list) {
		int min_dist = 999999;
		for (auto& s : selected) {
			int d = dist_func(c, s);
			min_dist = min(min_dist, d);
		}
		dist_sum += min_dist;
	}
	return dist_sum;
}

void list_dfs(vector<pos>& selected, int idx, int cnt) {
	if (cnt == M) {
		if (selected.empty())
			return;
		int dist = calculate_dist(selected);
		answer = min(answer, dist);
		return;
	}
	if (idx == hub_list.size()) {
		return;
	}

	selected.push_back(hub_list[idx]);
	list_dfs(selected, idx + 1, cnt + 1);

	selected.pop_back(); 
	list_dfs(selected, idx + 1, cnt);
}

void solve() {
	cin >> N >> M;
	answer = 999999; 

	for (int y = 1; y <= N; y++) {
		for (int x = 1; x <= N; x++) {
			cin >> map[y][x];
			if (map[y][x] == 1) {
				cluster_list.push_back({ y, x });
			}
			if (map[y][x] == 2) {
				hub_list.push_back({ y, x });
			}
		}
	}
	vector<pos> selected;
	list_dfs(selected, 0, 0); 

	cout << answer << "\n";
}

int main() {
	ios::sync_with_stdio(0);
	cin.tie(0);
	//freopen("test.txt", "r", stdin);

	solve();

	return 0;
}