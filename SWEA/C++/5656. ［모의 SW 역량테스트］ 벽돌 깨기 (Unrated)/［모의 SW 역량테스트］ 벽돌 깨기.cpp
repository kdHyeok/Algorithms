#define _CRT_SECURE_NO_WARNINGS
#include <iostream>
#include <queue>
#include <algorithm>
#include <cstring>

using namespace std;

int N, W, H;
int min_remain;
int map[15][12];

struct Point {
	int r, c, p;
};

// 맵에 남은 벽돌의 개수를 세는 함수
int get_remain(int current_map[15][12]) {
	int count = 0;
	for (int i = 0; i < H; i++) {
		for (int j = 0; j < W; j++) {
			if (current_map[i][j] > 0) count++;
		}
	}
	return count;
}

// 벽돌을 아래로 내리는 함수
void apply_gravity(int current_map[15][12]) {
	for (int c = 0; c < W; c++) {
		int cursor = H - 1;
		for (int r = H - 1; r >= 0; r--) {
			if (current_map[r][c] > 0) {
				int temp = current_map[r][c];
				current_map[r][c] = 0;
				current_map[cursor--][c] = temp;
			}
		}
	}
}

// 벽돌 부수기 (플러드필?)
void explosion(int start_r, int start_c, int current_map[15][12]) {
	queue<Point> q;
	q.push({ start_r, start_c, current_map[start_r][start_c] });
	current_map[start_r][start_c] = 0;

	int dr[] = { -1, 1, 0, 0 };
	int dc[] = { 0, 0, -1, 1 };

	while (!q.empty()) {
		Point curr = q.front();
		q.pop();

		for (int i = 1; i < curr.p; i++) {
			for (int d = 0; d < 4; d++) {
				int nr = curr.r + dr[d] * i;
				int nc = curr.c + dc[d] * i;

				// 범위를 벗어나거나 없으면 넘어가기
				if (nr < 0 || nr >= H || nc < 0 || nc >= W) continue;
				if (current_map[nr][nc] == 0) continue;

				// 1이상이면 주변 폭발, q에 넣기
				if (current_map[nr][nc] > 1) {
					q.push({ nr, nc, current_map[nr][nc] });
				}
				current_map[nr][nc] = 0;
			}
		}
	}
}

void dfs(int count, int current_map[15][12]) {
	// 현재 남은 벽돌 개수
	int remain = get_remain(current_map);

	// 공을 다 던졌거나 벽돌이 더 이상 없으면 종료
	if (count == N || remain == 0) {
		min_remain = min(min_remain, remain);
		return;
	}

	int backup[15][12];

	for (int c = 0; c < W; c++) {
		int r = 0;
		while (r < H && current_map[r][c] == 0) r++;

		// 해당 열에 벽돌이 없으면 다음 열로
		if (r == H) continue;

		// 맵 상태 복사 후 시뮬레이션
		memcpy(backup, current_map, sizeof(backup));

		explosion(r, c, backup);
		apply_gravity(backup);

		dfs(count + 1, backup);

		// 정답이 0이면 더 이상 탐색 불필요 (가지치기)
		if (min_remain == 0) return;
	}
}

int main() {
	ios::sync_with_stdio(false);
	cin.tie(NULL);
	//freopen("sample_input.txt", "r", stdin);

	int T;
	cin >> T;
	for (int tc = 1; tc <= T; tc++) {
		cin >> N >> W >> H;
		for (int i = 0; i < H; i++) {
			for (int j = 0; j < W; j++) {
				cin >> map[i][j];
			}
		}

		min_remain = 1e9;
		dfs(0, map);

		cout << "#" << tc << " " << min_remain << "\n";
	}
	return 0;
}
	
