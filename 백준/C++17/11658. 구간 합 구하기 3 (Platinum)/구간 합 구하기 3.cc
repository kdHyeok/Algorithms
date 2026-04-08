#define _CRT_SECURE_NO_WARNINGS
#include<iostream>
using namespace std;

const int MX_N = 1'025;
const int MX_M = 100'001;

int map_data[MX_N][MX_N];
int n, m;

int tree[4 * MX_N][4 * MX_N];
// X축(가로) 구간을 초기화하는 함수
void init_x(int node_y, int start_y, int end_y, int node_x, int start_x, int end_x) {
	if (start_x >= end_x) {
		if (start_y >= end_y) {
			tree[node_y][node_x] = map_data[start_y][start_x];
		}
		else {
			tree[node_y][node_x] = tree[node_y << 1][node_x] + tree[node_y << 1 | 1][node_x];
		}
		return;
	}

	int mid_x = start_x + ((end_x - start_x) >> 1);

	init_x(node_y, start_y, end_y, node_x << 1, start_x, mid_x);
	init_x(node_y, start_y, end_y, node_x << 1 | 1, mid_x + 1, end_x);

	tree[node_y][node_x] = tree[node_y][node_x << 1] + tree[node_y][node_x << 1 | 1];
}

// Y축(세로) 구간을 초기화하는 함수
void init_y(int node_y, int start_y, int end_y) {
	if (start_y < end_y) {
		int mid_y = start_y + ((end_y - start_y) >> 1);
		init_y(node_y << 1, start_y, mid_y);       // 위쪽 절반
		init_y(node_y << 1 | 1, mid_y + 1, end_y); // 아래쪽 절반
	}
	init_x(node_y, start_y, end_y, 1, 1, n);
}

int query_x(int y_id, int x_id, int left, int right, int start_x, int end_x) {
	if (right < start_x || end_x < left) return 0;
	if (start_x <= left && right <= end_x) return tree[y_id][x_id];
	int mid = left + ((right - left) >> 1);
	int xl = query_x(y_id, x_id << 1, left, mid, start_x, end_x);
	int xr = query_x(y_id, x_id << 1 | 1, mid + 1, right, start_x, end_x);

	return xl + xr;
}

int query(int idx, int top, int bot, int start_y, int start_x, int end_y, int end_x) {
	if (bot < start_y || end_y < top) return 0;
	if (start_y <= top && bot <= end_y) return query_x(idx, 1, 1, n, start_x, end_x);
	int mid = top + ((bot - top) >> 1);
	int yt = query(idx << 1, top, mid, start_y, start_x, end_y, end_x);
	int yb = query(idx << 1 | 1, mid+1, bot, start_y, start_x, end_y, end_x);

	return yt + yb;
}

void update_x(int y_id, int x_id, int left, int right, int x, int val, bool flag) {
	if (left > x || x > right) return;
	if (left < right) {
		int mid = left + ((right - left) >> 1);
		update_x(y_id, x_id << 1, left, mid, x, val, flag);
		update_x(y_id, x_id << 1 | 1, mid + 1, right, x, val, flag);
		tree[y_id][x_id] = tree[y_id][x_id << 1] + tree[y_id][x_id << 1 | 1];
		return;
	}

	if (flag) tree[y_id][x_id] = val;
	else tree[y_id][x_id] = tree[y_id << 1][x_id] + tree[y_id << 1 | 1][x_id];
}

void update(int idx, int top, int bot, int y, int x, int val) {
	if (top > y || y > bot) return;
	if (top < bot) {
		int mid = top + ((bot - top) >> 1);
		update(idx << 1, top, mid, y, x, val);
		update(idx << 1 | 1, mid + 1, bot, y, x, val);
	}
	update_x(idx, 1, 1, n, x, val, (top==bot));
}


int main() {
	ios::sync_with_stdio(0);
	cin.tie(0);
	//freopen("test.txt", "r", stdin);


	cin >> n >> m;
	for (int y = 1; y <= n; ++y)
	{
		for (int x = 1; x <= n; ++x)
		{
			cin >> map_data[y][x];
		}
	}
	init_y(1, 1, n);
	int w, x1, y1, x2, y2, c;
	while (m--)
	{
		cin >> w;
		if (!w) {
			cin >> x1 >> y1 >> c;
			update(1, 1, n, x1, y1, c);
		}
		else {
			cin >> x1 >> y1 >> x2 >> y2;
			cout << query(1, 1, n, x1, y1, x2, y2) << '\n';
		}
	}
	return 0;
}