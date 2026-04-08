#define _CRT_SECURE_NO_WARNINGS
#include <iostream>
#include <vector>

using namespace std;

const int MAX_N = 40'001;
const int MAX_M = 10'001;

int parent[MAX_N];
bool visited[MAX_N];
vector<pair<int, int>> adj[MAX_N];
int dist_from_root[MAX_N]; //루트 노드에서부터 각 노드까지의 실제 간선 가중치 누적 합을 저장
vector<pair<int, int>> queries[MAX_N];
int answers[MAX_M];


int find(int tar) {
	if (tar == parent[tar]) return tar;
	return parent[tar] = find(parent[tar]);
}

void LCA(int curr, int cost) {
	visited[curr] = true;
	dist_from_root[curr] = cost; // 루트로부터의 누적 거리 저장

	for (auto& edge : adj[curr]) {
		int next = edge.first;
		int weight = edge.second;

		if (!visited[next]) {
			LCA(next, cost + weight);
			// set union
			parent[next] = curr;
		}
		
	}

	for (auto& query : queries[curr]) {
		int tar = query.first;
		int query_idx = query.second;

		if (visited[tar]) {
			int lca_node = find(tar);
			// 공통 조상 lca_node를 기준으로 curr , tar는 연결되어있음.
			// (1~curr의 거리 - 1~lca_node) = curr~lca_node의 길이
			// (1~tar의 거리 - 1~lca_node) = tar~lca_node의 길이
			// curr~lca_node + lca_node~tar == curr~tar
			answers[query_idx] = (
				dist_from_root[curr] 
				+ dist_from_root[tar] 
				- 2 * dist_from_root[lca_node]
			);
		}
	}
	
}

int main() {
	ios::sync_with_stdio(false);
	cin.tie(NULL);
	//freopen("test.txt", "r", stdin);
	int u, v, w;
	int N, M;
	if (!(cin >> N)) return 0;

	for (int i = 1; i <= N; i++) parent[i] = i;

	for (int i = 0; i < N - 1; i++) {
		cin >> u >> v >> w;
		adj[u].push_back({ v, w });
		adj[v].push_back({ u, w });
	}

	if (!(cin >> M)) return 0;
	for (int i = 0; i < M; i++) {
		cin >> u >> v;
		queries[u].push_back({ v, i });
		queries[v].push_back({ u, i });
	}

	LCA(1,0);

	for (int i = 0; i < M; i++) {
		cout << answers[i] << "\n";
	}

	return 0;
}