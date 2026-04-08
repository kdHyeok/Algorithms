#define _CRT_SECURE_NO_WARNINGS
#include <iostream>
#include <vector>

using namespace std;

int parent[100'001];
bool visited[100'001];
vector<int> adj[100001];
vector<pair<int, int>> queries[100'001];
int answers[100'001];

// 표준 Path Compression
int find(int tar) {
	if (tar == parent[tar]) return tar;
	return parent[tar] = find(parent[tar]);
}

void LCA(int curr) {
	visited[curr] = true;

	for (int next : adj[curr]) {
		if (!visited[next]) {
			LCA(next);

			// set union
			parent[next] = curr;
		}
	}

	for (auto& query : queries[curr]) {
		int tar = query.first;
		int query_idx = query.second;

		if (visited[tar]) {
			answers[query_idx] = find(tar);
		}
	}
	
}

int main() {
	ios::sync_with_stdio(false);
	cin.tie(NULL);
	//freopen("test.txt", "r", stdin);

	int N, M;
	if (!(cin >> N)) return 0;

	for (int i = 1; i <= N; i++) parent[i] = i;

	for (int i = 0; i < N - 1; i++) {
		int u, v;
		cin >> u >> v;
		adj[u].push_back(v);
		adj[v].push_back(u);
	}

	if (!(cin >> M)) return 0;
	for (int i = 0; i < M; i++) {
		int u, v;
		cin >> u >> v;
		queries[u].push_back({ v, i });
		queries[v].push_back({ u, i });
	}

	LCA(1);

	for (int i = 0; i < M; i++) {
		cout << answers[i] << "\n";
	}

	return 0;
}