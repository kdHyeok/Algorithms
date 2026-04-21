#define _CRT_SECURE_NO_WARNINGS
#include <iostream>
#include <algorithm>
#include <cstring>
#include <queue>

using namespace std;


int N, M, K;
pair<int,int> mx[105][105];
int map[105][105];
int visi[105][105] = {0};
int dy[] = {0, -1,1,0,0 };
int dx[] = {0, 0,0,-1,1 };

struct node {
	int y, x, k, d;
};

int main() {
	ios::sync_with_stdio(false);
	cin.tie(NULL);
	//freopen("sample_input.txt", "r", stdin);

	int T;
	cin >> T;
	for (int tc = 1; tc <= T; tc++) {
		int ans = 0;
		queue<node> q;
		queue<pair<int,int>> rq;
		memset(visi, 0, sizeof(visi));
		
		cin >> N >> M >> K;

		int iy, ix, ik, id;
		for (int i = 0; i < K; i++)
		{
			cin >> iy >> ix >> ik>> id;
			q.push({ iy, ix, ik, id });
		}

		for (int i = 1; i <= M; i++)
		{
			memset(mx, 0, sizeof(mx));
			memset(map, 0, sizeof(map));

			while (!q.empty()) {
				node c = q.front();
				q.pop();
				int cy = c.y + dy[c.d];
				int cx = c.x + dx[c.d];
				int ck = c.k;
				int cd = c.d;
				if (cy == 0 || cx == 0 || cy == N - 1 || cx == N - 1) {
					ck /= 2;
					cd = (cd&1) ? cd + 1 : cd - 1;
				}
				if (!ck) continue;

				map[cy][cx] += ck;

				if (mx[cy][cx].first < ck) {
					mx[cy][cx].first = ck;
					mx[cy][cx].second = cd;
				}

				if (visi[cy][cx] == i) continue;

				rq.push({ cy,cx });
				visi[cy][cx] = i;
			}

			while (!rq.empty()) {
				int cy = rq.front().first;
				int cx = rq.front().second;
				int ck = map[cy][cx];
				int cd = mx[cy][cx].second;
				q.push({ cy,cx,ck,cd });
				rq.pop();
			}
		}

		while (!q.empty()) {
			ans += q.front().k;
			q.pop();
		}

		cout << "#" << tc << " " << ans << "\n";
	}
	return 0;
}
	
